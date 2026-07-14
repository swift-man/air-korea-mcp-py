import unittest
from unittest.mock import patch

from air_korea_mcp.exceptions import AirKoreaGatewayError
from air_korea_mcp.gateway import UrllibAirKoreaGateway, normalize_api_payload
from air_korea_mcp.settings import AirKoreaSettings, ServiceKeyConfig


class GatewayNormalizationTests(unittest.TestCase):
    def test_request_timeout_raises_gateway_error(self):
        gateway = UrllibAirKoreaGateway(
            settings=AirKoreaSettings(service_key=ServiceKeyConfig(raw_key="test-key"))
        )

        with patch("air_korea_mcp.gateway.request.urlopen", side_effect=TimeoutError):
            with self.assertRaisesRegex(AirKoreaGatewayError, "timed out"):
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
                "body": {},
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
