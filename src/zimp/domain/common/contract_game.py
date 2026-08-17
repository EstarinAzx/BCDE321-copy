from typing import Protocol
from zimp.domain.common.direction import Direction
from zimp.domain.common.result import Result


class GameContract(Protocol):
    def reset(self) -> Result:
        """Restart the game"""
    def move_player(self, direction: Direction) -> Result:
        """Attempt to move the player in a given direction"""
    def rotate_tile(self) -> Result:
        """Rotate the drawn tile in a given direction"""
    def place_tile(self) -> Result:
        """Attempt to place the drawn tile"""
    def pick_zombie_door(self, direction: Direction) -> Result:
        """Trigger a zombie door attack in the selected direction"""
    def attack(self, use_chainsaw: bool = False, instant_kill: bool = False) -> Result:
        """Fight any zombies on the current tile"""
    def flee(self, direction: Direction, with_oil: bool = False) -> Result:
        """Flee to a previously explored tile"""
    def end_turn(self, is_cower: bool) -> Result:
        """End the current turn, optionally cowering"""
    def perform_search_for_item(self) -> Result:
        """Draw a new card to find an item"""
    def ignore_search_for_item(self) -> Result:
        """Choose not to draw a card to find an item"""
    def take_item(self) -> Result:
        """Add the found item to the items"""
    def discard_item(self, item_id: int = -1) -> Result:
        """Discard the chosen item from the items"""
    def use_item(self, item_id: int) -> Result:
        """Use the chosen item"""
    def check_win_loss(self) -> Result:
        """To be called after each action; determines if the player has won or lost"""