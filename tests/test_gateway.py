import unittest
from http.client import IncompleteRead
from unittest.mock import patch
from urllib.error import HTTPError

from air_korea_mcp.exceptions import AirKoreaGatewayError
from air_korea_mcp.gateway import UrllibAirKoreaGateway, normalize_api_payload
from air_korea_mcp.settings import AirKoreaSettings, ServiceKeyConfig


class InterruptedResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        raise IncompleteRead(b"partial", 100)


class InterruptedFile:
    def read(self):
        raise IncompleteRead(b"partial", 100)

    def close(self):
        pass


class GatewayNormalizationTests(unittest.TestCase):
    def test_request_timeout_raises_gateway_error(self):
        gateway = UrllibAirKoreaGateway(
            settings=AirKoreaSettings(service_key=ServiceKeyConfig(raw_key="test-key"))
        )

        with patch("air_korea_mcp.gateway.request.urlopen", side_effect=TimeoutError):
            with self.assertRaisesRegex(AirKoreaGatewayError, "timed out"):
                gateway.request("getMinuDustFrcstDspth", {})

    def test_interrupted_response_body_raises_gateway_error(self):
        gateway = UrllibAirKoreaGateway(
            settings=AirKoreaSettings(service_key=ServiceKeyConfig(raw_key="test-key"))
        )

        with patch("air_korea_mcp.gateway.request.urlopen", return_value=InterruptedResponse()):
            with self.assertRaisesRegex(AirKoreaGatewayError, "interrupted"):
                gateway.request("getMinuDustFrcstDspth", {})

    def test_interrupted_http_error_body_raises_gateway_error(self):
        gateway = UrllibAirKoreaGateway(
            settings=AirKoreaSettings(service_key=ServiceKeyConfig(raw_key="test-key"))
        )
        http_error = HTTPError(
            url="https://example.com",
            code=502,
            msg="Bad Gateway",
            hdrs=None,
            fp=InterruptedFile(),
        )

        with patch("air_korea_mcp.gateway.request.urlopen", side_effect=http_error):
            with self.assertRaisesRegex(AirKoreaGatewayError, "response body was interrupted"):
                gateway.request("getMinuDustFrcstDspth", {})

    def test_normalize_api_payload_preserves_full_response_fields(self):
        forecast_item = {
            "informCode": "PM10",
            "informData": "2026-04-09",
            "informGrade": "서울 : 보통",
            "imageUrl1": "https://example.com/forecast-1.png",
            "imageUrl2": "https://example.com/forecast-2.png",
        }
        payload = {
            "response": {
                "header": {
                    "resultCode": "00",
                    "resultMsg": "NORMAL SERVICE",
                },
                "body": {
                    "pageNo": 1,
                    "numOfRows": 10,
                    "totalCount": 1,
                    "dataType": "JSON",
                    "items": {
                        "item": forecast_item,
                    },
                },
            }
        }

        result = normalize_api_payload(
            endpoint="getMinuDustFrcstDspth",
            query_params={"returnType": "json", "InformCode": "PM10"},
            status_code=200,
            payload=payload,
        )

        self.assertEqual(payload, result["api_payload"])
        self.assertEqual("00", result["response_header"]["resultCode"])
        self.assertEqual("JSON", result["response_body"]["dataType"])
        self.assertEqual([forecast_item], result["response_body"]["items"])
        self.assertEqual("2026-04-09", result["items"][0]["informData"])
        self.assertEqual("https://example.com/forecast-1.png", result["items"][0]["imageUrl1"])

    def test_non_object_json_raises_gateway_error(self):
        with self.assertRaisesRegex(AirKoreaGatewayError, "not an object"):
            normalize_api_payload(
                endpoint="getMinuDustFrcstDspth",
                query_params={},
                status_code=200,
                payload=[],
            )

    def test_non_object_response_field_raises_gateway_error(self):
        with self.assertRaisesRegex(AirKoreaGatewayError, "response must be an object"):
            normalize_api_payload(
                endpoint="getMinuDustFrcstDspth",
                query_params={},
                status_code=200,
                payload={"response": []},
            )

    def test_non_object_header_and_body_raise_gateway_error(self):
        for field_name in ("header", "body"):
            with self.subTest(field_name=field_name):
                payload = {
                    "response": {
                        "header": {"resultCode": "00"},
                        "body": {},
                    }
                }
                payload["response"][field_name] = []

                with self.assertRaisesRegex(AirKoreaGatewayError, f"response.{field_name}"):
                    normalize_api_payload(
                        endpoint="getMinuDustFrcstDspth",
                        query_params={},
                        status_code=200,
                        payload=payload,
                    )

    def test_missing_required_response_fields_raise_gateway_error(self):
        cases = (
            ({"response": {"body": {}}}, "response.header"),
            ({"response": {"header": {}, "body": {}}}, "resultCode"),
            ({"response": {"header": {"resultCode": "  "}, "body": {}}}, "resultCode"),
            ({"response": {"header": {"resultCode": "00"}}}, "response.body"),
        )

        for payload, expected_message in cases:
            with self.subTest(expected_message=expected_message):
                with self.assertRaisesRegex(AirKoreaGatewayError, expected_message):
                    normalize_api_payload(
                        endpoint="getMinuDustFrcstDspth",
                        query_params={},
                        status_code=200,
                        payload=payload,
                    )

    def test_portal_error_payload_preserves_error_details(self):
        payload = {
            "OpenAPI_ServiceResponse": {
                "cmmMsgHeader": {
                    "returnReasonCode": "30",
                    "returnAuthMsg": "SERVICE KEY IS NOT REGISTERED ERROR",
                    "errMsg": "SERVICE ERROR",
                }
            }
        }

        with self.assertRaisesRegex(AirKoreaGatewayError, "SERVICE KEY IS NOT REGISTERED ERROR"):
            normalize_api_payload(
                endpoint="getMinuDustFrcstDspth",
                query_params={},
                status_code=200,
                payload=payload,
            )

    def test_api_error_result_code_raises_gateway_error(self):
        payload = {
            "response": {
                "header": {"resultCode": "03", "resultMsg": "NO DATA"},
            }
        }

        with self.assertRaisesRegex(AirKoreaGatewayError, "03: NO DATA"):
            normalize_api_payload(
                endpoint="getMinuDustFrcstDspth",
                query_params={},
                status_code=200,
                payload=payload,
            )


if __name__ == "__main__":
    unittest.main()
