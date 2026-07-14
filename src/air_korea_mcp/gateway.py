from __future__ import annotations

import json
from dataclasses import dataclass
from http import client as http_client
from typing import Any, Dict, List, Mapping, Optional, Protocol
from urllib import error, parse, request

from .constants import DATASET_NAME, DATASET_URL
from .exceptions import AirKoreaGatewayError
from .settings import AirKoreaSettings


class AirKoreaGateway(Protocol):
    def request(self, endpoint: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        """Fetch JSON data from the Air Korea API."""


@dataclass(frozen=True)
class UrllibAirKoreaGateway:
    settings: AirKoreaSettings
    user_agent: str = "air-korea-mcp/0.1.0"

    def request(self, endpoint: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        query_params = {key: value for key, value in params.items() if value is not None}
        url = f"{self.settings.api_base}/{endpoint}?{self._build_query(query_params)}"
        http_request = request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
        )

        try:
            with request.urlopen(http_request, timeout=self.settings.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8", "replace")
                status_code = response.status
        except error.HTTPError as exc:
            try:
                raw_body = exc.read().decode("utf-8", "replace")
            except (http_client.HTTPException, OSError) as read_exc:
                raise AirKoreaGatewayError(
                    f"Air Korea API returned HTTP {exc.code}, but its response body was interrupted."
                ) from read_exc
            message = raw_body.strip() or exc.reason
            raise AirKoreaGatewayError(f"Air Korea API returned HTTP {exc.code}: {message}") from exc
        except error.URLError as exc:
            raise AirKoreaGatewayError(f"Air Korea API request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise AirKoreaGatewayError("Air Korea API request timed out.") from exc
        except http_client.HTTPException as exc:
            raise AirKoreaGatewayError("Air Korea API response was interrupted.") from exc
        except OSError as exc:
            raise AirKoreaGatewayError(f"Air Korea API connection failed: {exc}") from exc

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AirKoreaGatewayError("Expected JSON from Air Korea API but received a different payload.") from exc

        return normalize_api_payload(endpoint=endpoint, query_params=query_params, status_code=status_code, payload=payload)

    def _build_query(self, params: Mapping[str, Any]) -> str:
        segments = [self.settings.service_key.to_query_segment()]
        for key, value in params.items():
            encoded_key = parse.quote(str(key), safe="")
            encoded_value = parse.quote(str(value), safe="")
            segments.append(f"{encoded_key}={encoded_value}")
        return "&".join(segments)


def normalize_api_payload(
    endpoint: str,
    query_params: Mapping[str, Any],
    status_code: int,
    payload: Any,
) -> Dict[str, Any]:
    plain_payload = to_plain_data(payload)
    if not isinstance(plain_payload, Mapping):
        raise AirKoreaGatewayError("Air Korea API returned JSON that is not an object.")

    response_value = plain_payload.get("response")
    if response_value is None:
        portal_error = extract_portal_error(plain_payload)
        if portal_error:
            raise AirKoreaGatewayError(f"Air Korea API error: {portal_error}")
        raise AirKoreaGatewayError("Air Korea API response did not contain a response object.")

    response = require_mapping("response", response_value)
    if "header" not in response:
        raise AirKoreaGatewayError("Air Korea API response did not contain response.header.")
    header = require_mapping("response.header", response["header"])

    result_code_value = header.get("resultCode")
    if result_code_value is None or not str(result_code_value).strip():
        raise AirKoreaGatewayError("Air Korea API response.header did not contain resultCode.")
    result_code = str(result_code_value).strip()
    result_message = str(header.get("resultMsg", ""))
    if result_code != "00":
        raise AirKoreaGatewayError(f"Air Korea API error {result_code}: {result_message}")

    if "body" not in response:
        raise AirKoreaGatewayError("Air Korea API success response did not contain response.body.")
    body = require_mapping("response.body", response["body"])

    normalized_body = normalize_response_body(body)

    return {
        "dataset": DATASET_NAME,
        "dataset_url": DATASET_URL,
        "endpoint": endpoint,
        "http_status": status_code,
        "request_params": dict(query_params),
        "api_payload": plain_payload,
        "result": {
            "code": result_code,
            "message": result_message or None,
        },
        "response_header": header,
        "response_body": normalized_body,
        "page_no": normalized_body.get("pageNo"),
        "num_of_rows": normalized_body.get("numOfRows"),
        "total_count": normalized_body.get("totalCount"),
        "items": normalized_body.get("items", []),
    }


def require_mapping(field_name: str, value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AirKoreaGatewayError(f"Air Korea API field {field_name} must be an object.")
    return value


def extract_portal_error(payload: Mapping[str, Any]) -> Optional[str]:
    service_response = payload.get("OpenAPI_ServiceResponse", payload)
    if not isinstance(service_response, Mapping):
        return None

    header = service_response.get("cmmMsgHeader")
    if not isinstance(header, Mapping):
        return None

    details = [
        str(header[key]).strip()
        for key in ("returnReasonCode", "returnAuthMsg", "errMsg")
        if header.get(key) not in (None, "")
    ]
    return ": ".join(details) or None


def normalize_items(items: Any) -> List[Any]:
    if items in (None, "", {}):
        return []
    if isinstance(items, list):
        return items
    if isinstance(items, dict):
        if "item" in items:
            nested = items["item"]
            if isinstance(nested, list):
                return nested
            if nested in (None, "", {}):
                return []
            return [nested]
        return [items]
    return [items]


def normalize_response_body(body: Mapping[str, Any]) -> Dict[str, Any]:
    normalized_body = dict(body)
    normalized_body["items"] = normalize_items(body.get("items"))
    return normalized_body


def to_plain_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: to_plain_data(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    return value
