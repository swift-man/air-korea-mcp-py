class AirKoreaError(RuntimeError):
    """Base exception for Air Korea wrapper errors."""


class AirKoreaConfigurationError(AirKoreaError):
    """Raised when server configuration is missing or invalid."""


class AirKoreaGatewayError(AirKoreaError):
    """Raised when the upstream Air Korea API cannot return usable data."""
