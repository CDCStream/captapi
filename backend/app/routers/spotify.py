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
# Artist / track / podcast details: Pathfinder GraphQL, priced at 1 credit (SC parity).
CREDIT_ARTIST = 1
CREDIT_TRACK = 1
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
    never special-case missing keys. ``raw`` remains for advanced use.
    """
    stats = item.get("stats") if isinstance(item.get("stats"), dict) else {}
    profile = item.get("profile") if isinstance(item.get("profile"), dict) else {}
    discography = item.get("discography") if isinstance(item.get("discography"), dict) else {}
    goods = item.get("goods") if isinstance(item.get("goods"), dict) else {}
    related = item.get("relatedContent") if isinstance(item.get("relatedContent"), dict) else {}
    albums_block = discography.get("albums") if isinstance(discography.get("albums"), dict) else {}
    singles_block = discography.get("singles") if isinstance(discography.get("singles"), dict) else {}
    return {
        "worldRank": safe_int(stats.get("worldRank")),
        "topCities": _artist_top_cities(stats),
        "externalLinks": _artist_external_links(profile),
        "verified": _artist_verified(item),
        "topTracks": _artist_top_tracks(discography),
        "concerts": _artist_concerts(goods),
        "relatedArtists": _artist_related(related),
        "albums": _artist_releases(albums_block, limit=20),
        "singles": _artist_releases(singles_block, limit=20),
        "albumsCount": safe_int(albums_block.get("totalCount")),
        "singlesCount": safe_int(singles_block.get("totalCount")),
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


def _track_fields(item: dict[str, Any], album: dict[str, Any]) -> dict[str, Any]:
    """Lift getTrack fields: playCount, ids, rating, albumInfo. Omits bulky raw."""
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
    artist_items = _track_artist_items(item)
    album_info = None
    if album_id or (isinstance(album, dict) and album.get("name")):
        album_info = {
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
        "popularity": safe_int(item.get("popularity")),
        "trackNumber": safe_int(item.get("trackNumber") or item.get("track_number")),
        "discNumber": safe_int(item.get("discNumber") or item.get("disc_number")),
        "contentRating": label,
        "explicit": explicit,
        "mediaType": safe_str(item.get("mediaType")),
        "playable": playable,
        "previewUrl": _track_preview_url(item),
        "releaseDate": release_date,
        "artistItems": artist_items,
        "albumInfo": album_info,
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
    if sid and not out.get("url"):
        out["url"] = f"https://open.spotify.com/{uri_kind}/{sid}"
    if kind == "artist":
        out.update(_artist_fields(item))
    if kind == "track":
        # getTrack payload embeds full artist discographies — do not leak as raw.
        out.pop("raw", None)
        track_extra = _track_fields(item, album if isinstance(album, dict) else {})
        out.update(track_extra)
        # Prefer structured artist names when string list was empty.
        if not out.get("artists") and track_extra.get("artistItems"):
            out["artists"] = [
                a["name"] for a in track_extra["artistItems"] if isinstance(a, dict) and a.get("name")
            ]
        if not out.get("album") and isinstance(track_extra.get("albumInfo"), dict):
            out["album"] = track_extra["albumInfo"].get("name")
        tid = track_extra.get("id") or sid
        if tid:
            # Always ship full spotify:track:… URI (search Apify used bare ids).
            out["id"] = tid
            out["uri"] = f"spotify:track:{tid}"
            out["url"] = f"https://open.spotify.com/track/{tid}"
        if not out.get("releaseYear") and track_extra.get("releaseDate"):
            out["releaseYear"] = _year_of(track_extra["releaseDate"])
    if kind == "podcast":
        # Pathfinder show payload includes visualIdentity color dumps + episode stubs — drop raw.
        out.pop("raw", None)
        podcast_extra = _podcast_fields(item)
        out.update(podcast_extra)
        if podcast_extra.get("id"):
            out["url"] = f"https://open.spotify.com/show/{podcast_extra['id']}"
            out["uri"] = f"spotify:show:{podcast_extra['id']}"
    elif kind in ("album", "artist", "episode") and sid:
        out.setdefault("id", sid)
        out["uri"] = f"spotify:{uri_kind}:{sid}"
        if not out.get("url") or "open.spotify.com" not in str(out.get("url")):
            out["url"] = f"https://open.spotify.com/{uri_kind}/{sid}"
    # Episodes/albums/artists: lift Apify explicit/playable when Pathfinder fields absent.
    if kind in ("album", "artist", "episode", "podcast") and out.get("explicit") is None:
        lifted = _as_bool(item.get("isExplicit"))
        if lifted is not None:
            out["explicit"] = lifted
    if kind in ("album", "artist", "episode", "podcast") and out.get("playable") is None:
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
            "trackNumber",
            "discNumber",
            "contentRating",
            "mediaType",
            "previewUrl",
            "releaseDate",
            "artistItems",
            "albumInfo",
            "id",
        ):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        for key in ("explicit", "playable"):
            if out.get(key) is None:
                out.pop(key, None)
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
        ):
            if out.get(key) in (None, "", []):
                out.pop(key, None)
        for key in ("explicit", "playable"):
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
        "(with playCount), concerts, relatedArtists, and albums/singles. Flat 1 credit. "
        "monthlyListeners / topCities / worldRank are not on Spotify's public Web API — "
        "they require this GraphQL path. raw keeps the upstream payload for advanced use "
        "(shape may change); prefer the normalized fields."
    ),
)
async def artist(
    url: str = Query(..., description="Spotify artist URL, URI, or ID"),
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
            {"uri": uri, "v": 8},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get(
    "/track",
    summary="Spotify track details",
    description=(
        "Track from Spotify's web-player GraphQL as clean JSON: id, playCount, "
        "trackNumber, contentRating/explicit, artistItems[{id,uri,name,url}], "
        "albumInfo[{id,uri,name,url,releaseDate}], duration, and previewUrl when "
        "Spotify exposes one. Flat artist name strings and album name kept for "
        "back-compat. Flat 1 credit. No bulky raw discography dump."
    ),
)
async def track(
    url: str = Query(..., description="Spotify track URL, URI, or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "track")
    async with billed_call(caller=caller, endpoint="/v1/spotify/track", platform="spotify", resource_url=uri, base_credits=CREDIT_TRACK) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("track", uri, ctx=ctx)

        data = await cached_or_run(
            "spotify.track",
            {"uri": uri, "v": 9},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/album", summary="Spotify album details")
async def album(
    url: str = Query(..., description="Spotify album URL, URI, or ID"),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "album")
    async with billed_call(caller=caller, endpoint="/v1/spotify/album", platform="spotify", resource_url=uri, base_credits=CREDIT_NATIVE) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("album", uri, limit=1, ctx=ctx)

        data = await cached_or_run(
            "spotify.album",
            {"uri": uri, "v": 7},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/podcast", summary="Spotify podcast/show details")
async def podcast(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    async with billed_call(caller=caller, endpoint="/v1/spotify/podcast", platform="spotify", resource_url=uri, base_credits=CREDIT_PODCAST) as ctx:
        async def _run() -> dict[str, Any]:
            return await _details("podcast", uri, limit, ctx=ctx)

        data = await cached_or_run(
            "spotify.podcast",
            {"uri": uri, "limit": limit, "v": 8},
            _run,
            ctx,
            ttl=get_settings().CACHE_TTL_STATIC,
            use_cache=cache,
        )
        return ApiResponse(data=data)


@router.get("/podcast-episodes", summary="Spotify podcast episodes")
async def podcast_episodes(
    url: str = Query(..., description="Spotify show/podcast URL, URI, or ID"),
    limit: int = Query(20, ge=1, le=50),
    cache: bool = Query(False, description="Set true to use the 24h cache. Default false — always fetch fresh data."),
    caller: ApiCaller = Depends(require_api_key),
):
    uri = _url(url, "show")
    # Flat fee: native Pathfinder first; Apify only on fallthrough.
    async with billed_call(
        caller=caller,
        endpoint="/v1/spotify/podcast-episodes",
        platform="spotify",
        resource_url=uri,
        base_credits=CREDIT_NATIVE,
    ) as ctx:
        async def _run() -> dict[str, Any]:
            native = await spotify_native.podcast_episodes_native(uri, limit)
            if native is not None:
                podcast_raw, episode_rows = native
                podcast = _normalize(podcast_raw, "podcast")
                episodes = [_normalize(i, "episode") for i in episode_rows]
                ctx["source"] = "direct"
                return {
                    "platform": "spotify",
                    "podcast": podcast,
                    "totalReturned": len(episodes),
                    "episodes": episodes,
                }

            # Apify details actor (normalize drops raw — extract episodes from actor item).
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
            normalized = [_normalize(i, "episode") for i in rows]
            ctx["source"] = "apify"
            return {
                "platform": "spotify",
                "podcast": _normalize(item, "podcast"),
                "totalReturned": len(normalized[:limit]),
                "episodes": normalized[:limit],
            }

        data = await cached_or_run(
            "spotify.podcast-episodes",
            {"uri": uri, "limit": limit, "v": 8},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["episodes"]))
        return ApiResponse(data=data)


@router.get("/search", summary="Search Spotify")
async def search(
    q: str = Query(..., min_length=2),
    type: str = Query("tracks", pattern="^(tracks|albums|artists|podcasts|episodes)$"),
    limit: int = Query(20, ge=1, le=50),
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

            def _stamp(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
                # Promote per-item Apify scrapedAt when present; else stamp fetch time.
                for row in results:
                    if not row.get("scrapedAt"):
                        row["scrapedAt"] = fetched_at
                return results

            native_items = await spotify_native.search_native(q, type, limit)
            if native_items is not None:
                results = _stamp([_normalize(i, kind) for i in native_items])
                ctx["source"] = "direct"
                return {
                    "platform": "spotify",
                    "query": q,
                    "type": type,
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
            results = _stamp([_normalize(i, kind) for i in items[:limit] if not i.get("error")])
            ctx["source"] = "apify"
            return {"platform": "spotify", "query": q, "type": type, "totalReturned": len(results), "results": results}

        data = await cached_or_run(
            "spotify.search",
            {"q": q, "type": type, "limit": limit, "v": 8},
            _run,
            ctx,
            use_cache=cache,
        )
        if ctx.get("source") != "direct":
            ctx["credits_override"] = _scaled(len(data["results"]))
        return ApiResponse(data=data)
