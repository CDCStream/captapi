"""Pillar page mapper: clicks, products, socials, displayName/id."""

from __future__ import annotations

from app.routers import creator_pages as cp


def test_pillar_username_path_and_bare():
    assert cp._pillar_username("https://pillar.io/angelstrife") == "angelstrife"
    assert cp._pillar_username("@angelstrife") == "angelstrife"


def test_pillar_cloudinary_url():
    assert (
        cp._pillar_cloudinary_url("cloudinary:user-image/page/abc")
        == "https://res.cloudinary.com/pillario/image/upload/user-image/page/abc"
    )
    assert cp._pillar_cloudinary_url("https://cdn.example/a.jpg") == "https://cdn.example/a.jpg"


def test_map_links_clicks_skip_deleted_and_referral():
    links = cp._pillar_map_links(
        [
            {
                "link_id": "66472110-1ba7-11ee-b33b-e5396daf72e9",
                "order": None,
                "clicks": 2,
                "status": "ACTIVE",
                "data": {
                    "url": "https://twitter.com/SoyAngelStrife",
                    "tagline": "Twitter",
                    "visible": True,
                },
            },
            {
                "link_id": "deleted",
                "order": 1,
                "clicks": 9,
                "status": "DELETED",
                "data": {"url": "https://example.com/x", "tagline": "Gone"},
            },
            {
                "link_id": "referral",
                "order": 2,
                "clicks": 1,
                "status": "ACTIVE",
                "data": {
                    "url": "https://pillar.io/referral/someone",
                    "tagline": "Make a Pillar",
                },
            },
            {
                "link_id": "album",
                "order": 2,
                "clicks": 0,
                "status": "ACTIVE",
                "data": {
                    "url": "https://open.spotify.com/album/14jq",
                    "tagline": "30 Mil Pies",
                    "visible": True,
                },
            },
        ]
    )
    assert len(links) == 2
    album = next(l for l in links if l["order"] == 2)
    tw = next(l for l in links if l["clicks"] == 2)
    assert album["type"] == "spotify"
    assert tw["type"] == "twitter"
    assert tw["id"] == "66472110-1ba7-11ee-b33b-e5396daf72e9"


def test_map_products_and_socials():
    products = cp._pillar_map_products(
        [
            {
                "product_id": "254c8681-1d52-11ee-b065-850167411bb1",
                "name": "LP Deluxe",
                "description": "Vinyl",
                "price": 0,
                "url": "https://shop.example/lp",
                "image": "https://cdn.example/lp.jpg",
                "status": "ACTIVE",
                "show_price": False,
            }
        ]
    )
    assert products[0]["id"] == "254c8681-1d52-11ee-b065-850167411bb1"
    assert products[0]["title"] == "LP Deluxe"
    assert products[0]["name"] == "LP Deluxe"
    assert products[0]["price"] == 0
    assert products[0]["showPrice"] is False

    socials, other = cp._pillar_socials(
        {
            "socials": {
                "EMAIL": {"value": "a@b.com", "visible": True},
                "TIKTOK": {"value": "https://tiktok.com/@x", "visible": True},
                "PATREON": {"value": "", "visible": True},
                "AMAZON": {"value": "https://amazon.com/shop/x", "visible": True},
            }
        },
        [{"channel": "YOUTUBE", "url": "https://youtube.com/@x"}],
    )
    assert "email" not in socials
    assert socials["tiktok"].endswith("@x")
    assert socials["amazon"].startswith("https://amazon.com/")
    assert socials["youtube"].startswith("https://youtube.com/")
    assert "patreon" not in socials
    assert isinstance(other, list)


def test_map_page_identity():
    page = cp._pillar_map_page(
        {
            "data": {
                "influencer": {
                    "id": "d8a5cbb4-a64d-44f2-830d-27a489bbc608",
                    "alias": "angelrafaelcovablanco",
                    "contact_email": "contact@example.com",
                    "socials": [],
                    "user": {
                        "first_name": "Angel",
                        "last_name": "Blanco",
                        "full_name": "Angel Blanco",
                        "email": "angel@example.com",
                        "bio": "Creator bio",
                        "profile_image": "cloudinary:user-image/page/uid",
                    },
                },
                "banner": {
                    "url_key": "angelstrife",
                    "customizations": {
                        "user_alias": "Angel Strife",
                        "location": "Mexico",
                        "socials": {
                            "EMAIL": {"value": "angel@example.com", "visible": True},
                            "TWITTER": {
                                "value": "https://twitter.com/SoyAngelStrife",
                                "visible": True,
                            },
                        },
                    },
                },
                "links": [
                    {
                        "link_id": "1",
                        "order": None,
                        "clicks": 2,
                        "status": "ACTIVE",
                        "data": {
                            "url": "https://twitter.com/SoyAngelStrife",
                            "tagline": "Twitter",
                            "visible": True,
                        },
                    }
                ],
                "products": [],
            }
        },
        page_key="angelstrife",
    )
    assert page is not None
    assert page["id"] == "d8a5cbb4-a64d-44f2-830d-27a489bbc608"
    assert page["username"] == "angelstrife"
    assert page["displayName"] == "Angel Strife"
    assert page["name"] == page["displayName"]
    assert page["firstName"] == "Angel"
    assert page["lastName"] == "Blanco"
    assert page["location"] == "Mexico"
    assert page["email"] == "angel@example.com"
    assert page["bio"] == "Creator bio"
    assert page["avatar"].endswith("/user-image/page/uid")
    assert page["links"][0]["clicks"] == 2


def test_pillar_credits_is_one():
    assert cp.CREDIT_PAGE["pillar"] == 1
