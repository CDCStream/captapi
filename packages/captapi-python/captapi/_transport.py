"""HTTP transports for the generated Captapi SDK."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.captapi.com"


class CaptapiError(Exception):
    """Raised for every failed request. Never fails silently."""

    def __init__(self, message: str, status_code: int = 0, code: str | None = None, detail: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.detail = detail


def _resolve_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("CAPTAPI_API_KEY")
    if not key:
        raise CaptapiError(
            "Missing API key. Pass api_key= or set CAPTAPI_API_KEY. "
            "Get one at https://captapi.com/dashboard/api-keys",
            status_code=401,
            code="missing_api_key",
        )
    return key


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _check(response: httpx.Response, path: str) -> dict[str, Any]:
    try:
        body: Any = response.json()
    except Exception:
        body = None

    ok = response.status_code < 400 and not (isinstance(body, dict) and body.get("success") is False)
    if not ok:
        detail = body.get("detail") or body.get("error") if isinstance(body, dict) else body
        code = None
        if isinstance(detail, dict) and detail.get("error"):
            code = str(detail["error"])
        elif isinstance(body, dict) and isinstance(body.get("error"), str):
            code = body["error"]
        raise CaptapiError(
            f"Captapi {path} returned {response.status_code}: {detail!r}",
            status_code=response.status_code,
            code=code,
            detail=detail,
        )
    if not isinstance(body, dict):
        raise CaptapiError(f"Captapi {path} returned a non-JSON response", status_code=response.status_code)
    return body


class SyncTransport:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: float = 120.0) -> None:
        self._client = httpx.Client(
            base_url=(base_url or DEFAULT_BASE_URL).rstrip("/"),
            headers={"authorization": f"Bearer {_resolve_key(api_key)}", "accept": "application/json"},
            timeout=timeout,
        )

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.get(path, params=_clean_params(params))
        except httpx.HTTPError as exc:
            raise CaptapiError(f"Request to {path} failed: {exc}", code="network_error") from exc
        return _check(response, path)

    def close(self) -> None:
        self._client.close()


class AsyncTransport:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: float = 120.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=(base_url or DEFAULT_BASE_URL).rstrip("/"),
            headers={"authorization": f"Bearer {_resolve_key(api_key)}", "accept": "application/json"},
            timeout=timeout,
        )

    async def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._client.get(path, params=_clean_params(params))
        except httpx.HTTPError as exc:
            raise CaptapiError(f"Request to {path} failed: {exc}", code="network_error") from exc
        return _check(response, path)

    async def aclose(self) -> None:
        await self._client.aclose()
