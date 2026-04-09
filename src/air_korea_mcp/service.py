from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from .constants import DEFAULT_RETURN_TYPE, VALID_DATA_TERMS, VALID_INFORM_CODES
from .gateway import AirKoreaGateway
from .location_resolution import resolve_sido_name
from .validation import require_text, validate_choice, validate_optional_iso_date, validate_positive_int


class AirKoreaServiceProtocol(Protocol):
    def get_air_quality_forecast(
        self,
        inform_code: str = "PM10",
        search_date: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        ...

    def get_pm25_weekly_forecast(
        self,
        search_date: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        ...

    def get_station_measurements(
        self,
        station_name: str,
        data_term: str = "DAILY",
        page_no: int = 1,
        num_of_rows: int = 100,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        ...

    def get_bad_khai_stations(
        self,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        ...

    def get_sido_measurements(
        self,
        sido_name: str,
        page_no: int = 1,
        num_of_rows: int = 100,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class AirKoreaService:
    gateway: AirKoreaGateway

    def get_air_quality_forecast(
        self,
        inform_code: str = "PM10",
        search_date: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        inform_code = inform_code.upper()
        validate_choice("inform_code", inform_code, VALID_INFORM_CODES)
        validate_optional_iso_date("search_date", search_date)
        return self._request_with_paging(
            "getMinuDustFrcstDspth",
            page_no=page_no,
            num_of_rows=num_of_rows,
            params={
                "searchDate": search_date,
                "InformCode": inform_code,
            },
        )

    def get_pm25_weekly_forecast(
        self,
        search_date: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        validate_optional_iso_date("search_date", search_date)
        return self._request_with_paging(
            "getMinuDustWeekFrcstDspth",
            page_no=page_no,
            num_of_rows=num_of_rows,
            params={
                "searchDate": search_date,
            },
        )

    def get_station_measurements(
        self,
        station_name: str,
        data_term: str = "DAILY",
        page_no: int = 1,
        num_of_rows: int = 100,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        normalized_station = require_text("station_name", station_name)
        normalized_data_term = data_term.upper()
        validate_choice("data_term", normalized_data_term, VALID_DATA_TERMS)
        return self._request_with_paging(
            "getMsrstnAcctoRltmMesureDnsty",
            page_no=page_no,
            num_of_rows=num_of_rows,
            params={
                "stationName": normalized_station,
                "dataTerm": normalized_data_term,
                "ver": version,
            },
        )

    def get_bad_khai_stations(
        self,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> Dict[str, Any]:
        return self._request_with_paging(
            "getUnityAirEnvrnIdexSnstiveAboveMsrstnList",
            page_no=page_no,
            num_of_rows=num_of_rows,
            params={},
        )

    def get_sido_measurements(
        self,
        sido_name: str,
        page_no: int = 1,
        num_of_rows: int = 100,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        normalized_sido = resolve_sido_name(require_text("sido_name", sido_name))
        return self._request_with_paging(
            "getCtprvnRltmMesureDnsty",
            page_no=page_no,
            num_of_rows=num_of_rows,
            params={
                "sidoName": normalized_sido,
                "ver": version,
            },
        )

    def _request_with_paging(
        self,
        endpoint: str,
        *,
        page_no: int,
        num_of_rows: int,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        request_params = {
            "returnType": DEFAULT_RETURN_TYPE,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            **params,
        }
        return self.gateway.request(endpoint, request_params)
