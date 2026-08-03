"""Tests for Cloudflare-blocked creator-page fetches (lnk.bio)."""

from __future__ import annotations

from app.services.browser_fetch import _is_cloudflare_block
from app.routers.creator_pages import _anchor_links, _is_platform_noise_link, _meta, _LINKBIO_TITLE_SUFFIX


def test_cloudflare_challenge_detected() -> None:
    html = "<html><title>Attention Required! | Cloudflare</title><div>cf-ray</div></html>"
    assert _is_cloudflare_block(403, html) is True
    assert _is_cloudflare_block(200, "<html><title>@user Lnk.Bio</title></html>") is False


def test_lnk_bio_anchor_parse_keeps_creator_links() -> None:
    html = """
    <html><head>
      <meta property="og:title" content="@charlidamelio Lnk.Bio · link in bio" />
      <meta property="og:image" content="https://cdn.example/avatar.jpg" />
    </head><body>
      <a href="https://lnk.bio/">Home</a>
      <a href="https://lnk.bio/charlidamelio">Self</a>
      <a href="https://lnk.bio/share/x">Share</a>
      <a href="https://tiktok.com/@charlidamelio">TikTok</a>
      <a href="https://www.charlidamelio.com">official website</a>
    </body></html>
    """
    page_url = "https://lnk.bio/charlidamelio"
    title = _meta(html, "og:title")
    assert title and "charlidamelio" in title.lower()
    name = _LINKBIO_TITLE_SUFFIX.sub("", title).strip()
    assert name.startswith("@charlidamelio")
    links = [
        l
        for l in _anchor_links(html, page_url=page_url)
        if not _is_platform_noise_link(l.get("url") or "", page_url)
    ]
    urls = {l["url"] for l in links}
    assert "https://tiktok.com/@charlidamelio" in urls
    assert "https://www.charlidamelio.com" in urls
    assert "https://lnk.bio/" not in urls
