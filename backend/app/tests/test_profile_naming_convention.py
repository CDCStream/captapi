"""Enforce one canonical name per profile concept (no identical-value twins)."""

from __future__ import annotations

from app.routers import creator_pages as cp
from app.services.instagram_native import map_channel_details, map_profile_search_user
from app.utils.profile_core import stamp_profile_core
from app.utils.profile_duplicates import duplicate_non_boolean_keys, drop_alias_twins


def _assert_no_dup_values(data: dict, *, label: str) -> None:
    dups = duplicate_non_boolean_keys(data)
    assert not dups, f"{label}: duplicate non-boolean values {dups!r}"


def test_drop_alias_twins_prefers_canonical():
    cleaned = drop_alias_twins(
        {
            "username": "a",
            "handle": "a",
            "displayName": "A",
            "name": "A",
            "firstName": "A",
            "bio": "b",
            "description": "b",
            "avatar": "https://x/a",
            "profileImage": "https://x/a",
            "profileImageHd": "https://x/a",
            "thumbnailUrl": "https://x/a",
            "banner": "https://x/b",
            "bannerUrl": "https://x/b",
            "followers": 10,
            "subscriberCount": 10,
            "postCount": 3,
            "videoCount": 3,
            "isPrivate": False,
            "private": False,
            "createdAt": "2012-02-19",
            "joinedAt": "2012-02-19",
            "joinedDate": "Feb 19, 2012",
        }
    )
    for gone in (
        "handle", "name", "firstName", "description", "profileImage",
        "profileImageHd", "thumbnailUrl", "bannerUrl", "subscriberCount",
        "videoCount", "private", "joinedAt", "joinedDate",
    ):
        assert gone not in cleaned
    _assert_no_dup_values(cleaned, label="drop_alias_twins")


def test_instagram_channel_details_no_duplicate_values():
    user = {
        "username": "austinbbq",
        "full_name": "Austin BBQ",
        "biography": "brisket",
        "is_verified": True,
        "is_private": False,
        "is_business_account": True,
        "profile_pic_url": "https://cdn.example/s150x150.jpg",
        "profile_pic_url_hd": "https://cdn.example/s150x150.jpg",
        "id": "1",
        "fbid": "2",
        "edge_followed_by": {"count": 100},
        "edge_follow": {"count": 10},
        "edge_owner_to_timeline_media": {"count": 5},
    }
    out = map_channel_details(user)
    assert out["username"] == "austinbbq"
    assert "handle" not in out
    _assert_no_dup_values(out, label="instagram/channel-details")


def test_instagram_profile_search_no_duplicate_values():
    user = {
        "username": "austinbbq",
        "full_name": "Austin BBQ",
        "biography": "brisket",
        "is_verified": True,
        "is_private": False,
        "profile_pic_url": "https://cdn.example/a.jpg",
        "profile_pic_url_hd": "https://cdn.example/a.jpg",
        "id": "1",
        "edge_followed_by": {"count": 100},
        "edge_follow": {"count": 10},
        "edge_owner_to_timeline_media": {"count": 5},
    }
    out = map_profile_search_user(user)
    assert out["username"] == "austinbbq"
    assert "handle" not in out
    assert "profileImage" not in out
    assert "private" not in out
    _assert_no_dup_values(out, label="instagram/profile-search")


def test_youtube_channel_details_shape_no_duplicate_values():
    card = drop_alias_twins(
        stamp_profile_core(
            {
                "platform": "youtube",
                "id": "UCabc",
                "username": "nasa",
                "url": "https://www.youtube.com/channel/UCabc",
                "canonicalUrl": "https://www.youtube.com/@nasa",
                "displayName": "NASA",
                "bio": "space",
                "avatar": "https://yt/a.jpg",
                "banner": "https://yt/b.jpg",
                "followers": 1000,
                "subscriberCountIsApproximate": True,
                "postCount": 50,
                "viewCount": 9,
                "country": "US",
                "countryName": "United States",
                "createdAt": "2012-02-19",
                "verified": True,
                "links": [],
                "email": None,
                "tags": ["space"],
            },
            platform="youtube",
            emit_deprecated_aliases=False,
        )
    )
    assert "joinedDate" not in card
    assert "thumbnailUrl" not in card
    assert "subscriberCount" not in card
    assert "videoCount" not in card
    assert "handle" not in card
    _assert_no_dup_values(card, label="youtube/channel-details")


