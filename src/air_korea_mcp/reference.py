from __future__ import annotations

from typing import Any, Dict

from .constants import API_BASE, DATASET_NAME, DATASET_URL, TOOL_DEFINITIONS, VALID_INFORM_CODES
from .location_resolution import SIDO_ALIAS_MAP


def build_reference_payload() -> Dict[str, Any]:
    return {
        "dataset": DATASET_NAME,
        "dataset_url": DATASET_URL,
        "api_base": API_BASE,
        "valid_inform_codes": sorted(VALID_INFORM_CODES),
        "valid_data_terms": ["DAILY", "MONTH", "3MONTH"],
        "valid_sido_names": [
            "전국",
            "서울",
            "부산",
            "대구",
            "인천",
            "광주",
            "대전",
            "울산",
            "경기",
            "강원",
            "충북",
            "충남",
            "전북",
            "전남",
            "경북",
            "경남",
            "제주",
            "세종",
        ],
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
            "known_sido_alias_count": len(SIDO_ALIAS_MAP),
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
