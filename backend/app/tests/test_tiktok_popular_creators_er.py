from __future__ import annotations

from app.services.tiktok_native import (
    ENGAGEMENT_RATE_BASIS,
    creator_engagement_rate,
    extract_bio_contact,
)


def test_creator_engagement_rate_avg_likes_per_video_over_followers() -> None:
    # Nicolas Williams sample from docs — was 6.92 under likes/followers; true ER ~12.58%.
    assert creator_engagement_rate(41_527_477, 55, 6_002_719) == 12.5784
    # Lifetime likes/followers trap (old formula) would be ~53.998 for Katseye.
    assert creator_engagement_rate(1_053_364_775, 1_307, 19_507_494) == 4.1314
    assert creator_engagement_rate(548_849_706, 1_363, 6_173_962) == 6.5222


def test_creator_engagement_rate_null_when_incomplete() -> None:
    assert creator_engagement_rate(100, 0, 50) is None
    assert creator_engagement_rate(100, 10, None) is None
    assert creator_engagement_rate(None, 10, 50) is None


def test_engagement_rate_basis_constant() -> None:
    assert ENGAGEMENT_RATE_BASIS == "avgLikesPerVideo/followers"


def test_extract_bio_contact_emails_and_links() -> None:
    contact = extract_bio_contact(
        "Cash App $chefmoe83\nPayPal.me/chatnchops\nBusiness: chefmoe83@gmail.com"
    )
    assert contact is not None
    assert contact["emails"] == ["chefmoe83@gmail.com"]
    assert "PayPal.me/chatnchops" in contact["links"]
    assert any("chefmoe83" in x for x in contact["links"])


def test_extract_bio_contact_none_without_signals() -> None:
    assert extract_bio_contact("Jugador del Athletic club") is None
