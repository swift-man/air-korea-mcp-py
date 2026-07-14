import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from air_korea_mcp.exceptions import AirKoreaConfigurationError, AirKoreaError, AirKoreaGatewayError
from air_korea_mcp.rest_api import create_app


class FakeService:
    def __init__(self):
        self.calls = []

    def get_air_quality_forecast(self, inform_code="PM10", search_date=None, page_no=1, num_of_rows=100):
        self.calls.append(("forecast", inform_code, search_date, page_no, num_of_rows))
        return {"endpoint": "getMinuDustFrcstDspth", "request_params": {"InformCode": inform_code}}

    def get_pm25_weekly_forecast(self, search_date=None, page_no=1, num_of_rows=100):
        self.calls.append(("weekly", search_date, page_no, num_of_rows))
        return {"endpoint": "getMinuDustWeekFrcstDspth"}

    def get_station_measurements(
        self,
        station_name,
        data_term="DAILY",
        page_no=1,
        num_of_rows=100,
        version="1.0",
    ):
        self.calls.append(("station", station_name, data_term, page_no, num_of_rows, version))
        return {"endpoint": "getMsrstnAcctoRltmMesureDnsty"}

    def get_bad_khai_stations(self, page_no=1, num_of_rows=100):
        self.calls.append(("bad-khai", page_no, num_of_rows))
        return {"endpoint": "getUnityAirEnvrnIdexSnstiveAboveMsrstnList"}

    def get_sido_measurements(self, sido_name, page_no=1, num_of_rows=100, version="1.0"):
        self.calls.append(("sido", sido_name, page_no, num_of_rows, version))
        return {"endpoint": "getCtprvnRltmMesureDnsty", "request_params": {"sidoName": sido_name}}


class RestApiTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        patcher = patch("air_korea_mcp.rest_api.get_service", return_value=self.service)
        self.addCleanup(patcher.stop)
        self.get_service = patcher.start()
        self.client = TestClient(create_app())

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])

    def test_account_view_explains_login_gated_portal(self):
        response = self.client.get("/api/data-go-kr/account-view")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["server_to_server_supported"])
        self.assertIn("selectAPIAcountView.do", payload["url"])

    def test_reference_returns_supported_options(self):
        response = self.client.get("/api/reference")

        self.assertEqual(200, response.status_code)
        self.assertIn("PM10", response.json()["valid_inform_codes"])

    def test_forecast_delegates_query_params(self):
        response = self.client.get(
            "/api/air-quality/forecast",
            params={"inform_code": "O3", "search_date": "2026-07-14", "page_no": 2, "num_of_rows": 20},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(("forecast", "O3", "2026-07-14", 2, 20), self.service.calls[-1])

    def test_weekly_forecast_delegates_query_params(self):
        response = self.client.get(
            "/api/air-quality/pm25-weekly-forecast",
            params={"search_date": "2026-07-14", "page_no": 3, "num_of_rows": 30},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(("weekly", "2026-07-14", 3, 30), self.service.calls[-1])

    def test_station_measurements_delegates_query_params(self):
        response = self.client.get(
            "/api/air-quality/station-measurements",
            params={
                "station_name": "종로구",
                "data_term": "MONTH",
                "page_no": 4,
                "num_of_rows": 40,
                "version": "1.0",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(("station", "종로구", "MONTH", 4, 40, "1.0"), self.service.calls[-1])

    def test_bad_khai_stations_delegates_query_params(self):
        response = self.client.get(
            "/api/air-quality/bad-khai-stations",
            params={"page_no": 5, "num_of_rows": 50},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(("bad-khai", 5, 50), self.service.calls[-1])

    def test_sido_measurements_delegates_query_params(self):
        response = self.client.get(
            "/api/air-quality/sido-measurements",
            params={"sido_name": "수내", "page_no": 2, "num_of_rows": 10, "version": "1.0"},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(("sido", "수내", 2, 10, "1.0"), self.service.calls[-1])

    def test_validation_error_returns_400(self):
        def raise_validation_error(*_, **__):
            raise AirKoreaError("sido_name is not supported")

        with patch("air_korea_mcp.rest_api.get_service") as mock_get_service:
            mock_get_service.return_value.get_sido_measurements.side_effect = raise_validation_error
            response = self.client.get("/api/air-quality/sido-measurements", params={"sido_name": "도쿄"})

        self.assertEqual(400, response.status_code)

    def test_gateway_error_returns_502(self):
        def raise_gateway_error(*_, **__):
            raise AirKoreaGatewayError("Air Korea API request failed")

        with patch("air_korea_mcp.rest_api.get_service") as mock_get_service:
            mock_get_service.return_value.get_sido_measurements.side_effect = raise_gateway_error
            response = self.client.get("/api/air-quality/sido-measurements", params={"sido_name": "서울"})

        self.assertEqual(502, response.status_code)

    def test_configuration_error_returns_503(self):
        with patch("air_korea_mcp.rest_api.get_service", side_effect=AirKoreaConfigurationError("missing key")):
            response = self.client.get("/api/air-quality/sido-measurements", params={"sido_name": "서울"})

        self.assertEqual(503, response.status_code)

    def test_query_validation_rejects_non_positive_page(self):
        response = self.client.get("/api/air-quality/bad-khai-stations", params={"page_no": 0})

        self.assertEqual(422, response.status_code)

    def test_lifespan_initializes_service(self):
        self.get_service.reset_mock()

        with TestClient(create_app()) as client:
            self.assertEqual(200, client.get("/health").status_code)

        self.get_service.assert_called_once_with()

    def test_lifespan_rejects_invalid_server_configuration(self):
        with patch(
            "air_korea_mcp.rest_api.get_service",
            side_effect=AirKoreaConfigurationError("missing key"),
        ):
            with self.assertRaisesRegex(AirKoreaConfigurationError, "missing key"):
                with TestClient(create_app()):
                    pass


if __name__ == "__main__":
    unittest.main()
