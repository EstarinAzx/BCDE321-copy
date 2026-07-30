import pytest

from zimp.domain.basic_movement import BasicMovement
from zimp.domain.game_state import GameState


def test_valid_move_updates_state_and_returns_status() -> None:
    state = GameState()
    movement = BasicMovement(state)

    assert movement.move("North") == "Moved north. Turn 1."
    assert state.last_move == "north"
    assert state.turn_number == 1


def test_invalid_move_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unsupported direction"):
        BasicMovement(GameState()).move("up")


@pytest.mark.parametrize("direction", ["north", "south", "east", "west"])
def test_each_supported_direction(direction: str) -> None:
    assert BasicMovement(GameState()).move(direction).startswith(f"Moved {direction}.")
