class AirKoreaError(RuntimeError):
    """Base exception for Air Korea wrapper errors."""


class AirKoreaGatewayError(AirKoreaError):
    """Raised when the upstream Air Korea API cannot return usable data."""
