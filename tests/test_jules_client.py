import pytest
from jules.client import JulesClient
from jules.models import EventInput, Round, Leaderboard
from jules.transport import Response

class FakeTransport:
    def get(self, *args, **kwargs):
        if "rounds/r1" in args[0]:
             return Response(200, {"id": "r1", "score": 72, "status": "ok"}, "")
        if "leaderboard/t1" in args[0]:
             return Response(200, {"entries": [{"player_id": "p1", "score": 72}]}, "")

        return Response(404, {}, "Not found")

    def post(self, *args, **kwargs):
        return Response(200, {"event_id": "e1", "status": "ok"}, "")


def test_submit_event():
    transport = FakeTransport()
    client = JulesClient(api_key="test", base_url="https://api.jules.dev", transport=transport)

    event = EventInput(player_id="p1", action="swing", value=1.0)
    resp = client.submit_event(event)

    assert resp.event_id == "e1"
    assert resp.status == "ok"


def test_get_round():
    transport = FakeTransport()
    client = JulesClient(api_key="test", base_url="https://api.jules.dev", transport=transport)

    resp = client.get_round("r1")

    assert isinstance(resp, Round)
    assert resp.id == "r1"
    assert resp.score == 72
    assert resp.status == "ok"

def test_get_leaderboard():
    transport = FakeTransport()
    client = JulesClient(api_key="test", base_url="https://api.jules.dev", transport=transport)

    resp = client.get_leaderboard("t1")

    assert isinstance(resp, Leaderboard)
    assert len(resp.entries) == 1
    assert resp.entries[0].player_id == "p1"
    assert resp.entries[0].score == 72


from jules.middleware import MiddlewareTransport, MetricsMiddleware, RetryMiddleware
from jules.exceptions import TransportError

class FailingTransport:
    def __init__(self, fail_times):
        self.attempts = 0
        self.fail_times = fail_times

    def get(self, *args, **kwargs):
        self.attempts += 1
        if self.attempts <= self.fail_times:
             raise TransportError("Simulated network failure")
        return Response(200, {"id": "r1", "score": 72, "status": "ok"}, "")

    def post(self, *args, **kwargs):
        self.attempts += 1
        if self.attempts <= self.fail_times:
             raise TransportError("Simulated network failure")
        return Response(200, {"event_id": "e1", "status": "ok"}, "")


def test_middleware_chain():
    metrics = MetricsMiddleware()
    retry = RetryMiddleware(retries=3, backoff=0.01) # fast backoff for testing

    # Base transport fails twice, then succeeds
    base = FailingTransport(fail_times=2)

    transport = MiddlewareTransport(
        base=base,
        middleware=[
            metrics,
            retry,
        ]
    )

    client = JulesClient(api_key="test", base_url="https://api.jules.dev", transport=transport)

    # 1st call to client (will internally retry 3 times, succeeding on the 3rd attempt)
    resp = client.get_round("r1")

    assert resp.id == "r1"
    assert base.attempts == 3 # Transport was called 3 times
    assert metrics.count == 1 # Metrics middleware only saw 1 logical request
    assert metrics.errors == 0
