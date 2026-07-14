import os
import unittest
from unittest.mock import patch

from air_korea_mcp.exceptions import AirKoreaConfigurationError
from air_korea_mcp.runtime import RuntimeConfig, apply_runtime_config, build_transport_security


class DummySettings:
    def __init__(self):
        self.host = None
        self.port = None
        self.streamable_http_path = None
        self.transport_security = None


class DummyMcp:
    def __init__(self):
        self.settings = DummySettings()


class RuntimeConfigTests(unittest.TestCase):
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=False):
            for name in (
                "AIR_KOREA_MCP_HOST",
                "AIR_KOREA_MCP_PORT",
                "AIR_KOREA_MCP_PATH",
                "AIR_KOREA_MCP_ALLOWED_HOSTS",
                "AIR_KOREA_MCP_ALLOWED_ORIGINS",
            ):
                os.environ.pop(name, None)
            config = RuntimeConfig.from_env()

        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8000, config.port)
        self.assertEqual("/mcp", config.streamable_http_path)
        self.assertEqual([], config.allowed_hosts)
        self.assertEqual([], config.allowed_origins)

    def test_path_is_normalized(self):
        with patch.dict(os.environ, {"AIR_KOREA_MCP_PATH": "custom"}, clear=False):
            config = RuntimeConfig.from_env()

        self.assertEqual("/custom", config.streamable_http_path)

    def test_invalid_port_raises(self):
        with patch.dict(os.environ, {"AIR_KOREA_MCP_PORT": "abc"}, clear=False):
            with self.assertRaises(AirKoreaConfigurationError):
                RuntimeConfig.from_env()

    def test_empty_port_uses_default(self):
        with patch.dict(os.environ, {"AIR_KOREA_MCP_PORT": "   "}, clear=False):
            config = RuntimeConfig.from_env()

        self.assertEqual(8000, config.port)

    def test_out_of_range_port_raises(self):
        for port in ("0", "65536"):
            with self.subTest(port=port):
                with patch.dict(os.environ, {"AIR_KOREA_MCP_PORT": port}, clear=False):
                    with self.assertRaises(AirKoreaConfigurationError):
                        RuntimeConfig.from_env()

    def test_apply_runtime_config(self):
        config = RuntimeConfig(host="0.0.0.0", port=9000, streamable_http_path="/air")
        mcp = DummyMcp()

        apply_runtime_config(mcp, config)

        self.assertEqual("0.0.0.0", mcp.settings.host)
        self.assertEqual(9000, mcp.settings.port)
        self.assertEqual("/air", mcp.settings.streamable_http_path)
        self.assertFalse(mcp.settings.transport_security.enable_dns_rebinding_protection)

    def test_build_transport_security_enables_loopback_defaults(self):
        config = RuntimeConfig(host="127.0.0.1", port=8000, streamable_http_path="/mcp")

        security = build_transport_security(config)

        self.assertTrue(security.enable_dns_rebinding_protection)
        self.assertIn("127.0.0.1:*", security.allowed_hosts)

    def test_build_transport_security_respects_custom_allowed_hosts(self):
        config = RuntimeConfig(
            host="0.0.0.0",
            port=8021,
            streamable_http_path="/mcp",
            allowed_hosts=["192.168.1.218:*", "127.0.0.1:*"],
            allowed_origins=["http://127.0.0.1:*"],
        )

        security = build_transport_security(config)

        self.assertTrue(security.enable_dns_rebinding_protection)
        self.assertEqual(["192.168.1.218:*", "127.0.0.1:*"], security.allowed_hosts)
        self.assertEqual(["http://127.0.0.1:*"], security.allowed_origins)


if __name__ == "__main__":
    unittest.main()
