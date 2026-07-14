from __future__ import annotations

import os
from dataclasses import dataclass
from math import isfinite
from typing import Optional
from urllib import parse

from .constants import API_BASE, DEFAULT_TIMEOUT_SECONDS
from .exceptions import AirKoreaConfigurationError


@dataclass(frozen=True)
class ServiceKeyConfig:
    raw_key: Optional[str] = None
    encoded_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ServiceKeyConfig":
        raw_key = (os.getenv("AIR_KOREA_SERVICE_KEY") or "").strip() or None
        encoded_key = (os.getenv("AIR_KOREA_SERVICE_KEY_ENCODED") or "").strip() or None
        if not raw_key and not encoded_key:
            raise AirKoreaConfigurationError(
                "Set AIR_KOREA_SERVICE_KEY or AIR_KOREA_SERVICE_KEY_ENCODED before starting the server."
            )
        return cls(raw_key=raw_key, encoded_key=encoded_key)

    def to_query_segment(self) -> str:
        if self.encoded_key:
            return f"serviceKey={self.encoded_key}"
        assert self.raw_key is not None
        encoded = parse.quote(self.raw_key, safe="")
        return f"serviceKey={encoded}"


@dataclass(frozen=True)
class AirKoreaSettings:
    service_key: ServiceKeyConfig
    api_base: str = API_BASE
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "AirKoreaSettings":
        api_base = os.getenv("AIR_KOREA_API_BASE", API_BASE).strip().rstrip("/")
        try:
            parsed_api_base = parse.urlsplit(api_base)
            _ = parsed_api_base.port
        except ValueError as exc:
            raise AirKoreaConfigurationError(
                "AIR_KOREA_API_BASE must be a valid HTTP or HTTPS URL."
            ) from exc
        if (
            parsed_api_base.scheme not in {"http", "https"}
            or not parsed_api_base.hostname
            or parsed_api_base.query
            or parsed_api_base.fragment
            or any(character.isspace() for character in api_base)
        ):
            raise AirKoreaConfigurationError("AIR_KOREA_API_BASE must be a valid HTTP or HTTPS URL.")

        timeout_raw = os.getenv("AIR_KOREA_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
        try:
            timeout_seconds = float(timeout_raw)
        except ValueError as exc:
            raise AirKoreaConfigurationError(
                "AIR_KOREA_TIMEOUT_SECONDS must be a positive finite number."
            ) from exc
        if not isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise AirKoreaConfigurationError(
                "AIR_KOREA_TIMEOUT_SECONDS must be a positive finite number."
            )

        return cls(
            service_key=ServiceKeyConfig.from_env(),
            api_base=api_base,
            timeout_seconds=timeout_seconds,
        )
