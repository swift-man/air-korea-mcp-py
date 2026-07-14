from __future__ import annotations

import os
from dataclasses import dataclass

from .exceptions import AirKoreaConfigurationError

DEFAULT_REST_HOST = "127.0.0.1"
DEFAULT_REST_PORT = 8010


@dataclass(frozen=True)
class RestApiRuntimeConfig:
    host: str = DEFAULT_REST_HOST
    port: int = DEFAULT_REST_PORT

    @classmethod
    def from_env(cls) -> "RestApiRuntimeConfig":
        host = os.getenv("AIR_KOREA_REST_HOST", DEFAULT_REST_HOST).strip() or DEFAULT_REST_HOST
        port_raw = os.getenv("AIR_KOREA_REST_PORT", str(DEFAULT_REST_PORT)).strip() or str(DEFAULT_REST_PORT)

        try:
            port = int(port_raw)
        except ValueError as exc:
            raise AirKoreaConfigurationError("AIR_KOREA_REST_PORT must be an integer.") from exc

        if port < 1 or port > 65535:
            raise AirKoreaConfigurationError("AIR_KOREA_REST_PORT must be between 1 and 65535.")

        return cls(host=host, port=port)