def test_linkme_profile_no_duplicate_values():
    html = (
        '<script class="$tsr">({initialData:$R[1]={featuredLinks:$R[2]={meta:$R[3]={totalRecords:1},'
        'list:$R[4]=[$R[5]={id:1,title:"Twitch",description:null,image:"",url:"https://twitch.tv/x",thumbnail:""}]}},'
        'profile:$R[6]={id:"abc",firstName:"Dana",lastName:"",username:"danucd",verifiedAccount:0,'
        'bio:"ALL MY LINKS",isAmbassador:0,profileVisitCount:"54.2k",isDefaultProfilePicture:!1,'
        'profileImage:"user-profile/1/a.png",isPrivate:0,createdAt:"2024-11-01 12:37:51",'
        'updatedAt:"2025-11-16 13:43:17",stripeStatus:$R[7]={tipsEnabled:0,stripeEnabled:!1},'
        'totalLinks:7,chatID:"LinkMe-1",infoLinks:null,webLinks:null})</script>'
    )
    out = cp._linkme_parse_page(html, "https://link.me/danucd")
    assert out is not None
    assert out["username"] == "danucd"
    assert "handle" not in out
    assert "name" not in out
    assert "description" not in out
    assert out["totalLinks"] == 7
    assert out["linkCount"] == 1
    _assert_no_dup_values(out, label="linkme/profile")


def test_pillar_page_no_duplicate_values():
    out = cp._pillar_map_page(
        {
            "influencer": {
                "id": "1",
                "alias": "miguelangeles",
                "user": {
                    "first_name": "Miguel",
                    "last_name": "Angeles",
                    "full_name": "Miguel Angeles",
                    "bio": "dj",
                    "profile_image": "https://cdn/p.jpg",
                },
                "socials": [],
            },
            "banner": {
                "url_key": "miguelangeles",
                "customizations": {"user_alias": "Miguel Angeles", "location": "LA", "socials": {}},
            },
            "links": [
                {"id": "1", "title": "Spotify", "url": "https://open.spotify.com/x", "active": True}
            ],
            "products": [],
        },
        page_key="miguelangeles",
    )
    assert out is not None
    assert out["username"] == "miguelangeles"
    assert "handle" not in out
    assert "name" not in out
    assert "description" not in out
    _assert_no_dup_values(out, label="pillar/page")


def test_linkbio_page_no_duplicate_values():
    html = """
    <html><head>
      <meta property="og:title" content="Demo Creator | Lnk.Bio">
      <meta property="og:description" content="Real bio text here">
      <meta property="og:image" content="https://cdn/l.jpg">
    </head><body>
      <a class="pb-linkbox" href="https://example.com" data-title="Home">Home</a>
    </body></html>
    """
    out = cp._linkbio_parse_page(html, "https://lnk.bio/demo")
    assert out is not None
    assert out["username"] == "demo"
    assert "handle" not in out
    assert "name" not in out
    assert "description" not in out
    assert out.get("displayName")
    assert out.get("bio") == "Real bio text here"
    _assert_no_dup_values(out, label="linkbio/page")


def test_komi_shape_no_duplicate_values():
    page = drop_alias_twins(
        {
            "platform": "komi",
            "id": "1",
            "url": "https://komi.io/kimkardashian",
            "username": "kimkardashian",
            "displayName": "Kim Kardashian",
            "firstName": "Kim",
            "lastName": "Kardashian",
            "bio": "hello",
            "avatar": "https://cdn/a.jpg",
            "linkCount": 1,
            "links": [{"title": "Visit SKIMS", "url": "https://skims.com"}],
            "socials": {},
            "other": [],
        }
    )
    assert "handle" not in page
    assert "name" not in page
    assert "description" not in page
    _assert_no_dup_values(page, label="komi/page")
