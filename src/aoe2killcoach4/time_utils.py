"""Utilities for parsing time values."""
from __future__ import annotations

from datetime import timedelta
from typing import Any


TIME_KEYS = {
    "time",
    "t",
    "t_sec",
    "timestamp",
    "duration",
    "uptime",
    "click_time",
    "start",
    "end",
    "response_time",
    "threat_switch_time",
}


def coerce_seconds(value: Any) -> int | None:
    """Coerce common replay time formats into whole seconds."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, timedelta):
        return int(value.total_seconds())
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.replace(".", "", 1).isdigit():
            return int(float(stripped))
        parts = stripped.split(":")
        if len(parts) in {2, 3}:
            hours = 0
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
            else:
                minutes = int(parts[0])
                seconds = float(parts[1])
            total = hours * 3600 + minutes * 60 + seconds
            return int(total)
    raise ValueError(f"Unsupported time format: {value!r}")


def normalize_time_fields(obj: Any) -> Any:
    """Normalize time-like fields in nested structures."""
    if isinstance(obj, list):
        return [normalize_time_fields(item) for item in obj]
    if isinstance(obj, dict):
        normalized: dict[Any, Any] = {}
        for key, value in obj.items():
            normalized_value = normalize_time_fields(value)
            if isinstance(key, str) and key in TIME_KEYS:
                try:
                    normalized_value = coerce_seconds(normalized_value)
                except ValueError:
                    normalized_value = normalized_value
            normalized[key] = normalized_value
        return normalized
    return obj
