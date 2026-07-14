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

    def test_whitespace_service_keys_are_rejected(self):
        for variable_name in ("AIR_KOREA_SERVICE_KEY", "AIR_KOREA_SERVICE_KEY_ENCODED"):
            with self.subTest(variable_name=variable_name):
                with patch.dict(os.environ, {variable_name: "   "}, clear=True):
                    with self.assertRaises(AirKoreaConfigurationError):
                        ServiceKeyConfig.from_env()

    def test_service_keys_are_trimmed(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_SERVICE_KEY": "  test-key  "},
            clear=True,
        ):
            service_key = ServiceKeyConfig.from_env()

        self.assertEqual("serviceKey=test-key", service_key.to_query_segment())

    def test_invalid_timeout_is_configuration_error(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_TIMEOUT_SECONDS": "invalid"},
            clear=True,
        ):
            with self.assertRaisesRegex(AirKoreaConfigurationError, "positive finite"):
                AirKoreaSettings.from_env()

    def test_non_positive_or_non_finite_timeout_is_rejected(self):
        for timeout in ("0", "-1", "nan", "inf", "-inf"):
            with self.subTest(timeout=timeout):
                with patch.dict(
                    os.environ,
                    {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_TIMEOUT_SECONDS": timeout},
                    clear=True,
                ):
                    with self.assertRaisesRegex(AirKoreaConfigurationError, "positive finite"):
                        AirKoreaSettings.from_env()

    def test_invalid_api_base_is_rejected(self):
        for api_base in (
            "",
            "example.com",
            "ftp://example.com",
            "https://",
            "https://bad host",
            "https://example.com:invalid",
            "https://example.com/api?token=value",
            "https://example.com/api#fragment",
        ):
            with self.subTest(api_base=api_base):
                with patch.dict(
                    os.environ,
                    {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_API_BASE": api_base},
                    clear=True,
                ):
                    with self.assertRaisesRegex(AirKoreaConfigurationError, "HTTP or HTTPS URL"):
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

    def test_api_base_is_trimmed_and_normalized(self):
        with patch.dict(
            os.environ,
            {"AIR_KOREA_SERVICE_KEY": "test-key", "AIR_KOREA_API_BASE": "  https://example.com/api/  "},
            clear=True,
        ):
            settings = AirKoreaSettings.from_env()

        self.assertEqual("https://example.com/api", settings.api_base)


if __name__ == "__main__":
    unittest.main()
