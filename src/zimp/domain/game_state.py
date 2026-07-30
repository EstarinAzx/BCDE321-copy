from dataclasses import dataclass


@dataclass
class GameState:
    """Deliberately small tutor example, not a completed game engine."""

    last_move: str | None = None
    turn_number: int = 0
