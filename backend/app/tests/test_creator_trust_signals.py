from __future__ import annotations

from app.core.cache_params import parse_cache_max_age, resolve_cache_options
from app.routers.twitter import _normalize_profile
from app.services.tiktok_native import build_contact, trust_fields_from_user_info
from app.services.twitter_native import parse_user_result


def test_cache_max_age_tokens() -> None:
    assert parse_cache_max_age("7d") == 7 * 86_400
    assert parse_cache_max_age("30days") == 30 * 86_400
    use, ttl = resolve_cache_options(False, "3d")
    assert use is True and ttl == 3 * 86_400
    use2, ttl2 = resolve_cache_options(True, None)
    assert use2 is True and ttl2 is None


def test_tiktok_trust_fields_create_time() -> None:
    trust = trust_fields_from_user_info(
        {
            "user": {
                "id": "1",
                "secUid": "MS4w",
                "createTime": 1550594547,
                "signature": "hi chef@brand.com",
                "ttSeller": True,
                "bioLink": {"link": "https://example.com", "risk": 0},
                "commerceUserInfo": {"commerceUser": True},
                "isOrganization": 0,
                "language": "en",
            },
            "stats": {"friendCount": 52},
            "statsV2": {},
        }
    )
    assert trust["createTimeUnix"] == 1550594547
    assert trust["createTime"].startswith("2019-")
    assert trust["bioLinkRisk"] == 0
    assert trust["ttSeller"] is True
    assert trust["isOrganization"] is False
    assert trust["contact"]["emails"] == ["chef@brand.com"]


def test_build_contact_tipjar_payment_handles() -> None:
    contact = build_contact(
        bio="DM me",
        tipjar={"pay_pal_handle": "chefmoe", "cash_app_handle": "$chefmoe83", "patreon_handle": ""},
        bio_urls=[{"expandedUrl": "http://GauntletAI.com", "url": "https://t.co/x", "displayUrl": "GauntletAI.com"}],
    )
    assert contact is not None
    assert contact["paymentHandles"]["paypal"] == "chefmoe"
    assert contact["paymentHandles"]["cashApp"] == "$chefmoe83"
    assert "patreon" not in contact["paymentHandles"]
    assert "http://GauntletAI.com" in contact["links"]


def test_twitter_verification_triad_not_collapsed() -> None:
    user = {
        "rest_id": "12",
        "is_blue_verified": True,
        "core": {"screen_name": "bloom", "name": "Bloom", "created_at": "Wed Dec 01 19:13:23 +0000 2010"},
        "legacy": {
            "verified": False,
            "followers_count": 1000,
            "friends_count": 10,
            "statuses_count": 50,
            "fast_followers_count": 40,
            "normal_followers_count": 960,
            "entities": {
                "description": {
                    "urls": [
                        {
                            "url": "https://t.co/m6TigM5azr",
                            "expanded_url": "http://GauntletAI.com",
                            "display_url": "GauntletAI.com",
                        }
                    ]
                }
            },
        },
        "verification_info": {
            "is_identity_verified": False,
            "reason": {
                "description": {"text": "This account is verified because it's an affiliate of @bloomtech on X."},
                "verified_since_msec": "1473330227634",
            },
        },
        "affiliates_highlighted_label": {
            "label": {
                "description": "BloomTech",
                "url": {"url": "https://x.com/bloomtech"},
                "badge": {"url": "https://example.com/badge.png"},
            }
        },
        "tipjar_settings": {"pay_pal_handle": "bloom", "venmo_handle": ""},
    }
    parsed = parse_user_result(user)
    assert parsed is not None
    assert parsed["isBlueVerified"] is True
    assert parsed["isLegacyVerified"] is False
    assert parsed["isIdentityVerified"] is False
    assert parsed["fastFollowers"] == 40
    assert parsed["normalFollowers"] == 960
    assert parsed["bioUrls"][0]["expandedUrl"] == "http://GauntletAI.com"

    out = _normalize_profile(parsed)
    assert out["isBlueVerified"] is True
    assert out["isLegacyVerified"] is False
    assert out["isIdentityVerified"] is False
    assert out["contact"]["paymentHandles"]["paypal"] == "bloom"
    assert out["createdAt"].startswith("2010-")
