"""LinkedIn company industry fallbacks when JSON-LD omits the field."""

from app.services.linkedin_native import _industry_from_html


MOO_SNIPPET = """
<h1 class="top-card-layout__title">MOO NORWAY</h1>
<h2 class="top-card-layout__headline break-words font-sans text-md">
    Design Services
</h2>
<div data-test-id="about-us__industry">
  <dt>Industry</dt>
  <dd class="font-sans">
              Design Services
  </dd>
</div>
"""


def test_industry_from_about_us_section():
    assert _industry_from_html(MOO_SNIPPET) == "Design Services"


def test_industry_from_headline_when_about_missing():
    html = """
    <h2 class="top-card-layout__headline break-words">Retail</h2>
    """
    assert _industry_from_html(html) == "Retail"


def test_industry_missing_returns_none():
    assert _industry_from_html("<html><body>no industry here</body></html>") is None
