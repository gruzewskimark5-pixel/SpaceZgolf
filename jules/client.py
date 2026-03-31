from __future__ import annotations
from typing import Any, Dict

from .models import Round, EventInput, EventResponse, Leaderboard
from .exceptions import (
    JulesAPIError,
    JulesAuthError,
    JulesRateLimitError,
)
from .transport import Transport, RequestsTransport, Response


class JulesClient:
    """
    Typed SDK client for the Jules REST API.
    Deterministic, stateless, retry-aware.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 10,
        transport: Transport | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport or RequestsTransport(timeout=timeout)

    # -------------------------
    # Internal helpers
    # -------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_response(self, resp: Response) -> Dict[str, Any]:
        if resp.status_code == 401:
            raise JulesAuthError("Invalid or missing API key")

        if resp.status_code == 429:
            raise JulesRateLimitError("Rate limit exceeded")

        if resp.status_code >= 400:
            raise JulesAPIError(
                f"Jules API error {resp.status_code}: {resp.text}"
            )

        if not resp.data and resp.text:
             raise JulesAPIError("Invalid JSON response from Jules API")

        return resp.data

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.transport.get(url, headers=self._headers(), timeout=self.timeout)
        return self._handle_response(resp)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.transport.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(resp)

    # -------------------------
    # Public API methods
    # -------------------------

    def get_round(self, round_id: str) -> Round:
        data = self._get(f"/rounds/{round_id}")
        return Round.from_dict(data)

    def submit_event(self, event: EventInput) -> EventResponse:
        data = self._post("/events", event.to_dict())
        return EventResponse.from_dict(data)

    def get_leaderboard(self, tournament_id: str) -> Leaderboard:
        data = self._get(f"/leaderboard/{tournament_id}")
        return Leaderboard.from_dict(data)
