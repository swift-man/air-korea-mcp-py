from __future__ import annotations

from dataclasses import dataclass

API_BASE = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
DATASET_NAME = "한국환경공단_에어코리아_대기오염정보"
DATASET_URL = "https://www.data.go.kr/data/15073861/openapi.do"
DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_RETURN_TYPE = "json"

VALID_DATA_TERMS = {"DAILY", "MONTH", "3MONTH"}
VALID_INFORM_CODES = {"PM10", "PM25", "O3"}
VALID_SIDO_NAMES = {
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
}


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    endpoint: str
    description: str


TOOL_DEFINITIONS = (
    ToolDefinition(
        name="get_air_quality_forecast",
        endpoint="getMinuDustFrcstDspth",
        description="대기질 예보통보 조회",
    ),
    ToolDefinition(
        name="get_pm25_weekly_forecast",
        endpoint="getMinuDustWeekFrcstDspth",
        description="초미세먼지 주간예보 조회",
    ),
    ToolDefinition(
        name="get_station_measurements",
        endpoint="getMsrstnAcctoRltmMesureDnsty",
        description="측정소별 실시간 측정정보 조회",
    ),
    ToolDefinition(
        name="get_bad_khai_stations",
        endpoint="getUnityAirEnvrnIdexSnstiveAboveMsrstnList",
        description="통합대기환경지수 나쁨 이상 측정소 목록조회",
    ),
    ToolDefinition(
        name="get_sido_measurements",
        endpoint="getCtprvnRltmMesureDnsty",
        description="시도별 실시간 측정정보 조회",
    ),
)
