import os
import unittest

from air_korea_mcp.exceptions import AirKoreaError
from air_korea_mcp.rest_runtime import RestApiRuntimeConfig


class RestApiRuntimeConfigTests(unittest.TestCase):
    def test_defaults(self):
        config = RestApiRuntimeConfig.from_env()

        self.assertEqual("127.0.0.1", config.host)
        self.assertEqual(8010, config.port)

    def test_env_overrides(self):
        old_host = os.environ.get("AIR_KOREA_REST_HOST")
        old_port = os.environ.get("AIR_KOREA_REST_PORT")
        os.environ["AIR_KOREA_REST_HOST"] = "0.0.0.0"
        os.environ["AIR_KOREA_REST_PORT"] = "18010"
        try:
            config = RestApiRuntimeConfig.from_env()
        finally:
            restore_env("AIR_KOREA_REST_HOST", old_host)
            restore_env("AIR_KOREA_REST_PORT", old_port)

        self.assertEqual("0.0.0.0", config.host)
        self.assertEqual(18010, config.port)

    def test_invalid_port_raises(self):
        old_port = os.environ.get("AIR_KOREA_REST_PORT")
        os.environ["AIR_KOREA_REST_PORT"] = "abc"
        try:
            with self.assertRaises(AirKoreaError):
                RestApiRuntimeConfig.from_env()
        finally:
            restore_env("AIR_KOREA_REST_PORT", old_port)


def restore_env(name, value):
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


if __name__ == "__main__":
    unittest.main()
