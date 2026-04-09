import os
import unittest

from air_korea_mcp.exceptions import AirKoreaError
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
        config = RuntimeConfig.from_env()

        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8000, config.port)
        self.assertEqual("/mcp", config.streamable_http_path)
        self.assertEqual([], config.allowed_hosts)
        self.assertEqual([], config.allowed_origins)

    def test_path_is_normalized(self):
        old = os.environ.get("AIR_KOREA_MCP_PATH")
        os.environ["AIR_KOREA_MCP_PATH"] = "custom"
        try:
            config = RuntimeConfig.from_env()
        finally:
            if old is None:
                os.environ.pop("AIR_KOREA_MCP_PATH", None)
            else:
                os.environ["AIR_KOREA_MCP_PATH"] = old

        self.assertEqual("/custom", config.streamable_http_path)

    def test_invalid_port_raises(self):
        old = os.environ.get("AIR_KOREA_MCP_PORT")
        os.environ["AIR_KOREA_MCP_PORT"] = "abc"
        try:
            with self.assertRaises(AirKoreaError):
                RuntimeConfig.from_env()
        finally:
            if old is None:
                os.environ.pop("AIR_KOREA_MCP_PORT", None)
            else:
                os.environ["AIR_KOREA_MCP_PORT"] = old

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
