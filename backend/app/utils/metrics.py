"""Operational metrics collector for application performance monitoring."""

from datetime import datetime, timezone
import threading
from typing import Any, Dict


class MetricsCollector:
    """Thread-safe operational telemetry metrics aggregator."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.start_time = datetime.now(timezone.utc)
        self.request_count = 0
        self.endpoint_counts: Dict[str, int] = {}
        self.total_latency_ms = 0.0
        self.active_websocket_connections = 0
        self.rule_evaluations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.auth_successes = 0
        self.auth_failures = 0
        self.ai_reasoning_requests = 0
        self.simulation_executions = 0

    def record_request(self, endpoint: str, latency_ms: float) -> None:
        """Record HTTP request metric."""
        with self._lock:
            self.request_count += 1
            self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
            self.total_latency_ms += latency_ms

    def record_websocket_connect(self) -> None:
        """Increment active WebSocket connection count."""
        with self._lock:
            self.active_websocket_connections += 1

    def record_websocket_disconnect(self) -> None:
        """Decrement active WebSocket connection count."""
        with self._lock:
            self.active_websocket_connections = max(0, self.active_websocket_connections - 1)

    def record_rule_evaluation(self, count: int = 1) -> None:
        """Increment rule evaluations counter."""
        with self._lock:
            self.rule_evaluations += count

    def record_cache_hit(self) -> None:
        """Increment cache hit counter."""
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Increment cache miss counter."""
        with self._lock:
            self.cache_misses += 1

    def record_auth_success(self) -> None:
        """Increment authentication success counter."""
        with self._lock:
            self.auth_successes += 1

    def record_auth_failure(self) -> None:
        """Increment authentication failure counter."""
        with self._lock:
            self.auth_failures += 1

    def record_ai_request(self) -> None:
        """Increment AI reasoning copilot request counter."""
        with self._lock:
            self.ai_reasoning_requests += 1

    def record_simulation_execution(self) -> None:
        """Increment simulation execution counter."""
        with self._lock:
            self.simulation_executions += 1

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Return structured operational metrics payload."""
        with self._lock:
            uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            avg_latency = round(self.total_latency_ms / self.request_count, 2) if self.request_count > 0 else 0.0
            total_cache_ops = self.cache_hits + self.cache_misses
            cache_hit_rate = round(self.cache_hits / total_cache_ops, 4) if total_cache_ops > 0 else 1.0

            return {
                "uptime_seconds": round(uptime_seconds, 1),
                "requests": {
                    "total_count": self.request_count,
                    "avg_latency_ms": avg_latency,
                    "top_endpoints": dict(sorted(self.endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10])
                },
                "websockets": {
                    "active_connections": self.active_websocket_connections
                },
                "detection": {
                    "rule_evaluations": self.rule_evaluations,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "cache_hit_rate": cache_hit_rate
                },
                "security_auth": {
                    "success_count": self.auth_successes,
                    "failure_count": self.auth_failures
                },
                "ai_and_simulations": {
                    "ai_reasoning_requests": self.ai_reasoning_requests,
                    "simulation_executions": self.simulation_executions
                }
            }


# Central singleton instance
metrics_collector = MetricsCollector()
