from __future__ import annotations

from functools import lru_cache
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .bootstrap import create_air_korea_service
from .exceptions import AirKoreaError
from .reference import build_reference_payload
from .runtime import RuntimeConfig, apply_runtime_config
from .service import AirKoreaServiceProtocol

mcp = FastMCP("Air Korea", stateless_http=True, json_response=True)


@lru_cache(maxsize=1)
def get_service() -> AirKoreaServiceProtocol:
    return create_air_korea_service()


@mcp.resource("airkorea://reference")
def reference() -> dict:
    """Reference data for valid options and endpoint mapping."""
    return build_reference_payload()


@mcp.tool()
def get_air_quality_forecast(
    inform_code: str = "PM10",
    search_date: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict:
    """Get Air Korea forecast notices for PM10, PM2.5, or O3."""
    return get_service().get_air_quality_forecast(
        inform_code=inform_code,
        search_date=search_date,
        page_no=page_no,
        num_of_rows=num_of_rows,
    )


@mcp.tool()
def get_pm25_weekly_forecast(
    search_date: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict:
    """Get the weekly PM2.5 forecast bulletin."""
    return get_service().get_pm25_weekly_forecast(
        search_date=search_date,
        page_no=page_no,
        num_of_rows=num_of_rows,
    )


@mcp.tool()
def get_station_measurements(
    station_name: str,
    data_term: str = "DAILY",
    page_no: int = 1,
    num_of_rows: int = 100,
    version: str = "1.0",
) -> dict:
    """Get real-time measurements for a station."""
    return get_service().get_station_measurements(
        station_name=station_name,
        data_term=data_term,
        page_no=page_no,
        num_of_rows=num_of_rows,
        version=version,
    )


@mcp.tool()
def get_bad_khai_stations(
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict:
    """List stations where the integrated air quality index is bad or worse."""
    return get_service().get_bad_khai_stations(
        page_no=page_no,
        num_of_rows=num_of_rows,
    )


@mcp.tool()
def get_sido_measurements(
    sido_name: str,
    page_no: int = 1,
    num_of_rows: int = 100,
    version: str = "1.0",
) -> dict:
    """Get real-time measurements for a 시도 or a uniquely resolvable lower-level location."""
    return get_service().get_sido_measurements(
        sido_name=sido_name,
        page_no=page_no,
        num_of_rows=num_of_rows,
        version=version,
    )


def main() -> None:
    try:
        runtime_config = RuntimeConfig.from_env()
        apply_runtime_config(mcp, runtime_config)
        mcp.run(transport="streamable-http")
    except AirKoreaError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
