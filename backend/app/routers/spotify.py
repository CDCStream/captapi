"""Spotify public catalog endpoints backed by Apify actors."""

from __future__ import annotations

import math
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import ApiCaller, require_api_key
from app.core.config import get_settings
from app.core.credits import billed_call
from app.schemas.common import ApiResponse
from app.services.apify_client import ApifyError, get_apify
from app.services.cached_runner import cached_or_run
from app.services import spotify_native
from app.utils.formatters import safe_int, safe_str
from app.utils.media_urls import utc_now_iso
from app.utils.url import detect_url_platform, platform_mismatch_detail

router = APIRouter()

RATE = 1.15
# Native Pathfinder (web-player) — flat fee; our cost ~$0.
CREDIT_NATIVE = 2
# Artist / track / album / podcast details: Pathfinder GraphQL, priced at 1 credit.
CREDIT_ARTIST = 1
CREDIT_TRACK = 1
CREDIT_ALBUM = 1
CREDIT_PODCAST = 1


def _scaled(n: int, rate: float = RATE, minimum: int = 2) -> int:
    if n <= 0:
        return 0
    return max(minimum, math.ceil(n * rate))


def _url(value: str, kind: str) -> str:
    detected = detect_url_platform(value)
    if detected and detected != "spotify":
        raise HTTPException(
            status_code=400,
            detail=platform_mismatch_detail(value, "spotify", f"https://open.spotify.com/{kind}/ID"),
        )
    value = (value or "").strip()
    if value.startswith("spotify:") or "open.spotify.com/" in value:
        return value
    return f"https://open.spotify.com/{kind}/{value}"


def _names(items: Any) -> list[str]:
    if isinstance(items, dict):
        items = items.get("items")
    if isinstance(items, str):
        return [part.strip() for part in items.split(",") if part.strip()]
    if not isinstance(items, list):
        return []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or (item.get("profile") or {}).get("name")
            if name:
                out.append(str(name))
        elif isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _image(item: dict[str, Any]) -> str | None:
    header = item.get("headerImage")
    header_sources = (header.get("data") or {}).get("sources") if isinstance(header, dict) else None
    cover = item.get("coverArt")
    cover_sources = cover.get("sources") if isinstance(cover, dict) else None
    images = (
        item.get("images")
        or item.get("visuals", {}).get("avatarImage", {}).get("sources")
        or cover_sources
        or header_sources
    )
    if isinstance(images, list) and images:
        best: dict[str, Any] | None = None
        best_h = -1
        for row in images:
            if not isinstance(row, dict) or not row.get("url"):
                continue
            h = safe_int(row.get("height")) or 0
            if best is None or h >= best_h:
                best = row
                best_h = h
        if best is not None:
            return safe_str(best.get("url"))
    return safe_str(item.get("image") or item.get("thumbnail") or item.get("thumbnailUrl"))


def _year_of(value: Any) -> int | None:
    if isinstance(value, dict):
        value = value.get("year") or value.get("isoString")
    match = re.search(r"\b(\d{4})\b", str(value or ""))
    return safe_int(match.group(1)) if match else None


def _episodes_v2(item: dict[str, Any]) -> dict[str, Any]:
    """Unwrap the podcast's episodes GraphQL envelope
    (episodes.data.podcastUnionV2.episodesV2) or top-level episodesV2."""
    top = item.get("episodesV2")
    if isinstance(top, dict) and top.get("totalCount") is not None:
        return top
    block = item.get("episodes")
    if not isinstance(block, dict):
        return top if isinstance(top, dict) else {}
    union = (block.get("data") or {}).get("podcastUnionV2") if isinstance(block.get("data"), dict) else None
    v2 = (union or {}).get("episodesV2")
    if isinstance(v2, dict):
        return v2
    return block


# Fields that never apply to a given entity type — omit rather than null.
_OMIT_BY_KIND: dict[str, frozenset[str]] = {
    "artist": frozenset(
        {
            "artists",
            "album",
            "durationMs",
            "durationFormatted",
            "releaseYear",
            "totalTracks",
            "totalEpisodes",
        }
    ),
    "track": frozenset({"followers", "monthlyListeners", "totalTracks", "totalEpisodes"}),
    "album": frozenset(
        {
            "album",
            "durationMs",
            "durationFormatted",
            "followers",
            "monthlyListeners",
            "totalEpisodes",
        }
    ),
    # Podcast publisher ≠ music artists — never ship artists[] for shows.
    "podcast": frozenset(
        {
            "album",
            "artists",
            "durationMs",
            "durationFormatted",
            "followers",
            "monthlyListeners",
            "releaseYear",
            "totalTracks",
        }
    ),
    # Episode creators/play counts are almost never present in this actor payload.
    "episode": frozenset(
        {
            "album",
            "artists",
            "followers",
            "monthlyListeners",
            "totalTracks",
            "totalEpisodes",
        }
    ),
}

# Drop when empty so sparse search/details payloads don't ship noise keys.
_OMIT_IF_EMPTY = frozenset(
    {
        "description",
        "artists",
        "album",
        "durationMs",
        "followers",
        "monthlyListeners",
        "releaseYear",
        "totalTracks",
        "totalEpisodes",
        "image",
    }
)


