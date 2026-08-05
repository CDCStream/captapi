"""Linkbio page mapper: titles, id, no fabricated name, other[]."""

from __future__ import annotations

from app.routers import creator_pages as cp


SAMPLE = """
<html><head>
<meta property="og:title" content="@charlidamelio Lnk.Bio - link in bio" />
<meta property="og:image" content="https://cdn.lnk.bio/profilepics/-1344625_x.jpg" />
<meta property="og:description" content="@charlidamelio Lnk.Bio - Profile and social media links for @charlidamelio" />
</head><body>
<a class="pb-username" href="https://lnk.bio/charlidamelio" data-type="TYPE_PROFILEPIC" data-uid="-1344625" data-id="-1344625">@charlidamelio</a>
<a rel="external nofollow ugc" href="https://www.charlidamelio.com" class="pb-linkbox" data-type="TYPE_BUTTON" data-id="btn1" data-uid="-1344625">official website of charli d&#039;amelio</a>
<a href="https://facebook.com/thecharlidamelio" data-network="SOCIAL_FB" data-url="https://facebook.com/thecharlidamelio" class="lb-icon-pub" data-id="SOCIAL_FB" data-uid="-1344625"><i class="ibio-facebook" title="Facebook"></i></a>
<a href="https://triller.co/m/@charlidamelio" data-network="SOCIAL_TRILLER" data-url="https://triller.co/m/@charlidamelio" class="lb-icon-pub" data-id="SOCIAL_TRILLER" data-uid="-1344625"><i title="Triller"></i></a>
<a href="https://instagram.com/charlidamelio" data-network="SOCIAL_IG" data-url="https://instagram.com/charlidamelio" class="lb-icon-pub" data-id="SOCIAL_IG" data-uid="-1344625"><i title="Instagram"></i></a>
<a href="https://m.facebook.com/dixiedamelio" data-network="SOCIAL_FB" data-url="https://m.facebook.com/dixiedamelio" class="lb-icon-pub" data-id="SOCIAL_FB" data-uid="-1344625"><i title="Facebook"></i></a>
<a href="https://niche.example/foo" data-network="SOCIAL_NICHEAPP" data-url="https://niche.example/foo" class="lb-icon-pub" data-id="SOCIAL_NICHEAPP" data-uid="-1344625"><i title="NicheApp"></i></a>
</body></html>
"""


def test_linkbio_parse_titles_id_no_fake_name():
    page = cp._linkbio_parse_page(SAMPLE, "https://lnk.bio/charlidamelio")
    assert page is not None
    assert page["id"] == "-1344625"
    assert page["username"] == "charlidamelio"
    assert page.get("displayName") is None
    assert page.get("name") is None
    assert page["website"] == "https://www.charlidamelio.com"
    assert page["socials"]["facebook"] == "https://facebook.com/thecharlidamelio"
    assert page["socials"]["triller"].endswith("@charlidamelio")
    assert page["socials"]["website"] == "https://www.charlidamelio.com"
    # Family dupe skipped — first SOCIAL_FB wins.
    assert "dixiedamelio" not in page["socials"]["facebook"]
    titles = {l["title"] for l in page["links"]}
    assert "Facebook" in titles
    assert "Triller" in titles
    assert "Instagram" in titles
    assert None not in titles
    assert any(o["url"] == "https://niche.example/foo" for o in page["other"])


def test_linkbio_credits_is_one():
    assert cp.CREDIT_PAGE["linkbio"] == 1


def test_partition_socials_other():
    socials, other = cp._partition_socials(
        [
            {"url": "https://instagram.com/x", "socialKey": "instagram"},
            {"url": "https://weird.example/y", "type": "SOCIAL_WEIRD", "title": "Weird"},
        ]
    )
    assert socials["instagram"].endswith("/x")
    assert other[0]["url"] == "https://weird.example/y"
    assert other[0]["type"] == "SOCIAL_WEIRD"
