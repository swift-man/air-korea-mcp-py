"""Backward-compatible facade around the service layer."""

from .bootstrap import create_air_korea_service
from .exceptions import AirKoreaError
from .reference import build_reference_payload
from .service import AirKoreaService

AirKoreaClient = AirKoreaService


__all__ = ["AirKoreaClient", "AirKoreaError", "build_reference_payload", "create_air_korea_service"]
