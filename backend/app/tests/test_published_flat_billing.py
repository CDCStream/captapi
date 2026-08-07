"""Published-flat price cap + path vocabulary (measurement window)."""

from __future__ import annotations

from app.core.credits import (
    PUBLISHED_FLAT,
    public_source,
    resolve_credits,
    rewrite_public_path_fields,
)


def test_public_source_hides_supplier():
    assert public_source("direct") == "native"
    assert public_source("apify") == "extended"
    assert public_source("apify-fallback") == "extended"
    assert public_source("cache") == "cache"


def test_rewrite_response_path_fields():
    data = {
        "source": "apify",
        "degradedReason": "apify-timeout",
        "timings": {"path": "apify-cache"},
    }
    rewrite_public_path_fields(data)
    assert data["source"] == "extended"
    assert data["degradedReason"] == "extended-timeout"
    assert data["timings"]["path"] == "extended-cache"


def test_event_search_cap_example():
    charged, computed = resolve_credits(
        endpoint="/v1/facebook/event-search",
        status_code=200,
        cache_hit=False,
        bill_on_cache_hit=False,
        credits_override=None,
        credits_computed=38,
        base_credits=2,
    )
    assert computed == 38
    assert charged == 2
    assert PUBLISHED_FLAT["/v1/facebook/event-search"] == 2


def test_product_details_extended_absorbed():
    charged, computed = resolve_credits(
        endpoint="/v1/tiktok-shop/product-details",
        status_code=200,
        cache_hit=False,
        bill_on_cache_hit=False,
        credits_override=None,
        credits_computed=14,
        base_credits=2,
    )
    assert computed == 14
    assert charged == 2


def test_failure_and_empty_stay_zero():
    charged, _ = resolve_credits(
        endpoint="/v1/facebook/event-search",
        status_code=504,
        cache_hit=False,
        bill_on_cache_hit=False,
        credits_override=None,
        credits_computed=38,
        base_credits=2,
    )
    assert charged == 0
    charged, computed = resolve_credits(
        endpoint="/v1/facebook/event-search",
        status_code=200,
        cache_hit=False,
        bill_on_cache_hit=False,
        credits_override=0,
        credits_computed=0,
        base_credits=2,
    )
    assert charged == 0
    assert computed == 0


def test_uncapped_endpoint_unchanged():
    charged, computed = resolve_credits(
        endpoint="/v1/instagram/comments",
        status_code=200,
        cache_hit=False,
        bill_on_cache_hit=False,
        credits_override=45,
        credits_computed=None,
        base_credits=45,
    )
    assert charged == 45
    assert computed == 45
