from __future__ import annotations

from typing import Any, Dict, Callable, List
import time

from .transport import Transport, Response, TransportError


class Middleware:
    def __call__(
        self,
        request_fn: Callable[..., Response],
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Response:
        return request_fn(method, url, **kwargs)


class MiddlewareTransport:
    """
    Wraps a base transport with a middleware chain.
    """

    def __init__(self, base: Transport, middleware: List[Middleware]):
        self.base = base
        self.middleware = middleware

    def _dispatch(self, method: str, url: str, **kwargs: Any) -> Response:
        def call_base(method: str, url: str, **kwargs: Any) -> Response:
            if method == "GET":
                return self.base.get(url, **kwargs)
            elif method == "POST":
                return self.base.post(url, **kwargs)
            raise TransportError(f"Unsupported method: {method}")

        handler = call_base

        # Apply middleware in reverse (like a stack)
        for mw in reversed(self.middleware):
            # Create a new scope for the handler loop
            def make_handler(current_mw, current_handler):
                def wrapper(m: str, u: str, **kw: Any) -> Response:
                    return current_mw(current_handler, m, u, **kw)
                return wrapper

            handler = make_handler(mw, handler)

        return handler(method, url, **kwargs)

    def get(self, url: str, headers: Dict[str, str], timeout: int) -> Response:
        return self._dispatch("GET", url, headers=headers, timeout=timeout)

    def post(
        self,
        url: str,
        headers: Dict[str, str],
        json: Dict[str, Any],
        timeout: int,
    ) -> Response:
        return self._dispatch(
            "POST", url, headers=headers, json=json, timeout=timeout
        )


class LoggingMiddleware(Middleware):
    def __call__(self, request_fn, method, url, **kwargs):
        start = time.time()
        try:
            resp = request_fn(method, url, **kwargs)
            duration = (time.time() - start) * 1000

            print(
                f"[Jules] {method} {url} "
                f"{resp.status_code} {duration:.2f}ms"
            )
            return resp

        except Exception as e:
            duration = (time.time() - start) * 1000
            print(
                f"[Jules][ERROR] {method} {url} "
                f"{duration:.2f}ms {str(e)}"
            )
            raise

class MetricsMiddleware(Middleware):
    def __init__(self):
        self.count = 0
        self.errors = 0

    def __call__(self, request_fn, method, url, **kwargs):
        self.count += 1
        try:
            resp = request_fn(method, url, **kwargs)
            return resp
        except Exception:
            self.errors += 1
            raise

class RetryMiddleware(Middleware):
    def __init__(self, retries: int = 3, backoff: float = 0.5):
        self.retries = retries
        self.backoff = backoff

    def __call__(self, request_fn, method, url, **kwargs):
        last_error = None

        for attempt in range(self.retries):
            try:
                return request_fn(method, url, **kwargs)
            except Exception as e:
                last_error = e
                time.sleep(self.backoff * (2 ** attempt))

        raise last_error
