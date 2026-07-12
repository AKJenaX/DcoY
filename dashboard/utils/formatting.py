"""Data formatting, timestamp extraction, and structuring utilities for dashboard components."""

import pandas as pd
from typing import Any, Dict, List

from dashboard.utils.constants import DEFAULT_FALLBACK_TIMESTAMP


def extract_event_timestamp(row: Dict[str, Any]) -> str:
    """Extract an event timestamp from a row dict, checking top-level and nested details.

    Lookup order:
    1. ``row["timestamp"]``
    2. ``row["details"]["timestamp"]``
    3. Falls back to ``DEFAULT_FALLBACK_TIMESTAMP``.

    Returns:
        An ISO-8601 timestamp string, never ``None``.
    """
    t = row.get("timestamp")
    if t:
        return str(t)
    details = row.get("details", {})
    if isinstance(details, dict):
        t = details.get("timestamp")
        if t:
            return str(t)
    return DEFAULT_FALLBACK_TIMESTAMP


def format_attack_locations(explain_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and structure location coordinates for map rendering."""
    locations = []
    for row in explain_rows:
        loc = row.get("location")
        if loc and isinstance(loc, dict):
            if loc.get("lat") is not None and loc.get("lon") is not None:
                locations.append({
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lon"),
                    "ip": row.get("ip", "Unknown"),
                    "country": loc.get("country", "Unknown"),
                    "city": loc.get("city", "Unknown"),
                })
    return locations


def get_preferred_log_columns(df: pd.DataFrame) -> List[str]:
    """Retrieve existing columns matched against preferred layout ordering."""
    preferred = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    return [col for col in preferred if col in df.columns]
