from __future__ import annotations

from app.routers.tiktok import _normalize_profile_region
from app.services.tiktok_native import _profile_identity_fields


def test_profile_identity_fields_promoted() -> None:
    out = _profile_identity_fields(
        {
            "id": "127905465618821121",
            "secUid": "MS4wLjABAAAA",
            "createTime": 1470866554,
            "ttSeller": False,
            "isOrganization": 0,
        }
    )
    assert out["id"] == "127905465618821121"
    assert out["secUid"] == "MS4wLjABAAAA"
    assert out["createTime"] == "2016-08-10T22:02:34.000Z"
    assert out["createTimeUnix"] == 1470866554
    assert out["ttSeller"] is False
    assert out["isOrganization"] == 0


def test_normalize_profile_region_promotes_identity() -> None:
    out = _normalize_profile_region(
        {
            "user": {
                "uniqueId": "khaby.lame",
                "nickname": "Khabane lame",
                "id": "127905465618821121",
                "secUid": "MS4wLjABAAAA",
                "createTime": 1470866554,
                "ttSeller": False,
                "isOrganization": 0,
                "verified": True,
                "language": "en",
                "heartCount": 10,
                "videoCount": 3,
            }
        },
        "khaby.lame",
    )
    assert out["id"] == "127905465618821121"
    assert out["secUid"] == "MS4wLjABAAAA"
    assert out["createTimeUnix"] == 1470866554
    assert out["ttSeller"] is False
    assert out["isOrganization"] == 0
    assert out["username"] == "khaby.lame"
