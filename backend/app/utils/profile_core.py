"""Canonical cross-platform profile core.

Every Captapi profile / channel-details endpoint should emit this core so a
multi-platform dashboard can join without a per-platform rename table:

  platform, id, handle, url, displayName, bio, avatar, banner,
  followers, following, postCount, verified, createdAt

Platform-specific extras (Bluesky ``verification{}``, YouTube ``subscriberCount``,
Instagram ``profileImage``, …) stay alongside. Legacy names are re-emitted as
deprecated aliases for one release — see ``DEPRECATED_PROFILE_ALIASES``.
"""

from __future__ import annotations

from typing import Any

# Canonical key → previous primary names still emitted as aliases (one release).
DEPRECATED_PROFILE_ALIASES: dict[str, tuple[str, ...]] = {
    "displayName": ("name",),
    "bio": ("description",),
    "avatar": ("profileImage", "thumbnailUrl"),
    "banner": ("bannerUrl", "bannerImage"),
    "postCount": ("posts", "videoCount", "tweetCount"),
    "followers": ("subscriberCount",),
    "handle": ("username",),
    "createdAt": ("joinedAt",),
}

CANONICAL_PROFILE_KEYS: tuple[str, ...] = (
    "platform",
    "id",
    "handle",
    "url",
    "displayName",
    "bio",
    "avatar",
    "banner",
    "followers",
    "following",
    "postCount",
    "verified",
    "createdAt",
)


def _first(*values: Any) -> Any:
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        return v
    return None


def stamp_profile_core(
    card: dict[str, Any],
    *,
    platform: str | None = None,
    emit_deprecated_aliases: bool = True,
) -> dict[str, Any]:
    """Ensure canonical profile keys exist; optionally mirror deprecated aliases.

    Reads either the canonical key or any known legacy alias, writes the
    canonical key, then (when ``emit_deprecated_aliases``) copies the value
    onto legacy keys that this card already used or that are listed for BC.
    Does not invent empty strings for missing optional fields — leaves them
    absent when no source value exists (except ``platform`` when provided).
    """
    out = dict(card)
    if platform:
        out["platform"] = platform
    elif out.get("platform") is None and card.get("platform") is not None:
        out["platform"] = card.get("platform")

    display = _first(out.get("displayName"), out.get("name"))
    bio = _first(out.get("bio"), out.get("description"))
    avatar = _first(out.get("avatar"), out.get("profileImage"), out.get("thumbnailUrl"))
    banner = _first(out.get("banner"), out.get("bannerUrl"), out.get("bannerImage"))
    handle = _first(out.get("handle"), out.get("username"))
    followers = _first(out.get("followers"), out.get("subscriberCount"))
    following = out.get("following")
    post_count = _first(
        out.get("postCount"), out.get("posts"), out.get("videoCount"), out.get("tweetCount")
    )
    created = _first(out.get("createdAt"), out.get("joinedAt"))
    ident = _first(out.get("id"), out.get("did"), out.get("channelId"))

    if ident is not None:
        out["id"] = ident
    if handle is not None:
        out["handle"] = handle
    if display is not None:
        out["displayName"] = display
    if bio is not None:
        out["bio"] = bio
    if avatar is not None:
        out["avatar"] = avatar
    if banner is not None:
        out["banner"] = banner
    if followers is not None:
        out["followers"] = followers
    if following is not None:
        out["following"] = following
    if post_count is not None:
        out["postCount"] = post_count
    if created is not None:
        out["createdAt"] = created
    # verified: keep whatever boolean/None the endpoint already set

    if emit_deprecated_aliases:
        # Prefer the stamped platform (kwarg or card) for alias policy.
        plat = out.get("platform") or card.get("platform")
        # Always mirror the common BC pairs when the canonical value exists,
        # so clients mid-migration keep working.
        if display is not None:
            out.setdefault("name", display)
        if bio is not None and ("description" in card or plat == "youtube"):
            out.setdefault("description", bio)
        if avatar is not None:
            if "profileImage" in card or plat in {
                "instagram",
                "twitter",
                "threads",
                "tiktok",
            }:
                out.setdefault("profileImage", avatar)
            if "thumbnailUrl" in card or plat == "youtube":
                out.setdefault("thumbnailUrl", avatar)
        if banner is not None:
            if "bannerUrl" in card or plat == "youtube":
                out.setdefault("bannerUrl", banner)
            if "bannerImage" in card or plat == "twitter":
                out.setdefault("bannerImage", banner)
        if post_count is not None:
            if "posts" in card or plat == "bluesky":
                out.setdefault("posts", post_count)
            if "videoCount" in card or plat == "youtube":
                out.setdefault("videoCount", post_count)
            if "tweetCount" in card or plat == "twitter":
                out.setdefault("tweetCount", post_count)
        if followers is not None and ("subscriberCount" in card or plat == "youtube"):
            out.setdefault("subscriberCount", followers)
        if handle is not None and (
            "username" in card
            or plat in {"instagram", "truth_social", "twitter", "threads", "tiktok"}
        ):
            out.setdefault("username", handle if not str(handle).startswith("@") else str(handle)[1:])
        if created is not None and ("joinedAt" in card or plat == "youtube"):
            out.setdefault("joinedAt", created)

    return out
