from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Protocol
from urllib import error, parse, request

from .constants import DATASET_NAME, DATASET_URL
from .exceptions import AirKoreaError
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
            raw_body = exc.read().decode("utf-8", "replace")
            message = raw_body.strip() or exc.reason
            raise AirKoreaError(f"Air Korea API returned HTTP {exc.code}: {message}") from exc
        except error.URLError as exc:
            raise AirKoreaError(f"Air Korea API request failed: {exc.reason}") from exc

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AirKoreaError("Expected JSON from Air Korea API but received a different payload.") from exc

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
    payload: Mapping[str, Any],
) -> Dict[str, Any]:
    plain_payload = to_plain_data(payload)
    response = plain_payload.get("response", {})
    header = response.get("header", {}) or {}
    body = response.get("body", {}) or {}

    result_code = str(header.get("resultCode", ""))
    result_message = str(header.get("resultMsg", ""))
    if result_code and result_code != "00":
        raise AirKoreaError(f"Air Korea API error {result_code}: {result_message}")

    normalized_body = normalize_response_body(body)

    return {
        "dataset": DATASET_NAME,
        "dataset_url": DATASET_URL,
        "endpoint": endpoint,
        "http_status": status_code,
        "request_params": dict(query_params),
        "api_payload": plain_payload,
        "result": {
            "code": result_code or None,
            "message": result_message or None,
        },
        "response_header": header,
        "response_body": normalized_body,
        "page_no": normalized_body.get("pageNo"),
        "num_of_rows": normalized_body.get("numOfRows"),
        "total_count": normalized_body.get("totalCount"),
        "items": normalized_body.get("items", []),
    }


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
