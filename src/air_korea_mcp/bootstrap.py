from __future__ import annotations

from typing import Callable, Optional

from .gateway import AirKoreaGateway, UrllibAirKoreaGateway
from .service import AirKoreaService, AirKoreaServiceProtocol
from .settings import AirKoreaSettings

GatewayFactory = Callable[[AirKoreaSettings], AirKoreaGateway]


def create_gateway(settings: AirKoreaSettings) -> AirKoreaGateway:
    return UrllibAirKoreaGateway(settings=settings)


def create_air_korea_service(
    settings: Optional[AirKoreaSettings] = None,
    gateway_factory: GatewayFactory = create_gateway,
) -> AirKoreaServiceProtocol:
    resolved_settings = settings or AirKoreaSettings.from_env()
    gateway = gateway_factory(resolved_settings)
    return AirKoreaService(gateway=gateway)
