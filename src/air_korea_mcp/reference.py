from __future__ import annotations

from typing import Any, Dict

from .constants import API_BASE, DATASET_NAME, DATASET_URL, TOOL_DEFINITIONS, VALID_INFORM_CODES


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
        "tools": [
            {
                "name": tool.name,
                "endpoint": tool.endpoint,
                "description": tool.description,
            }
            for tool in TOOL_DEFINITIONS
        ],
    }
