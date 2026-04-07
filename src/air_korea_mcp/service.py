from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from .constants import DEFAULT_RETURN_TYPE, VALID_DATA_TERMS, VALID_INFORM_CODES, VALID_SIDO_NAMES
from .gateway import AirKoreaGateway, UrllibAirKoreaGateway
from .settings import AirKoreaSettings
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

    @classmethod
    def from_env(cls) -> "AirKoreaService":
        settings = AirKoreaSettings.from_env()
        return cls(gateway=UrllibAirKoreaGateway(settings=settings))

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
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            "getMinuDustFrcstDspth",
            {
                "returnType": DEFAULT_RETURN_TYPE,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
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
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            "getMinuDustWeekFrcstDspth",
            {
                "returnType": DEFAULT_RETURN_TYPE,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
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
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            "getMsrstnAcctoRltmMesureDnsty",
            {
                "returnType": DEFAULT_RETURN_TYPE,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
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
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            "getUnityAirEnvrnIdexSnstiveAboveMsrstnList",
            {
                "returnType": DEFAULT_RETURN_TYPE,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )

    def get_sido_measurements(
        self,
        sido_name: str,
        page_no: int = 1,
        num_of_rows: int = 100,
        version: str = "1.0",
    ) -> Dict[str, Any]:
        normalized_sido = require_text("sido_name", sido_name)
        validate_choice("sido_name", normalized_sido, VALID_SIDO_NAMES)
        validate_positive_int("page_no", page_no)
        validate_positive_int("num_of_rows", num_of_rows)
        return self.gateway.request(
            "getCtprvnRltmMesureDnsty",
            {
                "returnType": DEFAULT_RETURN_TYPE,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
                "sidoName": normalized_sido,
                "ver": version,
            },
        )
