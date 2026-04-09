import unittest

from air_korea_mcp.gateway import normalize_api_payload


class GatewayNormalizationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
