"""Data formatting and structuring utilities for Streamlit components."""

import pandas as pd
from typing import Any, Dict, List

def format_attack_locations(explain_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and structure location coordinates for Map rendering."""
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
