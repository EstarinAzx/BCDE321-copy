from typing import Protocol, runtime_checkable
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.common.result import Result

@runtime_checkable
class ActionsContract(Protocol):
    """Contract used by the application layer to resolve actions."""
    def reset(self) -> Result:
        """Reset the deck for a new game"""
    def is_time_up(self) -> bool:
        """Returns whether it is past midnight"""
    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
    def draw_and_resolve_card(self) -> Result:
        """Draw and resolve a new card"""
    def resolve_attack(self, zombie_count: int, attack: int) -> Result:
        """What occurs when the player has attempted to attack zombies"""
    def resolve_moved(self) -> Result:
        """What occurs when the player has successfully moved to a different room"""
    def resolve_flee(self, zombie_count: int, take_damage: bool) -> Result:
        """What occurs when the player has attempted to flee zombies"""
    def resolve_cower(self) -> Result:
        """What occurs when the player has attempted to cower"""
    def search_for_item(self) -> Result:
        """After an event has found an item, draw the next card to see what it is and return its id."""
    def end_turn(self, effect: TileEffect) -> Result:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""