"""Komi page mapper: modules flatten, socials.website, displayName/id."""

from __future__ import annotations

from app.routers import creator_pages as cp


def test_komi_username_subdomain_and_path():
    assert cp._komi_username("https://kimkardashian.komi.io/") == "kimkardashian"
    assert cp._komi_username("https://komi.io/ksi") == "ksi"
    assert cp._komi_username("@ksi") == "ksi"


def test_flatten_visit_skims_and_product_price():
    modules = [
        {
            "id": "group-skims",
            "type": "GROUP",
            "name": "SKIMS",
            "items": [
                {
                    "id": "mod-link",
                    "type": "LINK",
                    "items": [
                        {
                            "id": "6d7086df-ede4-4f8a-85e5-0fa410e60bc2",
                            "url": "https://skims.social/shop-skims",
                            "order": 0,
                            "title": "Visit SKIMS",
                            "visible": True,
                            "moduleId": "mod-link",
                            "thumbnail": "https://example.com/skims.jpg",
                            "versionId": "ver-1",
                        }
                    ],
                },
                {
                    "id": "mod-product",
                    "type": "PRODUCT",
                    "items": [
                        {
                            "id": "f43e198b-2fd5-45f4-80d1-389906c5c840",
                            "url": "https://skims.com/products/bikini",
                            "order": 0,
                            "price": 44,
                            "title": " TRIANGLE BIKINI TOP ",
                            "visible": False,
                            "currency": "USD",
                            "moduleId": "mod-product",
                            "thumbnail": "https://example.com/bikini.png",
                            "versionId": "ver-1",
                        }
                    ],
                },
            ],
        }
    ]
    links = cp._komi_flatten_module_links(modules)
    assert len(links) == 2
    link = links[0]
    assert link["title"] == "Visit SKIMS"
    assert link["type"] == "LINK"
    assert link["id"] == "6d7086df-ede4-4f8a-85e5-0fa410e60bc2"
    assert link["thumbnail"].endswith("skims.jpg")
    assert link["order"] == 0
    assert link["visible"] is True
    product = links[1]
    assert product["type"] == "PRODUCT"
    assert product["price"] == 44
    assert product["currency"] == "USD"
    assert product["visible"] is False
    assert product["title"] == "TRIANGLE BIKINI TOP"


def test_socials_include_website_type():
    profile = {
        "socialProfileLinks": [
            {"type": "INSTAGRAM", "link": "https://www.instagram.com/ksi"},
            {"type": "WEBSITE", "link": "https://www.sidemen.com/"},
            {"type": "SPOTIFY", "link": "https://open.spotify.com/artist/x"},
        ]
    }
    socials, other = cp._komi_socials(profile, {})
    assert other == []
    assert socials["instagram"].endswith("/ksi")
    assert socials["website"] == "https://www.sidemen.com/"
    assert socials["spotify"].startswith("https://open.spotify.com/")
    # Content links must not be required for socials.
    assert "WEBSITE" not in socials


def test_komi_credits_is_one():
    assert cp.CREDIT_PAGE["komi"] == 1
