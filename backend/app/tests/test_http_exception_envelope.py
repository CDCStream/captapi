"""MP2 — HTTPException uses the catalogue error envelope."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.main import create_app


def test_http_exception_envelope_string_detail():
    app = create_app()

    @app.get("/__test_mp2_not_found")
    async def _boom():
        raise HTTPException(status_code=404, detail="Listing not found")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/__test_mp2_not_found")
    assert r.status_code == 404
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Listing not found"
    assert "creditsUsed" in body
    assert "requestId" in body
    assert "fetchedAt" in body
    assert "detail" not in body


def test_http_exception_envelope_structured_detail():
    app = create_app()

    @app.get("/__test_mp2_timeout")
    async def _boom():
        raise HTTPException(
            status_code=504,
            detail={"code": "UPSTREAM_TIMEOUT", "message": "timed out"},
        )

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/__test_mp2_timeout")
    assert r.status_code == 504
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UPSTREAM_TIMEOUT"
    assert body["error"]["message"] == "timed out"
