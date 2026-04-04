from __future__ import annotations

from typing import Any, Dict, Optional, Protocol
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .exceptions import TransportError


class Response:
    """
    Minimal response wrapper to decouple from requests.Response.
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
