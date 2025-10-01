"""Instrumentation helpers for performance scenarios."""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse


@dataclass
class PerfResult:
    """Result metadata for HTTP measurements."""

    duration_s: float
    query_count: int
    response: Any

    @property
    def duration_ms(self) -> float:
        return self.duration_s * 1000

    @property
    def status_code(self) -> int:
        return getattr(self.response, "status_code", 0)

    @property
    def payload_bytes(self) -> int:
        content = getattr(self.response, "content", b"")
        if content is None:
            return 0
        return len(content)


@dataclass
class PerfCallResult:
    """Result metadata for callable measurements."""

    duration_s: float
    query_count: int
    value: Any

    @property
    def duration_ms(self) -> float:
        return self.duration_s * 1000


_METRIC_LOCK = threading.Lock()


class PerfHTTPRunner:
    """Wrap Django's test client with timing/query instrumentation."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or Client()

    def get(
        self,
        url_name: str,
        *,
        user: Optional[Any] = None,
        reverse_kwargs: Optional[dict] = None,
        params: Optional[dict] = None,
        expected_status: Optional[int] = 200,
    ) -> PerfResult:
        if user is not None:
            self.client.force_login(user)

        url = reverse(url_name, kwargs=reverse_kwargs or {})
        start = time.perf_counter()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url, data=params or {})
        duration = time.perf_counter() - start

        if expected_status is not None:
            assert (
                response.status_code == expected_status
            ), f"Expected {expected_status}, got {response.status_code}"

        return PerfResult(duration, len(ctx.captured_queries), response)

    def post(
        self,
        url_name: str,
        *,
        user: Optional[Any] = None,
        reverse_kwargs: Optional[dict] = None,
        data: Optional[dict] = None,
        expected_status: Optional[int] = 200,
    ) -> PerfResult:
        if user is not None:
            self.client.force_login(user)

        url = reverse(url_name, kwargs=reverse_kwargs or {})
        start = time.perf_counter()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.post(url, data=data or {})
        duration = time.perf_counter() - start

        if expected_status is not None:
            assert (
                response.status_code == expected_status
            ), f"Expected {expected_status}, got {response.status_code}"

        return PerfResult(duration, len(ctx.captured_queries), response)


def measure_callable(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> PerfCallResult:
    """Measure a callable's execution time and database footprint."""

    start = time.perf_counter()
    with CaptureQueriesContext(connection) as ctx:
        value = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return PerfCallResult(duration, len(ctx.captured_queries), value)


def record_perf_metric(
    name: str, result: Any, extra: Optional[dict[str, Any]] = None
) -> None:
    """Append result metadata to the JSON metrics file if configured."""

    metrics_path = os.getenv("PERF_METRICS_FILE")
    if not metrics_path:
        return

    payload: dict[str, Any] = {
        "name": name,
        "duration_ms": getattr(result, "duration_ms", None),
        "query_count": getattr(result, "query_count", None),
    }

    if isinstance(result, PerfResult):
        payload["status_code"] = result.status_code
        payload["payload_bytes"] = result.payload_bytes

    if extra:
        payload.update(extra)

    target = Path(metrics_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with _METRIC_LOCK:
        if target.exists():
            try:
                data = json.loads(target.read_text())
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        data.append(payload)
        target.write_text(json.dumps(data, indent=2))
