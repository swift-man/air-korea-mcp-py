from __future__ import annotations

from typing import Any, Dict

from .constants import (
    API_BASE,
    DATASET_NAME,
    DATASET_URL,
    TOOL_DEFINITIONS,
    VALID_DATA_TERM_OPTIONS,
    VALID_INFORM_CODES,
    VALID_SIDO_NAME_OPTIONS,
)
from .location_resolution import SIDO_ALIAS_MAP, SUPPORTED_LOCATION_EXAMPLES


def build_reference_payload() -> Dict[str, Any]:
    return {
        "dataset": DATASET_NAME,
        "dataset_url": DATASET_URL,
        "api_base": API_BASE,
        "valid_inform_codes": sorted(VALID_INFORM_CODES),
        "valid_data_terms": list(VALID_DATA_TERM_OPTIONS),
        "valid_sido_names": list(VALID_SIDO_NAME_OPTIONS),
        "sido_alias_examples": {
            "서울특별시": "서울",
            "경기도": "경기",
            "우면동": "서울",
            "서초구 우면동": "서울",
        },
        "location_resolution": {
            "supports_sido_aliases": True,
            "supports_unique_lower_level_locations": True,
            "ambiguous_lower_level_locations_raise_error": True,
            "ambiguous_lower_level_locations_include_clarifying_examples": True,
            "known_sido_alias_count": len(SIDO_ALIAS_MAP),
            "supported_location_examples": list(SUPPORTED_LOCATION_EXAMPLES),
            "unsupported_location_note": "Air Korea regional queries support South Korea regions only.",
        },
        "tools": [
            {
                "name": tool.name,
                "endpoint": tool.endpoint,
                "description": tool.description,
            }
            for tool in TOOL_DEFINITIONS
        ],
    }
