"""Uniform object-array key sets (response-layer + Komi links)."""

from __future__ import annotations

from app.routers.creator_pages import KOMI_LINK_KEYS, _komi_flatten_module_links
from app.utils.array_normalise import normalise_object_arrays


def test_normalise_object_arrays_pads_union_keys():
    out = normalise_object_arrays(
        {
            "links": [
                {"id": "1", "title": "A", "url": "https://a"},
                {"id": "2", "title": "B", "url": "https://b", "price": 9, "currency": "USD"},
                {"id": "3", "title": "C", "url": "https://c", "thumbnail": "https://t"},
            ]
        }
    )
    shapes = {tuple(sorted(row.keys())) for row in out["links"]}
    assert len(shapes) == 1
    assert shapes.pop() == ("currency", "id", "price", "thumbnail", "title", "url")
    assert out["links"][0]["price"] is None
    assert out["links"][0]["currency"] is None
    assert out["links"][0]["thumbnail"] is None
    assert out["links"][1]["price"] == 9
    assert out["links"][2]["thumbnail"] == "https://t"


def test_normalise_skips_mixed_type_arrays():
    raw = {"mixed": [{"a": 1}, "x", {"a": 2, "b": 3}]}
    assert normalise_object_arrays(raw) == raw


def test_komi_links_uniform_keys_and_metadata_title():
    modules = [
        {
            "type": "GROUP",
            "id": "g1",
            "name": "SKKN",
            "items": [
                {
                    "type": "YOUTUBE_VIDEO",
                    "id": "m1",
                    "name": "",
                    "items": [
                        {
                            "id": "v1",
                            "url": "https://www.youtube.com/watch?v=Pxbk3q4d-nA",
                            "order": 0,
                            "visible": False,
                            "metadata": {
                                "title": "SKKN BY KIM Makeup is here!",
                                "thumbnail_url": "https://i.ytimg.com/vi/Pxbk3q4d-nA/hqdefault.jpg",
                            },
                            "moduleId": "m1",
                            "versionId": "ver1",
                        }
                    ],
                },
                {
                    "type": "PRODUCT",
                    "id": "m2",
                    "items": [
                        {
                            "id": "p1",
                            "url": "https://skknbykim.com/x",
                            "order": 0,
                            "price": 32,
                            "title": "Soft Matte Lip Color",
                            "visible": True,
                            "currency": "USD",
                            "moduleId": "m2",
                            "thumbnail": "https://cdn/t.webp",
                            "versionId": "ver1",
                        }
                    ],
                },
                {
                    "type": "LINK",
                    "id": "m3",
                    "items": [
                        {
                            "id": "l1",
                            "url": "https://skims.com",
                            "order": 0,
                            "title": "Visit SKIMS",
                            "visible": True,
                            "moduleId": "m3",
                            "versionId": "ver1",
                        }
                    ],
                },
            ],
        }
    ]
    links = _komi_flatten_module_links(modules)
    assert len(links) == 3
    shapes = {tuple(row.keys()) for row in links}
    assert shapes == {KOMI_LINK_KEYS}
    assert links[0]["title"] == "SKKN BY KIM Makeup is here!"
    assert links[0]["thumbnail"] == "https://i.ytimg.com/vi/Pxbk3q4d-nA/hqdefault.jpg"
    assert links[0]["price"] is None
    assert links[0]["currency"] is None
    assert links[1]["price"] == 32
    assert links[1]["currency"] == "USD"
    assert links[2]["thumbnail"] is None
    assert links[2]["price"] is None