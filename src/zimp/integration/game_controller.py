from zimp.domain.contracts import MovementGateway
from zimp.domain.events.contracts_events import EventsContract

class GameController:
    """Thin, testable boundary between Tkinter events and domain behaviour."""

    def __init__(self, movement: MovementGateway, events: EventsContract) -> None:
        self._movement = movement
        self._events = events

    def handle_move(self, direction: str) -> str:
        try:
            return self._movement.move(direction)
        except ValueError as error:
            return f"Cannot move: {error}"
        except RuntimeError:
            return "Cannot move: the movement component is currently unavailable."
