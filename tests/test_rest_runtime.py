import os
import unittest
from unittest.mock import patch

from air_korea_mcp.exceptions import AirKoreaConfigurationError
from air_korea_mcp.rest_runtime import RestApiRuntimeConfig


class RestApiRuntimeConfigTests(unittest.TestCase):
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AIR_KOREA_REST_HOST", None)
            os.environ.pop("AIR_KOREA_REST_PORT", None)
            config = RestApiRuntimeConfig.from_env()

        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8010, config.port)

    def test_env_overrides(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_REST_HOST": "0.0.0.0", "AIR_KOREA_REST_PORT": "18010"},
            clear=False,
        ):
            config = RestApiRuntimeConfig.from_env()

        self.assertEqual("0.0.0.0", config.host)
        self.assertEqual(18010, config.port)

    def test_empty_port_uses_default(self):
        with patch.dict(os.environ, {"AIR_KOREA_REST_PORT": "   "}, clear=False):
            config = RestApiRuntimeConfig.from_env()

        self.assertEqual(8010, config.port)

    def test_invalid_port_raises(self):
        with patch.dict(os.environ, {"AIR_KOREA_REST_PORT": "abc"}, clear=False):
            with self.assertRaises(AirKoreaConfigurationError):
                RestApiRuntimeConfig.from_env()

    def test_out_of_range_port_raises(self):
        with patch.dict(os.environ, {"AIR_KOREA_REST_PORT": "65536"}, clear=False):
            with self.assertRaises(AirKoreaConfigurationError):
                RestApiRuntimeConfig.from_env()


if __name__ == "__main__":
    unittest.main()
