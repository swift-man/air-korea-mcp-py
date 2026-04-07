import unittest

from air_korea_mcp.bootstrap import create_air_korea_service
from air_korea_mcp.service import AirKoreaService
from air_korea_mcp.settings import AirKoreaSettings, ServiceKeyConfig


class FakeGateway:
    def request(self, endpoint, params):
        return {"endpoint": endpoint, "request_params": params, "items": []}


class BootstrapTests(unittest.TestCase):
    def test_create_air_korea_service_uses_injected_gateway_factory(self):
        settings = AirKoreaSettings(
            service_key=ServiceKeyConfig(raw_key="test-key"),
            api_base="https://example.com",
            timeout_seconds=3.0,
        )

        service = create_air_korea_service(settings=settings, gateway_factory=lambda _: FakeGateway())

        self.assertIsInstance(service, AirKoreaService)
        self.assertIsInstance(service.gateway, FakeGateway)


if __name__ == "__main__":
    unittest.main()
