import socket
from typing import Any, Dict, Optional


def capture_basic_event() -> Optional[Dict[str, Any]]:
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        return {
            "ip": ip,
            "failed_logins": 0,
            "port_attempts": 1,
            "request_rate": 5.0,
        }
    except Exception:
        return None
