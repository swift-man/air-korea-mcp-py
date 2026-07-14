import os
import unittest
from unittest.mock import patch

from air_korea_mcp.exceptions import AirKoreaConfigurationError
from air_korea_mcp.settings import AirKoreaSettings, ServiceKeyConfig


class SettingsTests(unittest.TestCase):
    def test_service_key_is_required(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(AirKoreaConfigurationError, "AIR_KOREA_SERVICE_KEY"):
                ServiceKeyConfig.from_env()

    def test_invalid_timeout_is_configuration_error(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_TIMEOUT_SECONDS": "invalid"},
            clear=True,
        ):
            with self.assertRaisesRegex(AirKoreaConfigurationError, "must be numeric"):
                AirKoreaSettings.from_env()

    def test_valid_settings_are_loaded(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_TIMEOUT_SECONDS": "3.5"},
            clear=True,
        ):
            settings = AirKoreaSettings.from_env()

        self.assertEqual("serviceKey=test-key", settings.service_key.to_query_segment())
        self.assertEqual(3.5, settings.timeout_seconds)


if __name__ == "__main__":
    unittest.main()
