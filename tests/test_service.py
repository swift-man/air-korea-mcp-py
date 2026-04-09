import unittest

from air_korea_mcp.exceptions import AirKoreaError
from air_korea_mcp.reference import build_reference_payload
from air_korea_mcp.service import AirKoreaService


class FakeGateway:
    def __init__(self):
        self.calls = []

    def request(self, endpoint, params):
        self.calls.append((endpoint, params))
        return {"endpoint": endpoint, "request_params": params, "items": []}


class AirKoreaServiceTests(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeGateway()
        self.service = AirKoreaService(gateway=self.gateway)

    def test_get_sido_measurements_delegates_to_gateway(self):
        result = self.service.get_sido_measurements("서울", page_no=2, num_of_rows=10, version="1.0")

        self.assertEqual("getCtprvnRltmMesureDnsty", result["endpoint"])
        self.assertEqual(
            {
                "returnType": "json",
                "pageNo": 2,
                "numOfRows": 10,
                "sidoName": "서울",
                "ver": "1.0",
            },
            result["request_params"],
        )

    def test_get_sido_measurements_resolves_unique_lower_level_location(self):
        result = self.service.get_sido_measurements("우면동", page_no=1, num_of_rows=5, version="1.0")

        self.assertEqual("서울", result["request_params"]["sidoName"])

    def test_get_sido_measurements_rejects_ambiguous_lower_level_location(self):
        with self.assertRaises(AirKoreaError) as context:
            self.service.get_sido_measurements("삼성동")

        self.assertIn("ambiguous", str(context.exception))

    def test_get_station_measurements_rejects_blank_station_name(self):
        with self.assertRaises(AirKoreaError):
            self.service.get_station_measurements("   ")

    def test_get_air_quality_forecast_normalizes_inform_code(self):
        self.service.get_air_quality_forecast(inform_code="pm10")

        endpoint, params = self.gateway.calls[-1]
        self.assertEqual("getMinuDustFrcstDspth", endpoint)
        self.assertEqual("PM10", params["InformCode"])

    def test_reference_payload_lists_all_tools(self):
        payload = build_reference_payload()

        self.assertEqual("한국환경공단_에어코리아_대기오염정보", payload["dataset"])
        self.assertEqual(5, len(payload["tools"]))


if __name__ == "__main__":
    unittest.main()
