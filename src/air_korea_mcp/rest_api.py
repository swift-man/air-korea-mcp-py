from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from . import __version__
from .bootstrap import create_air_korea_service
from .constants import DATASET_URL
from .exceptions import AirKoreaError, AirKoreaGatewayError
from .reference import build_reference_payload
from .rest_runtime import RestApiRuntimeConfig
from .service import AirKoreaServiceProtocol

DATA_GO_KR_ACCOUNT_VIEW_URL = "https://www.data.go.kr/iim/api/selectAPIAcountView.do"


@lru_cache(maxsize=1)
def get_service() -> AirKoreaServiceProtocol:
    return create_air_korea_service()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Air Korea REST API",
        description="REST API wrapper for Air Korea public OpenAPI data.",
        version=__version__,
    )

    @app.exception_handler(AirKoreaError)
    def handle_air_korea_error(_, exc: AirKoreaError) -> JSONResponse:
        status_code = 502 if isinstance(exc, AirKoreaGatewayError) else 400
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok", "service": "air-korea-rest-api"}

    @app.get("/api/reference", tags=["reference"])
    def reference() -> dict:
        return build_reference_payload()

    @app.get("/api/data-go-kr/account-view", tags=["data.go.kr"])
    def data_go_kr_account_view() -> dict:
        return {
            "url": DATA_GO_KR_ACCOUNT_VIEW_URL,
            "dataset_url": DATASET_URL,
            "integration_type": "portal_account_view",
            "server_to_server_supported": False,
            "reason": (
                "This data.go.kr page redirects to the public data portal login flow. "
                "It requires an interactive user session and is not a service-key OpenAPI endpoint."
            ),
            "recommended_use": (
                "Open the URL in a browser to manage utilization requests, service keys, "
                "traffic limits, and extension/renewal tasks."
            ),
        }

    @app.get("/api/air-quality/forecast", tags=["air-quality"])
    def air_quality_forecast(
        inform_code: str = Query("PM10", description="PM10, PM25, or O3"),
        search_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
        page_no: int = Query(1, ge=1),
        num_of_rows: int = Query(100, ge=1),
    ) -> dict:
        return get_service().get_air_quality_forecast(
            inform_code=inform_code,
            search_date=search_date,
            page_no=page_no,
            num_of_rows=num_of_rows,
        )

    @app.get("/api/air-quality/pm25-weekly-forecast", tags=["air-quality"])
    def pm25_weekly_forecast(
        search_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
        page_no: int = Query(1, ge=1),
        num_of_rows: int = Query(100, ge=1),
    ) -> dict:
        return get_service().get_pm25_weekly_forecast(
            search_date=search_date,
            page_no=page_no,
            num_of_rows=num_of_rows,
        )

    @app.get("/api/air-quality/station-measurements", tags=["air-quality"])
    def station_measurements(
        station_name: str = Query(..., min_length=1),
        data_term: str = Query("DAILY", description="DAILY, MONTH, or 3MONTH"),
        page_no: int = Query(1, ge=1),
        num_of_rows: int = Query(100, ge=1),
        version: str = Query("1.0"),
    ) -> dict:
        return get_service().get_station_measurements(
            station_name=station_name,
            data_term=data_term,
            page_no=page_no,
            num_of_rows=num_of_rows,
            version=version,
        )

    @app.get("/api/air-quality/bad-khai-stations", tags=["air-quality"])
    def bad_khai_stations(
        page_no: int = Query(1, ge=1),
        num_of_rows: int = Query(100, ge=1),
    ) -> dict:
        return get_service().get_bad_khai_stations(
            page_no=page_no,
            num_of_rows=num_of_rows,
        )

    @app.get("/api/air-quality/sido-measurements", tags=["air-quality"])
    def sido_measurements(
        sido_name: str = Query(..., min_length=1, description="서울, 서울시, 우면동, 수내, etc."),
        page_no: int = Query(1, ge=1),
        num_of_rows: int = Query(100, ge=1),
        version: str = Query("1.0"),
    ) -> dict:
        return get_service().get_sido_measurements(
            sido_name=sido_name,
            page_no=page_no,
            num_of_rows=num_of_rows,
            version=version,
        )

    return app


app = create_app()


def main() -> None:
    try:
        config = RestApiRuntimeConfig.from_env()
    except AirKoreaError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise SystemExit("Install FastAPI dependencies before running the REST API.") from exc

    uvicorn.run("air_korea_mcp.rest_api:app", host=config.host, port=config.port)


if __name__ == "__main__":
    main()
