"""Execution trace generation."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from contracts import TraceEvent, utc_now


class ExecutionTracer:
    """Collect deterministic trace events for each classification request."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []
        self._last = time.perf_counter()

    def add(self, step: str, status: str = "ok", detail: Dict[str, Any] | None = None) -> None:
        now = time.perf_counter()
        self._events.append(
            TraceEvent(
                step=step,
                status=status,
                timestamp=utc_now(),
                duration_ms=round((now - self._last) * 1000, 3),
                detail=detail or {},
            )
        )
        self._last = now

    def events(self) -> List[TraceEvent]:
        return list(self._events)
