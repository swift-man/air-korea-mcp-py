from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .exceptions import AirKoreaError

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_STREAMABLE_HTTP_PATH = "/mcp"


@dataclass(frozen=True)
class RuntimeConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    streamable_http_path: str = DEFAULT_STREAMABLE_HTTP_PATH

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        host = os.getenv("AIR_KOREA_MCP_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
        port_raw = os.getenv("AIR_KOREA_MCP_PORT", str(DEFAULT_PORT)).strip()
        path = os.getenv("AIR_KOREA_MCP_PATH", DEFAULT_STREAMABLE_HTTP_PATH).strip() or DEFAULT_STREAMABLE_HTTP_PATH

        try:
            port = int(port_raw)
        except ValueError as exc:
            raise AirKoreaError("AIR_KOREA_MCP_PORT must be an integer.") from exc

        if port < 1 or port > 65535:
            raise AirKoreaError("AIR_KOREA_MCP_PORT must be between 1 and 65535.")

        if not path.startswith("/"):
            path = f"/{path}"

        return cls(
            host=host,
            port=port,
            streamable_http_path=path,
        )


class SupportsStreamableHttpSettings(Protocol):
    host: str
    port: int
    streamable_http_path: str


class SupportsStreamableHttpRuntime(Protocol):
    settings: SupportsStreamableHttpSettings


def apply_runtime_config(mcp: SupportsStreamableHttpRuntime, config: RuntimeConfig) -> None:
    mcp.settings.host = config.host
    mcp.settings.port = config.port
    mcp.settings.streamable_http_path = config.streamable_http_path