def _strip_empty_keys(value: Any) -> Any:
    """Drop null/empty keys from actor raw payloads (search often ships null dates)."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            cleaned = _strip_empty_keys(child)
            if cleaned in (None, "", []):
                continue
            out[key] = cleaned
        return out
    if isinstance(value, list):
        return [_strip_empty_keys(child) for child in value]
    return value


def _spotify_id(uri: str | None, kind: str) -> str | None:
    u = safe_str(uri)
    if not u:
        return None
    prefix = f"spotify:{kind}:"
    if u.startswith(prefix):
        return u[len(prefix) :]
    if "open.spotify.com/" in u:
        part = u.split(f"/{kind}/", 1)[-1]
        return part.split("?", 1)[0].strip("/") or None
    return u if ":" not in u else None


def _uri_kind(kind: str) -> str:
    """Spotify URI path segment — podcast shows use ``show``."""
    return "show" if kind == "podcast" else kind


def _format_duration_ms(ms: int | None) -> str | None:
    if ms is None or ms < 0:
        return None
    total_sec = int(ms) // 1000
    minutes, seconds = divmod(total_sec, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _items(block: Any) -> list[Any]:
    if isinstance(block, list):
        return block
    if isinstance(block, dict):
        return list(block.get("items") or [])
    return []


def _artist_top_cities(stats: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(stats.get("topCities")):
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "city": safe_str(row.get("city")),
                "country": safe_str(row.get("country")),
                "region": safe_str(row.get("region")),
                "listeners": safe_int(row.get("numberOfListeners")),
            }
        )
    return out


def _artist_external_links(profile: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(profile.get("externalLinks")):
        if not isinstance(row, dict):
            continue
        name = safe_str(row.get("name"))
        url = safe_str(row.get("url"))
        if name or url:
            out.append({"name": name, "url": url})
    return out


def _artist_top_tracks(discography: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(discography.get("topTracks")):
        track = row.get("track") if isinstance(row, dict) else None
        if not isinstance(track, dict):
            continue
        album = track.get("albumOfTrack") if isinstance(track.get("albumOfTrack"), dict) else {}
        duration = track.get("duration") if isinstance(track.get("duration"), dict) else {}
        uri = safe_str(track.get("uri"))
        tid = _spotify_id(uri, "track")
        rating = track.get("contentRating") if isinstance(track.get("contentRating"), dict) else {}
        label = safe_str(rating.get("label"))
        out.append(
            {
                "name": safe_str(track.get("name")),
                "uri": uri,
                "url": f"https://open.spotify.com/track/{tid}" if tid else None,
                "playCount": safe_int(track.get("playcount")),
                "durationMs": safe_int(duration.get("totalMilliseconds")),
                "albumUri": safe_str(album.get("uri")),
                "image": _image(album),
                "explicit": False if label in (None, "NONE") else True if label else None,
            }
        )
    return out


def _artist_concerts(goods: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(goods.get("concerts")):
        data = row.get("data") if isinstance(row, dict) else row
        if not isinstance(data, dict):
            continue
        loc = data.get("location") if isinstance(data.get("location"), dict) else {}
        uri = safe_str(data.get("uri"))
        cid = _spotify_id(uri, "concert")
        festival = data.get("festival")
        out.append(
            {
                "title": safe_str(data.get("title")),
                "city": safe_str(loc.get("city")),
                "venue": safe_str(loc.get("name")),
                "startsAt": safe_str(data.get("startDateIsoString")),
                "uri": uri,
                "url": f"https://open.spotify.com/concert/{cid}" if cid else None,
                "isFestival": bool(festival) if isinstance(festival, bool) else None,
            }
        )
    return out


def _artist_related(related: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(related.get("relatedArtists")):
        if not isinstance(row, dict):
            continue
        profile = row.get("profile") if isinstance(row.get("profile"), dict) else {}
        uri = safe_str(row.get("uri"))
        aid = _spotify_id(uri, "artist")
        out.append(
            {
                "name": safe_str(profile.get("name") or row.get("name")),
                "uri": uri,
                "url": f"https://open.spotify.com/artist/{aid}" if aid else None,
                "image": _image(row),
            }
        )
    return out


def _artist_releases(block: Any, *, limit: int = 20) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _items(block)[:limit]:
        if not isinstance(row, dict):
            continue
        releases = _items((row.get("releases") or {}) if isinstance(row.get("releases"), dict) else [])
        rel = releases[0] if releases and isinstance(releases[0], dict) else row
        if not isinstance(rel, dict):
            continue
        uri = safe_str(rel.get("uri"))
        aid = _spotify_id(uri, "album")
        tracks = rel.get("tracks") if isinstance(rel.get("tracks"), dict) else {}
        out.append(
            {
                "name": safe_str(rel.get("name")),
                "uri": uri,
                "url": f"https://open.spotify.com/album/{aid}" if aid else None,
                "image": _image(rel),
                "releaseYear": _year_of(rel.get("date")),
                "totalTracks": safe_int(tracks.get("totalCount") or rel.get("trackCount")),
            }
        )
    return out


def _artist_verified(item: dict[str, Any]) -> bool | None:
    trait = item.get("onPlatformReputationTrait")
    if not isinstance(trait, dict):
        return None
    verification = trait.get("verification")
    if not isinstance(verification, dict):
        return None
    verified = verification.get("isVerified")
    return bool(verified) if isinstance(verified, bool) else None


def _artist_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Lift GraphQL-only artist intel into a stable top-level shape.

    Keys are always present (lists may be empty; scalars may be null) so clients
    never special-case missing keys. ``raw`` is opt-in on the artist route.
    """
    stats = item.get("stats") if isinstance(item.get("stats"), dict) else {}
    profile = item.get("profile") if isinstance(item.get("profile"), dict) else {}
    discography = item.get("discography") if isinstance(item.get("discography"), dict) else {}
    goods = item.get("goods") if isinstance(item.get("goods"), dict) else {}
    related = item.get("relatedContent") if isinstance(item.get("relatedContent"), dict) else {}
    albums_block = discography.get("albums") if isinstance(discography.get("albums"), dict) else {}
    singles_block = discography.get("singles") if isinstance(discography.get("singles"), dict) else {}
    # queryArtistOverview only embeds a short sample (often 2) even when
    # totalCount is dozens — surface that so callers don't think albums[] is complete.
    albums = _artist_releases(albums_block, limit=50)
    singles = _artist_releases(singles_block, limit=50)
    albums_count = safe_int(albums_block.get("totalCount"))
    singles_count = safe_int(singles_block.get("totalCount"))
    return {
        "worldRank": safe_int(stats.get("worldRank")),
        "topCities": _artist_top_cities(stats),
        "externalLinks": _artist_external_links(profile),
        "verified": _artist_verified(item),
        "topTracks": _artist_top_tracks(discography),
        "concerts": _artist_concerts(goods),
        "relatedArtists": _artist_related(related),
        "albums": albums,
        "singles": singles,
        "albumsCount": albums_count,
        "singlesCount": singles_count,
        "albumsHasMore": bool(
            albums_count is not None and albums_count > len(albums)
        ),
        "singlesHasMore": bool(
            singles_count is not None and singles_count > len(singles)
        ),
    }


