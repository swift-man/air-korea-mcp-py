import os
import unittest

from air_korea_mcp.exceptions import AirKoreaError
from air_korea_mcp.runtime import RuntimeConfig, apply_runtime_config


class DummySettings:
    def __init__(self):
        self.host = None
        self.port = None
        self.streamable_http_path = None


class DummyMcp:
    def __init__(self):
        self.settings = DummySettings()


class RuntimeConfigTests(unittest.TestCase):
    def test_defaults(self):
        config = RuntimeConfig.from_env()

        self.assertEqual("streamable-http", config.transport)
        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8000, config.port)
        self.assertEqual("/mcp", config.streamable_http_path)

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

    def test_invalid_transport_raises(self):
        old = os.environ.get("AIR_KOREA_MCP_TRANSPORT")
        os.environ["AIR_KOREA_MCP_TRANSPORT"] = "invalid"
        try:
            with self.assertRaises(AirKoreaError):
                RuntimeConfig.from_env()
        finally:
            if old is None:
                os.environ.pop("AIR_KOREA_MCP_TRANSPORT", None)
            else:
                os.environ["AIR_KOREA_MCP_TRANSPORT"] = old

    def test_apply_runtime_config(self):
        config = RuntimeConfig(
            transport="streamable-http",
            host="0.0.0.0",
            port=9000,
            streamable_http_path="/air",
        )
        mcp = DummyMcp()

        apply_runtime_config(mcp, config)

        self.assertEqual("0.0.0.0", mcp.settings.host)
        self.assertEqual(9000, mcp.settings.port)
        self.assertEqual("/air", mcp.settings.streamable_http_path)


if __name__ == "__main__":
    unittest.main()
