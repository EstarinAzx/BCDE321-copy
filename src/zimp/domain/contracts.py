from typing import Protocol, runtime_checkable
from zimp.domain.enums import Mode

@runtime_checkable
class MovementGateway(Protocol):
    """Contract used by the application layer to request movement.

    Student work may implement this contract or consume it at an assessed
    integration boundary. Do not couple implementations to Tkinter widgets.
    """

    def move(self, direction: str) -> str:
        """Apply a movement command and return a user-facing status message."""

@runtime_checkable
class EventsContract(Protocol):
    """Contract used by the application layer to trigger events."""
    def shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
    def draw_card(self, state, tile) -> None:
        """Draw a dev card from the deck"""
    def resolve_attack(self, state, tile) -> None:
        """Conclude combat with zombies in the current room"""
    def resolve_flee(self, state) -> None:
        """Flee zombies in the current room"""
    def search_for_item(self, state) -> int:
        """After an event has found an item, draw the next card to see what it is and return its id."""
    def end_turn(self, state, tile)  -> None:
        """Conclude the current turn"""