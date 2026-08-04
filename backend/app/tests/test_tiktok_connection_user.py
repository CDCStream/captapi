from __future__ import annotations

from app.services.tiktok_native import _map_connection_user


def test_map_connection_user_identity_and_analysis_fields() -> None:
    mapped = _map_connection_user(
        {
            "user": {
                "id": "7084524072541307910",
                "secUid": "MS4wLjABAAAAU2DhFzvc",
                "uniqueId": "abdullah007a3",
                "nickname": "Abdullah",
                "signature": "hi",
                "verified": False,
                "region": "US",
                "language": "en",
                "createTime": 1649497070,
                "avatarMedium": {"url_list": ["https://cdn.example/a.jpg"]},
            },
            "stats": {"followerCount": 12, "followingCount": 41},
        }
    )
    assert mapped is not None
    assert mapped["id"] == "7084524072541307910"
    assert mapped["secUid"] == "MS4wLjABAAAAU2DhFzvc"
    assert mapped["username"] == "abdullah007a3"
    assert mapped["followers"] == 12
    assert mapped["following"] == 41
    assert mapped["region"] == "US"
    assert mapped["language"] == "en"
    assert mapped["createTimeUnix"] == 1649497070
    assert mapped["createTime"] == "2022-04-09T09:37:50.000Z"
    assert mapped["url"] == "https://www.tiktok.com/@abdullah007a3"


def test_map_connection_user_keeps_null_region_language() -> None:
    mapped = _map_connection_user(
        {
            "user": {
                "uniqueId": "sparse",
                "nickname": "Sparse",
            },
            "stats": {},
        }
    )
    assert mapped is not None
    assert mapped["username"] == "sparse"
    assert "id" not in mapped
    assert "secUid" not in mapped
    assert "createTime" not in mapped
    assert "region" in mapped and mapped["region"] is None
    assert "language" in mapped and mapped["language"] is None
    assert mapped["followers"] is None
    assert mapped["following"] is None