"""Backward-compatible facade around the service layer."""

from .exceptions import AirKoreaError
from .reference import build_reference_payload
from .service import AirKoreaService


class AirKoreaClient(AirKoreaService):
    """Backward-compatible alias for the service layer."""


__all__ = ["AirKoreaClient", "AirKoreaError", "build_reference_payload"]
