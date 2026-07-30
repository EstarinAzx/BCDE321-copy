class FakeMovementGateway:
    """Controllable fake for boundary and contract testing."""

    def __init__(self, response: str = "Move accepted.") -> None:
        self.response = response
        self.calls: list[str] = []
        self.failure: Exception | None = None

    def move(self, direction: str) -> str:
        self.calls.append(direction)
        if self.failure is not None:
            raise self.failure
        return self.response
