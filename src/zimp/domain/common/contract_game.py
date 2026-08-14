from typing import Protocol
from zimp.domain.common.direction import Direction

class GameContract(Protocol):
    def reset(self) -> None:
        """Reset all game components"""
    def move_player(self, direction: Direction) -> None:
        """Attempt to move the player in a given direction"""
    def rotate_tile(self, direction: Direction) -> None:
        """Rotate the drawn tile in a given direction"""
    def place_tile(self, direction: Direction) -> None:
        """Attempt to place the drawn tile"""
    def pick_zombie_door_attack(self, direction: str) -> None:
        """Trigger a zombie door attack in the selected direction"""
    def attack(self) -> None:
        """Fight any zombies on the current tile"""
    def flee(self, direction, with_oil: bool) -> None:
        """Flee to a previously explored tile"""
    def cower(self) -> None:
        """Hide and cower to regain hp"""
    def end_turn(self) -> None:
        """End the current turn"""
    def perform_search_for_item(self) -> None:
        """Draw a new card to find an item"""
    def ignore_search_for_item(self) -> None:
        """Choose not to draw a card to find an item"""
    def take_item(self, item_id: int) -> None:
        """Add the found item to the items"""
    def discard_item(self, slot_id: int) -> None:
        """Discard the chosen item from the items"""
    def use_item(self, item_id) -> None:
        """Use the chosen item"""