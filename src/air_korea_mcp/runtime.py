from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from .exceptions import AirKoreaError

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_STREAMABLE_HTTP_PATH = "/mcp"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
LOOPBACK_ALLOWED_HOSTS = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
LOOPBACK_ALLOWED_ORIGINS = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]


@dataclass(frozen=True)
class RuntimeConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    streamable_http_path: str = DEFAULT_STREAMABLE_HTTP_PATH
    allowed_hosts: list[str] = field(default_factory=list)
    allowed_origins: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        host = os.getenv("AIR_KOREA_MCP_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
        port_raw = os.getenv("AIR_KOREA_MCP_PORT", str(DEFAULT_PORT)).strip()
        path = os.getenv("AIR_KOREA_MCP_PATH", DEFAULT_STREAMABLE_HTTP_PATH).strip() or DEFAULT_STREAMABLE_HTTP_PATH
        allowed_hosts = _split_csv_env("AIR_KOREA_MCP_ALLOWED_HOSTS")
        allowed_origins = _split_csv_env("AIR_KOREA_MCP_ALLOWED_ORIGINS")

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
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        )


class SupportsStreamableHttpSettings(Protocol):
    host: str
    port: int
    streamable_http_path: str
    transport_security: Any


class SupportsStreamableHttpRuntime(Protocol):
    settings: SupportsStreamableHttpSettings


def apply_runtime_config(mcp: SupportsStreamableHttpRuntime, config: RuntimeConfig) -> None:
    mcp.settings.host = config.host
    mcp.settings.port = config.port
    mcp.settings.streamable_http_path = config.streamable_http_path
    mcp.settings.transport_security = build_transport_security(config)


@dataclass(frozen=True)
class TransportSecurityConfig:
    enable_dns_rebinding_protection: bool
    allowed_hosts: list[str]
    allowed_origins: list[str]


def build_transport_security(config: RuntimeConfig) -> Any:
    if config.allowed_hosts or config.allowed_origins:
        return _make_transport_security_settings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=config.allowed_hosts,
            allowed_origins=config.allowed_origins,
        )

    if config.host in LOOPBACK_HOSTS:
        return _make_transport_security_settings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=LOOPBACK_ALLOWED_HOSTS,
            allowed_origins=LOOPBACK_ALLOWED_ORIGINS,
        )

    return _make_transport_security_settings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=[],
        allowed_origins=[],
    )


def _make_transport_security_settings(
    enable_dns_rebinding_protection: bool,
    allowed_hosts: list[str],
    allowed_origins: list[str],
) -> Any:
    try:
        from mcp.server.transport_security import TransportSecuritySettings
    except ModuleNotFoundError:
        return TransportSecurityConfig(
            enable_dns_rebinding_protection=enable_dns_rebinding_protection,
            allowed_hosts=list(allowed_hosts),
            allowed_origins=list(allowed_origins),
        )

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=enable_dns_rebinding_protection,
        allowed_hosts=list(allowed_hosts),
        allowed_origins=list(allowed_origins),
    )


def _split_csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return []
    return [value.strip() for value in raw.split(",") if value.strip()]
