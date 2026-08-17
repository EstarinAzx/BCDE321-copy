from zimp.domain.common.direction import Direction
from zimp.domain.game.game import Game
from zimp.support.game.items_contract_fake import ItemsContract
from zimp.support.game.movement_contract_fake import MovementContract
from zimp.support.game.actions_contract_fake import ActionsContract


class GameController:
    """Thin, testable boundary between Tkinter events and domain behaviour."""

    def __init__(
            self,
            movement: MovementContract,
            items: ItemsContract,
            actions: ActionsContract,
    ) -> None:
        self._game = Game(movement, items, actions)

    def reset(self) -> str:
        result = self._game.reset()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Game reset."

    def move_up(self) -> str:
        result = self._game.move_player(Direction.NORTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Moved up."

    def move_left(self) -> str:
        result = self._game.move_player(Direction.WEST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Moved left."

    def move_right(self) -> str:
        result = self._game.move_player(Direction.EAST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Moved right."

    def move_down(self) -> str:
        result = self._game.move_player(Direction.SOUTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Moved down."

    def rotate_active_tile(self) -> str:
        result = self._game.rotate_tile()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Active tile rotated."

    def place_active_tile(self) -> str:
        result = self._game.place_tile()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Active tile placed."

    def zombie_door_up(self) -> str:
        result = self._game.pick_zombie_door(Direction.NORTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Picked the zombie door above."

    def zombie_door_left(self) -> str:
        result = self._game.pick_zombie_door(Direction.WEST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Picked the zombie door to the left."

    def zombie_door_right(self) -> str:
        result = self._game.pick_zombie_door(Direction.EAST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Picked the zombie door to the right."

    def zombie_door_down(self) -> str:
        result = self._game.pick_zombie_door(Direction.SOUTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Picked the zombie door below."

    def attack(self) -> str:
        result = self._game.attack()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Attacked."

    def attack_with_chainsaw(self) -> str:
        result = self._game.attack(use_chainsaw=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Attacked with the chainsaw."

    def attack_with_candle_fuel(self) -> str:
        result = self._game.attack(instant_kill=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Attacked with candle fuel."

    def flee_up(self) -> str:
        result = self._game.flee(Direction.NORTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled up."

    def flee_left(self) -> str:
        result = self._game.flee(Direction.WEST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled left."

    def flee_right(self) -> str:
        result = self._game.flee(Direction.EAST)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled right."

    def flee_down(self) -> str:
        result = self._game.flee(Direction.SOUTH)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled down."

    def flee_up_with_oil(self) -> str:
        result = self._game.flee(Direction.NORTH, with_oil=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled up using oil."

    def flee_left_with_oil(self) -> str:
        result = self._game.flee(Direction.WEST, with_oil=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled left using oil."

    def flee_right_with_oil(self) -> str:
        result = self._game.flee(Direction.EAST, with_oil=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled right using oil."

    def flee_down_with_oil(self) -> str:
        result = self._game.flee(Direction.SOUTH, with_oil=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Fled down using oil."

    def end_turn(self) -> str:
        result = self._game.end_turn()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Turn ended."

    def cower_and_end_turn(self) -> str:
        result = self._game.end_turn(is_cower=True)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Cowered and ended the turn."

    def search_for_item(self) -> str:
        result = self._game.perform_search_for_item()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Searched for an item."

    def dont_search_for_item(self) -> str:
        result = self._game.ignore_search_for_item()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Did not search for an item."

    def take_found_item(self) -> str:
        result = self._game.take_item()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Took the found item."

    def dont_take_found_item(self) -> str:
        result = self._game.discard_item()
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Discarded the found item."

    def discard_item_1(self) -> str:
        result = self._game.discard_item(0)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Discarded item 1."

    def discard_item_2(self) -> str:
        result = self._game.discard_item(1)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Discarded item 2."

    def use_item_1(self) -> str:
        result = self._game.use_item(0)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Used item 1."

    def use_item_2(self) -> str:
        result = self._game.use_item(1)
        if result is None:
            return "None"
        if result.is_fail():
            return str(result.get_error_code())
        return "Used item 2."