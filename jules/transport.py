from __future__ import annotations

import httpx
from typing import Any, Dict, Optional, Protocol
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .exceptions import TransportError


class Response:
    """
    Minimal response wrapper to decouple from requests.Response/httpx.Response.
    """
    def __init__(self, status_code: int, data: Dict[str, Any], text: str):
        self.status_code = status_code
        self.data = data
        self.text = text


class Transport(Protocol):
    """
    Transport interface (sync).
    Enables swapping implementations (requests, httpx, mock, etc.)
    """
    def get(self, url: str, headers: Dict[str, str], timeout: int) -> Response:
        ...

    def post(
        self,
        url: str,
        headers: Dict[str, str],
        json: Dict[str, Any],
        timeout: int,
    ) -> Response:
        ...

class AsyncTransport(Protocol):
    """
    Async Transport interface.
    """
    async def get(self, url: str, headers: Dict[str, str], timeout: float) -> Response:
        ...

    async def post(
        self,
        url: str,
        headers: Dict[str, str],
        json: Dict[str, Any],
        timeout: float,
    ) -> Response:
        ...

class RequestsTransport:
    """
    Default transport using requests + retry strategy.
    """

    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 0.5,
        timeout: int = 10,
    ):
        self.timeout = timeout
        self.session = requests.Session()

        retry_config = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_config)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _wrap(self, resp: requests.Response) -> Response:
        try:
            data = resp.json()
        except ValueError:
            data = {}

        return Response(
            status_code=resp.status_code,
            data=data,
            text=resp.text,
        )

    def get(self, url: str, headers: Dict[str, str], timeout: int) -> Response:
        try:
            resp = self.session.get(url, headers=headers, timeout=timeout)
            return self._wrap(resp)
        except requests.RequestException as e:
            raise TransportError(str(e)) from e

    def post(
        self,
        url: str,
        headers: Dict[str, str],
        json: Dict[str, Any],
        timeout: int,
    ) -> Response:
        try:
            resp = self.session.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            return self._wrap(resp)
        except requests.RequestException as e:
            raise TransportError(str(e)) from e

class AsyncHttpTransport:
    """
    Async transport using httpx.
    """
    def __init__(self, timeout: float = 10.0, max_connections: int = 100, max_keepalive: int = 20):
        self.timeout = timeout
        limits = httpx.Limits(max_connections=max_connections, max_keepalive_connections=max_keepalive)
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits)

    def _wrap(self, resp: httpx.Response) -> Response:
        try:
            data = resp.json()
        except ValueError:
            data = {}

        return Response(
            status_code=resp.status_code,
            data=data,
            text=resp.text,
        )

    async def get(self, url: str, headers: Dict[str, str], timeout: float) -> Response:
        try:
            resp = await self.client.get(url, headers=headers, timeout=timeout)
            return self._wrap(resp)
        except httpx.RequestError as e:
            raise TransportError(str(e)) from e

    async def post(
        self,
        url: str,
        headers: Dict[str, str],
        json: Dict[str, Any],
        timeout: float,
    ) -> Response:

        # Inject Idempotency-Key
        if json and "source_event_id" in json:
            headers["Idempotency-Key"] = json["source_event_id"]
        elif json and isinstance(json, list) and len(json) > 0 and "source_event_id" in json[0]:
            # Batch case -> hash first event id
            import hashlib
            headers["Idempotency-Key"] = hashlib.sha256(json[0]["source_event_id"].encode()).hexdigest()

        try:
            resp = await self.client.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            return self._wrap(resp)
        except httpx.RequestError as e:
            raise TransportError(str(e)) from e
