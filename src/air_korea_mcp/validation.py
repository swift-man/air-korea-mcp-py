from __future__ import annotations

from datetime import date
from typing import Optional, Set

from .exceptions import AirKoreaError


def validate_choice(field_name: str, value: str, allowed_values: Set[str]) -> None:
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise AirKoreaError(f"{field_name} must be one of: {allowed}")


def validate_optional_iso_date(field_name: str, value: Optional[str]) -> None:
    if value is None:
        return
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise AirKoreaError(f"{field_name} must use YYYY-MM-DD format.") from exc


def validate_positive_int(field_name: str, value: int) -> None:
    if value < 1:
        raise AirKoreaError(f"{field_name} must be >= 1.")


def require_text(field_name: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise AirKoreaError(f"{field_name} must not be empty.")
    return normalized
