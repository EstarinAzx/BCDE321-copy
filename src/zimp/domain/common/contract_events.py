from typing import Protocol, runtime_checkable
from zimp.domain.common.tile_effect import TileEffect
from zimp.support.events.tile_fake import Tile
from zimp.support.events.current_state_fake import CurrentState
from zimp.domain.events.dev_card import CardEffect

@runtime_checkable
class EventsContract(Protocol):
    """Contract used by the application layer to resolve events."""
    def reset(self) -> None:
        """Reset the deck for a new game"""
    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
    def draw_and_resolve_card(self, state: CurrentState, tile: Tile) -> CardEffect:
        """Draw and resolve a new card"""
    def resolve_attack(self, state: CurrentState, tile: Tile) -> None:
        """Conclude combat with zombies in the current room"""
    def resolve_flee(self, state: CurrentState, tile: Tile) -> None:
        """Flee zombies in the current room"""
    def search_for_item(self, state: CurrentState) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""
    def end_turn(self, state: CurrentState, tile_end_effect: TileEffect, tile: Tile) -> CardEffect | None:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""
