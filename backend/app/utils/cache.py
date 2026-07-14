"""Thread-safe SimpleCache utility with Time-To-Live (TTL) and size-bound evictions."""

import time
import threading
from typing import Any, Dict, Optional, Tuple


class SimpleCache:
    """A thread-safe cache with capacity bounding and expiration times."""

    def __init__(self, default_ttl_sec: Optional[float] = None, max_size: int = 1000) -> None:
        self._store: Dict[str, Tuple[Any, Optional[float]]] = {}
        self.default_ttl_sec = default_ttl_sec
        self.max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value if key exists and has not expired."""
        with self._lock:
            if key not in self._store:
                return None
            val, expiry = self._store[key]
            if expiry is not None and time.time() > expiry:
                del self._store[key]
                return None
            return val

    def set(self, key: str, value: Any, ttl_sec: Optional[float] = None) -> None:
        """Associate value with key, evicting oldest keys if max size reached."""
        with self._lock:
            # Enforce max size bounding via FIFO eviction
            if len(self._store) >= self.max_size and key not in self._store:
                oldest_key = next(iter(self._store))
                del self._store[oldest_key]

            ttl = ttl_sec if ttl_sec is not None else self.default_ttl_sec
            expiry = time.time() + ttl if ttl is not None else None
            self._store[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Explicitly purge a key from the cache store."""
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        """Clear all entries in the cache."""
        with self._lock:
            self._store.clear()
