from typing import Protocol, runtime_checkable
from zimp.domain.enums import EndTurnEffects
from zimp.domain.event_handler import DevCard
from zimp.domain.current_state import CurrentState

@runtime_checkable
class EventsContract(Protocol):
    """Contract used by the application layer to trigger events."""

    def shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""

    def draw_card(self, state: CurrentState) -> DevCard | None:
        """Draw a dev card from the deck and return it"""

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""

    def resolve_card(self, state: CurrentState) -> int:
        """Draw and resolve a new card, then return the number of zombies to spawn"""

    def resolve_attack(self, state: CurrentState, num_zombies: int) -> None:
        """Conclude combat with zombies in the current room"""

    def resolve_flee(self, state: CurrentState) -> None:
        """Flee zombies in the current room"""

    def search_for_item(self, state: CurrentState) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""

    def end_turn(self, state: CurrentState, tile_end_effect: EndTurnEffects) -> int:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""