def _artist_ref(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    uri = safe_str(raw.get("uri"))
    aid = safe_str(raw.get("id")) or _spotify_id(uri, "artist")
    profile = raw.get("profile") if isinstance(raw.get("profile"), dict) else {}
    name = safe_str(profile.get("name") or raw.get("name"))
    if not aid and not name:
        return None
    return {
        "id": aid,
        "uri": uri or (f"spotify:artist:{aid}" if aid else None),
        "name": name,
        "url": f"https://open.spotify.com/artist/{aid}" if aid else None,
    }


def _track_artist_items(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Structured artists with ids — from getTrack firstArtist/otherArtists or artists.items."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(ref: dict[str, Any] | None) -> None:
        if not ref:
            return
        key = ref.get("id") or ref.get("uri") or ref.get("name") or ""
        if not key or key in seen:
            return
        seen.add(str(key))
        out.append({k: v for k, v in ref.items() if v not in (None, "", [])})

    for block_name in ("firstArtist", "otherArtists"):
        block = item.get(block_name)
        if isinstance(block, dict):
            for row in block.get("items") or []:
                _add(_artist_ref(row))
        elif isinstance(block, list):
            for row in block:
                _add(_artist_ref(row))

    artists = item.get("artists")
    if isinstance(artists, dict):
        for row in artists.get("items") or []:
            _add(_artist_ref(row))
    elif isinstance(artists, list):
        for row in artists:
            _add(_artist_ref(row) if isinstance(row, dict) else None)

    return out


def _track_preview_url(item: dict[str, Any]) -> str | None:
    previews = item.get("previews") if isinstance(item.get("previews"), dict) else {}
    audio = previews.get("audioPreviews") if isinstance(previews.get("audioPreviews"), dict) else {}
    for row in audio.get("items") or []:
        if isinstance(row, dict):
            url = safe_str(row.get("url"))
            if url:
                return url
    return safe_str(item.get("previewUrl") or item.get("preview_url"))


def _slim_episode_raw(item: dict[str, Any]) -> dict[str, Any]:
    """Drop UI color dumps, play state, and per-episode show copies from raw."""
    cleaned = _strip_empty_keys(item)
    if not isinstance(cleaned, dict):
        return {}
    for key in ("visualIdentity", "playedState", "podcastV2"):
        cleaned.pop(key, None)
    # htmlDescription duplicates description — keep description only in raw.
    if cleaned.get("description") and cleaned.get("htmlDescription"):
        cleaned.pop("htmlDescription", None)
    return cleaned


def _episode_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Lift episode GraphQL fields the podcast page already treats as first-class."""
    uri = safe_str(item.get("uri"))
    eid = safe_str(item.get("id")) or _spotify_id(uri, "episode")

    preview = item.get("previewPlayback") if isinstance(item.get("previewPlayback"), dict) else {}
    audio_preview = (
        preview.get("audioPreview") if isinstance(preview.get("audioPreview"), dict) else {}
    )
    preview_url = safe_str(audio_preview.get("cdnUrl") or item.get("previewUrl"))

    audio_urls: list[str] = []
    audio = item.get("audio") if isinstance(item.get("audio"), dict) else {}
    for row in audio.get("items") or []:
        if isinstance(row, dict):
            u = safe_str(row.get("url"))
            if u and u not in audio_urls:
                audio_urls.append(u)

    media_types = [
        str(t).strip()
        for t in (item.get("mediaTypes") or [])
        if isinstance(t, str) and str(t).strip()
    ]
    has_video = "VIDEO" in {t.upper() for t in media_types} if media_types else None

    rating = item.get("contentRating") if isinstance(item.get("contentRating"), dict) else {}
    label = safe_str(rating.get("label") or item.get("contentRating"))
    explicit = True if label == "EXPLICIT" else (False if label else None)
    if explicit is None:
        explicit = _as_bool(item.get("isExplicit") or item.get("explicit"))

    release_date = _release_date_of(item.get("releaseDate")) or _release_date_of(item.get("date"))

    transcripts = item.get("transcripts") if isinstance(item.get("transcripts"), dict) else {}
    transcript_items = list(transcripts.get("items") or [])
    has_transcripts = bool(transcript_items)

    restrictions = item.get("restrictions") if isinstance(item.get("restrictions"), dict) else {}
    paywall = restrictions.get("paywallContent")
    paywall_content = bool(paywall) if isinstance(paywall, bool) else None

    show_types: list[str] = []
    for t in item.get("showTypes") or []:
        if isinstance(t, str) and t.strip():
            show_types.append(t.strip())
    if not show_types:
        podcast_v2 = item.get("podcastV2") if isinstance(item.get("podcastV2"), dict) else {}
        show = podcast_v2.get("data") if isinstance(podcast_v2.get("data"), dict) else {}
        for t in show.get("showTypes") or []:
            if isinstance(t, str) and t.strip():
                show_types.append(t.strip())

    playability = item.get("playability") if isinstance(item.get("playability"), dict) else {}
    playable = playability.get("playable") if isinstance(playability.get("playable"), bool) else None
    if playable is None:
        playable = _as_bool(item.get("isPlayable") or item.get("playable"))

    out: dict[str, Any] = {
        "id": eid,
        "previewUrl": preview_url,
        "audioUrls": audio_urls,
        "releaseDate": release_date,
        "mediaTypes": media_types,
        "hasVideo": has_video,
        "contentRating": label,
        "explicit": explicit,
        "hasTranscripts": has_transcripts,
        "paywallContent": paywall_content,
        "showTypes": show_types,
        "playable": playable,
        "htmlDescription": safe_str(item.get("htmlDescription")),
    }
    if has_transcripts:
        out["transcripts"] = transcript_items
    return {k: v for k, v in out.items() if v not in (None, "", []) or k in ("hasTranscripts", "explicit", "playable", "hasVideo", "paywallContent")}


def _podcast_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Lift show metadata: publisher, rating, topics, contentRating. Omits bulky raw."""
    uri = safe_str(item.get("uri"))
    pid = safe_str(item.get("id")) or _spotify_id(uri, "show")
    publisher_raw = item.get("publisher") if isinstance(item.get("publisher"), dict) else {}
    publisher_name = safe_str(publisher_raw.get("name"))
    publisher = {"name": publisher_name} if publisher_name else None

    rating_block = item.get("rating") if isinstance(item.get("rating"), dict) else {}
    avg_block = (
        rating_block.get("averageRating")
        if isinstance(rating_block.get("averageRating"), dict)
        else {}
    )
    average = avg_block.get("average")
    if not isinstance(average, (int, float)):
        average = None
    total_ratings = safe_int(avg_block.get("totalRatings"))
    rating = None
    if average is not None or total_ratings is not None:
        rating = {
            k: v
            for k, v in {"average": average, "totalRatings": total_ratings}.items()
            if v is not None
        }

    topics: list[dict[str, Any]] = []
    topics_block = item.get("topics")
    topic_rows = (
        topics_block.get("items")
        if isinstance(topics_block, dict)
        else topics_block
        if isinstance(topics_block, list)
        else []
    )
    for row in topic_rows or []:
        if not isinstance(row, dict):
            continue
        title = safe_str(row.get("title") or row.get("name"))
        topic_uri = safe_str(row.get("uri"))
        if not title and not topic_uri:
            continue
        topics.append(
            {k: v for k, v in {"title": title, "uri": topic_uri}.items() if v not in (None, "")}
        )

    labels: list[str] = []
    cr_v2 = item.get("contentRatingV2") if isinstance(item.get("contentRatingV2"), dict) else {}
    for label in cr_v2.get("labels") or []:
        if isinstance(label, str) and label.strip():
            labels.append(label.strip())
    if not labels:
        cr = item.get("contentRating")
        if isinstance(cr, dict):
            lab = safe_str(cr.get("label"))
            if lab:
                labels.append(lab)
        elif isinstance(cr, str) and cr.strip():
            labels.append(cr.strip())
    primary = labels[0] if labels else None
    explicit = True if "EXPLICIT" in labels else (False if labels else None)

    playability = item.get("playability") if isinstance(item.get("playability"), dict) else {}
    return {
        "id": pid,
        "publisher": publisher,
        "rating": rating,
        "topics": topics,
        "contentRating": primary,
        "contentRatingLabels": labels,
        "explicit": explicit,
        "mediaType": safe_str(item.get("mediaType")),
        "htmlDescription": safe_str(item.get("htmlDescription")),
        "playable": playability.get("playable") if isinstance(playability.get("playable"), bool) else None,
        "consumptionOrder": safe_str(item.get("consumptionOrderV2") or item.get("consumptionOrder")),
    }


def _track_isrc(item: dict[str, Any]) -> str | None:
    """ISRC when Pathfinder/Apify exposes it (often absent on getTrack)."""
    for key in ("isrc", "ISRC"):
        val = safe_str(item.get(key))
        if val:
            return val
    for nest_key in ("externalIds", "external_ids", "externalId"):
        nest = item.get(nest_key)
        if isinstance(nest, dict):
            val = safe_str(nest.get("isrc") or nest.get("ISRC"))
            if val:
                return val
        elif isinstance(nest, str) and nest.strip():
            return nest.strip()
    return None


def _release_date_of(value: Any) -> str | None:
    if isinstance(value, dict):
        return safe_str(value.get("isoString") or value.get("releaseDate") or value.get("year"))
    return safe_str(value)


def _album_track_row(entry: Any) -> dict[str, Any] | None:
    """One tracksV2 item → clean track row for album.tracks[]."""
    if not isinstance(entry, dict):
        return None
    track = entry.get("track") if isinstance(entry.get("track"), dict) else entry
    if not isinstance(track, dict):
        return None
    uri = safe_str(track.get("uri"))
    tid = _spotify_id(uri, "track") or safe_str(track.get("id"))
    duration = track.get("duration") if isinstance(track.get("duration"), dict) else {}
    duration_ms = safe_int(duration.get("totalMilliseconds") or track.get("durationMs"))
    rating = track.get("contentRating") if isinstance(track.get("contentRating"), dict) else {}
    label = safe_str(rating.get("label") or track.get("contentRating"))
    explicit = True if label == "EXPLICIT" else (False if label else None)
    if explicit is None:
        explicit = _as_bool(track.get("isExplicit") or track.get("explicit"))
    artists = _track_artist_items(track)
    row = {
        "id": tid,
        "trackNumber": safe_int(track.get("trackNumber") or track.get("track_number")),
        "discNumber": safe_int(track.get("discNumber") or track.get("disc_number")),
        "name": safe_str(track.get("name")),
        "uri": uri or (f"spotify:track:{tid}" if tid else None),
        "url": f"https://open.spotify.com/track/{tid}" if tid else None,
        "durationMs": duration_ms,
        "playCount": safe_int(track.get("playcount") or track.get("playCount")),
        "explicit": explicit,
        "artists": artists or None,
    }
    return {k: v for k, v in row.items() if v not in (None, "", [])}


def _album_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Lift getAlbum: tracks[], joinable artists, releaseDate, album-level explicit."""
    tracks_block = item.get("tracksV2") or item.get("tracks") or item.get("content") or {}
    track_rows: list[dict[str, Any]] = []
    if isinstance(tracks_block, dict):
        for entry in _items(tracks_block):
            row = _album_track_row(entry)
            if row:
                track_rows.append(row)
    total_tracks = (
        safe_int(tracks_block.get("totalCount")) if isinstance(tracks_block, dict) else None
    ) or len(track_rows)

    artists: list[dict[str, Any]] = []
    for row in _items(item.get("artists")):
        ref = _artist_ref(row)
        if ref:
            artists.append({k: v for k, v in ref.items() if v not in (None, "", [])})

    release_date = _release_date_of(item.get("date")) or _release_date_of(item.get("releaseDate"))

    flags = [t.get("explicit") for t in track_rows if isinstance(t.get("explicit"), bool)]
    if any(flags):
        explicit: bool | None = True
    elif flags and all(f is False for f in flags):
        explicit = False
    else:
        explicit = _as_bool(item.get("isExplicit") or item.get("explicit"))

    out: dict[str, Any] = {
        "artists": artists,
        "tracks": track_rows,
        "totalTracks": total_tracks,
        "tracksHasMore": bool(total_tracks and total_tracks > len(track_rows)),
        "releaseDate": release_date,
        "explicit": explicit,
    }
    return {k: v for k, v in out.items() if v not in (None, "", []) or k in ("tracks", "artists")}


def _track_fields(item: dict[str, Any], album: dict[str, Any]) -> dict[str, Any]:
    """Lift getTrack fields: playCount, structured artists/album, rating. No bulky raw."""
    uri = safe_str(item.get("uri"))
    tid = safe_str(item.get("id")) or _spotify_id(uri, "track")
    rating = item.get("contentRating") if isinstance(item.get("contentRating"), dict) else {}
    label = safe_str(rating.get("label") or item.get("contentRating"))
    playability = item.get("playability") if isinstance(item.get("playability"), dict) else {}
    album_uri = safe_str(album.get("uri")) if isinstance(album, dict) else None
    album_id = (
        safe_str(album.get("id")) if isinstance(album, dict) else None
    ) or _spotify_id(album_uri, "album")
    release_date = None
    if isinstance(album, dict):
        date = album.get("date") if isinstance(album.get("date"), dict) else {}
        release_date = safe_str(date.get("isoString") or album.get("releaseDate") or album.get("release_date"))
    artists = _track_artist_items(item)
    album_obj = None
    if album_id or (isinstance(album, dict) and album.get("name")):
        album_obj = {
            k: v
            for k, v in {
                "id": album_id,
                "uri": album_uri or (f"spotify:album:{album_id}" if album_id else None),
                "name": safe_str(album.get("name")) if isinstance(album, dict) else None,
                "url": f"https://open.spotify.com/album/{album_id}" if album_id else None,
                "releaseDate": release_date,
            }.items()
            if v not in (None, "", [])
        }
    explicit = True if label == "EXPLICIT" else (False if label else None)
    if explicit is None:
        explicit = _as_bool(item.get("isExplicit"))
        if explicit is None:
            explicit = _as_bool(item.get("explicit"))
    playable = playability.get("playable") if isinstance(playability.get("playable"), bool) else None
    if playable is None:
        playable = _as_bool(item.get("isPlayable"))
        if playable is None:
            playable = _as_bool(item.get("playable"))
    return {
        "id": tid,
        "playCount": safe_int(item.get("playcount") or item.get("playCount")),
        # Spotify Web API 0–100 popularity is not on Pathfinder getTrack.
        "popularity": safe_int(item.get("popularity")),
        "isrc": _track_isrc(item),
        "trackNumber": safe_int(item.get("trackNumber") or item.get("track_number")),
        "discNumber": safe_int(item.get("discNumber") or item.get("disc_number")),
        "contentRating": label,
        "explicit": explicit,
        "mediaType": safe_str(item.get("mediaType")),
        "playable": playable,
        "previewUrl": _track_preview_url(item),
        "releaseDate": release_date,
        # Joinable shapes (chain into /spotify/artist and /spotify/album).
        "artists": artists,
        "album": album_obj,
    }


def _normalize(item: dict[str, Any], kind: str) -> dict[str, Any]:
    stats = item.get("stats") or {}
    duration = item.get("duration") or {}
    album = item.get("albumOfTrack") or item.get("album") or {}
    tracks = item.get("tracksV2") or item.get("tracks") or item.get("content") or {}
    episodes = _episodes_v2(item) or item.get("items") or tracks

    if isinstance(duration, dict):
        duration_ms = safe_int(duration.get("totalMilliseconds"))
    else:
        duration_ms = safe_int(duration)
    duration_ms = duration_ms or safe_int(item.get("durationMs"))

    release_year = (
        _year_of(item.get("date"))
        or _year_of(item.get("releaseDate"))
        or (_year_of(album.get("date")) if isinstance(album, dict) else None)
    )

    description = safe_str(item.get("description") or item.get("subtitle"))
    biography = item.get("biography")
    if not description and isinstance(biography, dict):
        description = safe_str(biography.get("text"))
    if not description and isinstance(item.get("profile"), dict):
        bio = item["profile"].get("biography")
        if isinstance(bio, dict):
            description = safe_str(bio.get("text"))
        elif isinstance(bio, str):
            description = safe_str(bio)

    artists = _names(item.get("artists"))
    if not artists:
        artists = _names(item.get("firstArtist")) + _names(item.get("otherArtists"))
    # Do not map publisher → artists (podcast publisher ≠ hosts/artists).

    sharing = item.get("sharingInfo") if isinstance(item.get("sharingInfo"), dict) else {}
    profile = item.get("profile") if isinstance(item.get("profile"), dict) else {}
    name = safe_str(item.get("name") or item.get("title") or profile.get("name"))

    uri_kind = _uri_kind(kind)
    raw_uri = safe_str(item.get("uri") or item.get("id"))
    sid = _spotify_id(raw_uri, uri_kind) or _spotify_id(safe_str(item.get("id")), uri_kind)
    canonical_uri = f"spotify:{uri_kind}:{sid}" if sid else raw_uri

    duration_formatted = safe_str(item.get("durationFormatted")) or _format_duration_ms(duration_ms)
    scraped_at = safe_str(item.get("scrapedAt") or item.get("scraped_at"))

    out: dict[str, Any] = {
        "platform": "spotify",
        "type": kind,
        "uri": canonical_uri,
        "url": safe_str(item.get("url") or item.get("externalUrl") or item.get("shareUrl") or sharing.get("shareUrl")),
        "name": name,
        "description": description,
        "artists": artists,
        "album": safe_str(album.get("name") if isinstance(album, dict) else None) or safe_str(item.get("albumName")),
        "durationMs": duration_ms,
        "durationFormatted": duration_formatted,
        "followers": safe_int(stats.get("followers") or item.get("followers")),
        "monthlyListeners": safe_int(stats.get("monthlyListeners") or item.get("monthlyListeners")),
        "releaseYear": release_year,
        "image": _image(item)
        or safe_str(item.get("albumArt"))
        or (_image(album) if isinstance(album, dict) else None),
        "totalTracks": safe_int(tracks.get("totalCount") if isinstance(tracks, dict) else item.get("totalTracks")),
        "totalEpisodes": safe_int(episodes.get("totalCount") if isinstance(episodes, dict) else item.get("totalEpisodes")),
        "scrapedAt": scraped_at,
        "raw": _strip_empty_keys(item),
    }
    # searchTerm belongs on the search envelope (query), not every result.raw.
    raw_payload = out.get("raw")
    if isinstance(raw_payload, dict):
        raw_payload.pop("searchTerm", None)
    if sid and not out.get("url"):
        out["url"] = f"https://open.spotify.com/{uri_kind}/{sid}"
    if kind == "artist":
        out.update(_artist_fields(item))
    if kind == "track":
        track_extra = _track_fields(item, album if isinstance(album, dict) else {})
        # Structured artists[] / album{} overwrite the bare string forms from above.
        out.update(track_extra)
        tid = track_extra.get("id") or sid
        if tid:
            # Always ship full spotify:track:… URI (search Apify used bare ids).
            out["id"] = tid
            out["uri"] = f"spotify:track:{tid}"
            out["url"] = f"https://open.spotify.com/track/{tid}"
        if not out.get("releaseYear") and track_extra.get("releaseDate"):
            out["releaseYear"] = _year_of(track_extra["releaseDate"])
        # Lift Apify search flags when Pathfinder fields absent.
        if out.get("explicit") is None:
            lifted = _as_bool(item.get("isExplicit"))
            if lifted is not None:
                out["explicit"] = lifted
        if out.get("playable") is None:
            lifted_p = _as_bool(item.get("isPlayable"))
            if lifted_p is not None:
                out["playable"] = lifted_p
    if kind == "album":
        album_extra = _album_fields(item)
        out.update(album_extra)
        if album_extra.get("releaseDate") and not out.get("releaseYear"):
            out["releaseYear"] = _year_of(album_extra["releaseDate"])
    if kind == "podcast":
        # Pathfinder show payload includes visualIdentity color dumps + episode stubs — drop raw.
        out.pop("raw", None)
        podcast_extra = _podcast_fields(item)
        out.update(podcast_extra)
        if podcast_extra.get("id"):
            out["url"] = f"https://open.spotify.com/show/{podcast_extra['id']}"
            out["uri"] = f"spotify:show:{podcast_extra['id']}"
        # showTypes from metadata when present
        show_types = [
            str(t).strip()
            for t in (item.get("showTypes") or [])
            if isinstance(t, str) and str(t).strip()
        ]
        if show_types:
            out["showTypes"] = show_types
    if kind == "episode":
        episode_extra = _episode_fields(item)
        out.update(episode_extra)
        out["raw"] = _slim_episode_raw(item)
        if episode_extra.get("releaseDate") and not out.get("releaseYear"):
            out["releaseYear"] = _year_of(episode_extra["releaseDate"])
        eid = episode_extra.get("id") or sid
        if eid:
            out["id"] = eid
            out["uri"] = f"spotify:episode:{eid}"
            out["url"] = f"https://open.spotify.com/episode/{eid}"
    elif kind in ("album", "artist") and sid:
        out.setdefault("id", sid)
        out["uri"] = f"spotify:{uri_kind}:{sid}"
        if not out.get("url") or "open.spotify.com" not in str(out.get("url")):
            out["url"] = f"https://open.spotify.com/{uri_kind}/{sid}"
    # Artists/podcasts: lift Apify explicit/playable when Pathfinder fields absent.
    if kind in ("artist", "podcast") and out.get("explicit") is None:
        lifted = _as_bool(item.get("isExplicit"))
        if lifted is not None:
            out["explicit"] = lifted
    if kind in ("album", "artist", "podcast") and out.get("playable") is None:
        lifted_p = _as_bool(item.get("isPlayable"))
        if lifted_p is not None:
            out["playable"] = lifted_p
    for key in _OMIT_BY_KIND.get(kind, frozenset()):
        out.pop(key, None)
    for key in _OMIT_IF_EMPTY:
        if key in out and out[key] in (None, "", []):
            out.pop(key, None)
    if out.get("durationFormatted") in (None, ""):
        out.pop("durationFormatted", None)
    if out.get("scrapedAt") in (None, ""):
        out.pop("scrapedAt", None)
    # Track-only empties (keep falsey bools).
    if kind == "track":
        for key in (
            "playCount",
            "popularity",
            "isrc",
            "trackNumber",
            "discNumber",
            "contentRating",
            "mediaType",
            "previewUrl",
            "releaseDate",
            "artists",
            "album",
            "id",
        ):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        for key in ("explicit", "playable"):
            if out.get(key) is None:
                out.pop(key, None)
    if kind == "album":
        for key in ("releaseDate", "id"):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        if out.get("explicit") is None:
            out.pop("explicit", None)
        if out.get("tracksHasMore") is None:
            out.pop("tracksHasMore", None)
    if kind == "podcast":
        for key in (
            "id",
            "publisher",
            "rating",
            "topics",
            "contentRating",
            "contentRatingLabels",
            "mediaType",
            "htmlDescription",
            "consumptionOrder",
            "showTypes",
        ):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        for key in ("explicit", "playable"):
            if out.get(key) is None:
                out.pop(key, None)
    if kind == "episode":
        for key in (
            "id",
            "previewUrl",
            "audioUrls",
            "releaseDate",
            "mediaTypes",
            "contentRating",
            "showTypes",
            "transcripts",
            "htmlDescription",
        ):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        for key in ("explicit", "playable", "hasVideo", "hasTranscripts", "paywallContent"):
            if out.get(key) is None:
                out.pop(key, None)
    return out


async def _oembed_details(kind: str, uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
        resp = await client.get("https://open.spotify.com/oembed", params={"url": uri})
    if resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="Spotify item not found")
    item = resp.json()
    payload = dict(item)
    payload.update(
        {
            "uri": uri,
            "url": uri,
            "name": item.get("title"),
            "image": item.get("thumbnail_url"),
        }
    )
    return _normalize(payload, kind)


async def _details(kind: str, uri: str, limit: int | None = None, *, ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    # 1) Native Pathfinder (same stack as search / podcast-episodes).
    native = await spotify_native.details_native(kind, uri, episode_limit=max(1, limit or 1))
    if native is not None:
        if ctx is not None:
            ctx["source"] = "direct"
        return _normalize(native, kind)

    # 2) Apify details actor.
    album_limit = max(1, limit or 1) if kind == "album" else 1
    podcast_limit = max(1, limit or 1) if kind == "podcast" else 1
    run_input: dict[str, Any] = {
        "getDetailsType": kind,
        "spotifyUris": [uri],
        "proxyCountry": "US",
        "albums_get_offset": 0,
        "albums_get_limit": album_limit,
        "podcasts_get_offset": 0,
        "podcasts_get_limit": podcast_limit,
        "podcasts_includeRecommended": False,
        "episodes_includeRecommended": False,
    }
    try:
        items = await get_apify().run_actor_sync(
            settings.APIFY_ACTOR_SPOTIFY_DETAILS,
            run_input,
            max_items=1,
        )
    except (ApifyError, httpx.HTTPError):
        if ctx is not None:
            ctx["source"] = "oembed"
        return await _oembed_details(kind, uri)
    if not items or items[0].get("error"):
        if ctx is not None:
            ctx["source"] = "oembed"
        return await _oembed_details(kind, uri)
    if ctx is not None:
        ctx["source"] = "apify"
    return _normalize(items[0], kind)


@router.get(
    "/artist",
    summary="Spotify artist details",
    description=(
        "Artist profile from Spotify's web-player GraphQL as clean JSON: followers, "
        "monthlyListeners, worldRank, topCities, externalLinks, verified, topTracks "
        "(with playCount), concerts, relatedArtists, and albums/singles samples. Flat "
        "1 credit. monthlyListeners / topCities / worldRank are not on Spotify's public "
        "Web API. albums[]/singles[] are overview samples — albumsCount/singlesCount "
        "plus albumsHasMore/singlesHasMore tell you when the catalog is larger; chain "
        "each release URI into /spotify/album. Pass raw=true only when you need the "
        "full GraphQL payload (omitted by default)."
    ),
)
async def artist(
    url: str = Query(..., description="Spotify artist URL, URI, or ID"),
    raw: bool = Query(
        False,
        description="Include the upstream GraphQL payload as data.raw. Default false.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "artist")
    async with billed_call(
        caller=caller,
        endpoint="/v1/spotify/artist",
        platform="spotify",
        resource_url=uri,
        base_credits=CREDIT_ARTIST,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("artist", uri, ctx=ctx)

        data = await cached_or_run(
            "spotify.artist",
            {"uri": uri, "v": 9, "raw": bool(raw)},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        if not raw:
            data.pop("raw", None)
        return ApiResponse(data=data)


@router.get(
    "/track",
    summary="Spotify track details",
    description=(
        "Track from Spotify's web-player GraphQL as clean JSON: id, playCount "
        "(stream count), trackNumber, contentRating/explicit, durationMs, "
        "artists[{id,uri,name,url}], album{id,uri,name,url,releaseDate}, releaseDate, "
        "and previewUrl/isrc/popularity when Spotify exposes them on this surface. "
        "Flat 1 credit (same as artist). Pass raw=true only for the full GraphQL "
        "payload (omitted by default — getTrack embeds bulky artist discography). "
        "Note: Pathfinder getTrack often omits Web API popularity (0–100) and ISRC — "
        "playCount is the listen metric here."
    ),
)
async def track(
    url: str = Query(..., description="Spotify track URL, URI, or ID"),
    raw: bool = Query(
        False,
        description="Include the upstream GraphQL payload as data.raw. Default false.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "track")
    async with billed_call(caller=caller, endpoint="/v1/spotify/track", platform="spotify", resource_url=uri, base_credits=CREDIT_TRACK) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("track", uri, ctx=ctx)

        data = await cached_or_run(
            "spotify.track",
            {"uri": uri, "v": 11, "raw": bool(raw)},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        if not raw:
            data.pop("raw", None)
        return ApiResponse(data=data)


@router.get(
    "/album",
    summary="Spotify album details",
    description=(
        "Album from Spotify's web-player GraphQL as clean JSON: name, "
        "artists[{id,uri,name,url}], tracks[{trackNumber,discNumber,name,uri,url,"
        "durationMs,playCount,explicit,artists}], totalTracks, releaseDate, "
        "releaseYear, explicit, and cover image. Flat 1 credit (same as artist/track). "
        "Pass raw=true only when you need the full GraphQL payload (omitted by default)."
    ),
)
async def album(
    url: str = Query(..., description="Spotify album URL, URI, or ID"),
    raw: bool = Query(
        False,
        description="Include the upstream GraphQL payload as data.raw. Default false.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "album")
    async with billed_call(
        caller=caller,
        endpoint="/v1/spotify/album",
        platform="spotify",
        resource_url=uri,
        base_credits=CREDIT_ALBUM,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("album", uri, limit=300, ctx=ctx)

        data = await cached_or_run(
            "spotify.album",
            {"uri": uri, "v": 11, "raw": bool(raw)},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        if not raw:
            data.pop("raw", None)
        return ApiResponse(data=data)


@router.get(
    "/podcast",
    summary="Spotify podcast/show details",
    description=(
        "Podcast/show from Spotify's web-player GraphQL as clean JSON: id, name, "
        "description, publisher{name}, rating{average, totalRatings}, topics[], "
        "contentRating/explicit, mediaType, showTypes, totalEpisodes, and cover image. "
        "Flat 1 credit per call. Does not ship Spotify's UI color palette "
        "(visualIdentity) or a bulky raw dump. Chain into /spotify/podcast-episodes "
        "for the episode archive (cursor pagination)."
    ),
)
async def podcast(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID (not an artist URL)"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast", platform="spotify", resource_url=uri, base_credits=CREDIT_PODCAST) as ctx:
        async def _run() -> dict[str, Any]:
            # Single show — no list to limit.
            return await _details("podcast", uri, ctx=ctx)

        data = await cached_or_run(
            "spotify.podcast",
            {"uri": uri, "v": 9},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/podcast-episodes",
    summary="Spotify podcast episodes",
    description=(
        "Paginated episode archive for a Spotify show: id, name, description, "
        "releaseDate (full ISO), durationMs, previewUrl, audioUrls[], mediaTypes/"
        "hasVideo, contentRating/explicit, hasTranscripts, paywallContent, showTypes. "
        "Same show object as /spotify/podcast (totalEpisodes from this episodes query — "
        "no drift). Flat 2 credits per call on native Pathfinder. Cursor pagination via "
        "nextCursor/hasMore (offset into the archive; limit max 50). Pass raw=true only "
        "for a slimmed upstream payload — visualIdentity color dumps, playedState, and "
        "per-episode podcastV2 show copies are never shipped (same decision as /spotify/podcast)."
    ),
)
async def podcast_episodes(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID (not an artist URL)"),
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="Max episodes per page (default 20, max 50). Flat 2 credits per call on native Pathfinder.",
    ),
    cursor: str | None = Query(
        None,
        description="Pagination offset from a prior nextCursor (e.g. \"20\"). Omit for the newest page.",
    ),
    raw: bool = Query(
        False,
        description="Include slimmed per-episode upstream payload as episodes[].raw. Default false.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    offset = 0
    if cursor is not None and str(cursor).strip() != "":
        try:
            offset = max(0, int(str(cursor).strip()))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="cursor must be an integer offset") from exc
    # Flat fee: native Pathfinder first; Apify only on fallthrough.
    async with billed_call(
        caller=caller,
        endpoint="/v1/spotify/podcast-episodes",
        platform="spotify",
        resource_url=uri,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await spotify_native.podcast_episodes_native(uri, limit, offset=offset)
            if native is not None:
                podcast_raw, episode_rows, total_episodes = native
                podcast = _normalize(podcast_raw, "podcast")
                if total_episodes is not None:
                    podcast["totalEpisodes"] = total_episodes
                episodes = [_normalize(i, "episode") for i in episode_rows]
                ctx["source"] = "direct"
                next_offset = offset + len(episodes)
                if total_episodes is not None:
                    has_more = next_offset < total_episodes and len(episodes) > 0
                else:
                    has_more = len(episodes) >= limit
                return {
                    "platform": "spotify",
                    "podcast": podcast,
                    "totalEpisodes": total_episodes or podcast.get("totalEpisodes"),
                    "totalReturned": len(episodes),
                    "episodes": episodes,
                    "nextCursor": str(next_offset) if has_more else None,
                    "hasMore": has_more,
                }

            # Apify details actor — single page, no reliable deep archive cursor.
            if offset > 0:
                raise HTTPException(
                    status_code=503,
                    detail="Pagination past the first page requires the native Pathfinder path; retry shortly.",
                )
            settings = get_settings()
            try:
                actor_items = await get_apify().run_actor_sync(
                    settings.APIFY_ACTOR_SPOTIFY_DETAILS,
                    {
                        "getDetailsType": "podcast",
                        "spotifyUris": [uri],
                        "proxyCountry": "US",
                        "podcasts_get_offset": 0,
                        "podcasts_get_limit": limit,
                        "podcasts_includeRecommended": False,
                        "episodes_includeRecommended": False,
                    },
                    max_items=1,
                )
            except (ApifyError, httpx.HTTPError):
                actor_items = []
            item = actor_items[0] if actor_items and not actor_items[0].get("error") else None
            if not isinstance(item, dict):
                raise HTTPException(status_code=404, detail="Spotify podcast not found")
            episodes_block = _episodes_v2(item) or item.get("items") or item.get("content") or {}
            items = episodes_block.get("items") if isinstance(episodes_block, dict) else episodes_block
            rows: list[dict[str, Any]] = []
            for entry in items if isinstance(items, list) else []:
                if not isinstance(entry, dict):
                    continue
                # episodesV2 wraps each episode as {entity: {data: {...}}}
                entity = (entry.get("entity") or {}).get("data") if isinstance(entry.get("entity"), dict) else None
                rows.append(entity if isinstance(entity, dict) else entry)
            normalized = [_normalize(i, "episode") for i in rows[:limit]]
            podcast = _normalize(item, "podcast")
            total = safe_int(
                episodes_block.get("totalCount") if isinstance(episodes_block, dict) else None
            ) or podcast.get("totalEpisodes")
            if isinstance(total, int):
                podcast["totalEpisodes"] = total
            ctx["source"] = "apify"
            has_more = bool(isinstance(total, int) and len(normalized) < total and len(normalized) >= limit)
            return {
                "platform": "spotify",
                "podcast": podcast,
                "totalEpisodes": total,
                "totalReturned": len(normalized),
                "episodes": normalized,
                "nextCursor": str(len(normalized)) if has_more else None,
                "hasMore": has_more,
            }

        data = await cached_or_run(
            "spotify.podcast-episodes",
            {"uri": uri, "limit": limit, "offset": offset, "v": 10, "raw": bool(raw)},
            _run,
            ctx,
            use_cache=cache,
        )
        if not raw:
            for row in data.get("episodes") or []:
                if isinstance(row, dict):
                    row.pop("raw", None)
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["episodes"]))
        return ApiResponse(data=data)


@router.get(
    "/search",
    summary="Search Spotify",
    description=(
        "Search Spotify tracks, albums, artists, podcasts, or episodes. Primary path is "
        "web-player Pathfinder GraphQL (same family as /spotify/artist|track|album); "
        "Apify scraper is fallthrough only — its raw shape differs (flat albumName/"
        "isExplicit vs GraphQL __typename). Each result ships a canonical "
        "spotify:{type}:{id} URI, url, name, and explicit/playable when known. "
        "Envelope includes fetchedAt (not duplicated per row). Pathfinder search does "
        "not expose playCount — use /spotify/track or album.tracks[]. Flat 2 credits "
        "on native; Apify fallthrough scales per result. No cursor (max limit 50). "
        "Pass raw=true to include per-result upstream payloads (omitted by default)."
    ),
)
async def search(
    q: str = Query(..., min_length=2),
    type: str = Query("tracks", pattern="^(tracks|albums|artists|podcasts|episodes)$"),
    limit: int = Query(20, ge=1, le=50, description="Max results (default 20, max 50). Flat 2 credits on native Pathfinder."),
    raw: bool = Query(
        False,
        description="Include per-result upstream payload as results[].raw. Default false.",
    ),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    settings = get_settings()
    # Flat fee on native; Apify fallthrough keeps the old per-result scale.
    async with billed_call(
        caller=caller,
        endpoint="/v1/spotify/search",
        platform="spotify",
        resource_url=f"spotify:search:{q}",
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            kind = type[:-1] if type.endswith("s") else type
            fetched_at = utc_now_iso()

            def _finalize(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
                # fetchedAt on the envelope is the request timestamp — do not copy
                # it (or Apify scrapedAt) onto every row.
                for row in results:
                    row.pop("scrapedAt", None)
                return results

            native_items = await spotify_native.search_native(q, type, limit)
            if native_items is not None:
                results = _finalize([_normalize(i, kind) for i in native_items])
                ctx["source"] = "direct"
                return {
                    "platform": "spotify",
                    "query": q,
                    "type": type,
                    "fetchedAt": fetched_at,
                    "source": "pathfinder",
                    "totalReturned": len(results),
                    "results": results,
                }

            apify = get_apify()
            if type in ("tracks", "albums", "artists"):
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_SPOTIFY_SEARCH,
                    {"mode": "search", "searchTerms": [q], "searchType": type, "maxResults": limit},
                    max_items=limit,
                )
            else:
                # Podcast/episode search is only offered by the apiharvest
                # all-types actor.
                items = await apify.run_actor_sync(
                    settings.APIFY_ACTOR_SPOTIFY_SEARCH_ALL,
                    {
                        "searchType": "searchPodcasts" if type == "podcasts" else "searchFullEpisodes",
                        "keyword": [q],
                        "proxyCountry": "US",
                        "podcasts_search_limit": limit,
                        "episodes_search_limit": limit,
                    },
                    max_items=limit,
                )
            results = _finalize(
                [_normalize(i, kind) for i in items[:limit] if not i.get("error")]
            )
            ctx["source"] = "apify"
            return {
                "platform": "spotify",
                "query": q,
                "type": type,
                "fetchedAt": fetched_at,
                "source": "apify",
                "totalReturned": len(results),
                "results": results,
            }

        data = await cached_or_run(
            "spotify.search",
            {"q": q, "type": type, "limit": limit, "v": 11, "raw": bool(raw)},
            _run,
            ctx,
            use_cache=cache,
        )
        if not raw:
            for row in data.get("results") or []:
                if isinstance(row, dict):
                    row.pop("raw", None)
                    row.pop("scrapedAt", None)
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["results"]))
        return ApiResponse(data=data)
