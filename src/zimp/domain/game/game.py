from zimp.domain.common.action_result import ActionResult
from zimp.domain.common.action_result_type import ActionResultType
from zimp.domain.common.direction import Direction

from zimp.support.game.game_state_contract_fake import GameStateContract
from zimp.support.game.items_contract_fake import ItemsContract
#from zimp.support.game.actions_contract_fake import ActionsContract
from zimp.support.game.movement_contract_fake import MovementContract

from zimp.domain.common.contract_actions import ActionsContract

class Game:
    """Boundary class connecting the controller to domain components"""

    def __init__(self,
                 state: GameStateContract,
                 actions: ActionsContract,
                 items: ItemsContract,
                 movement: MovementContract
                 ) -> None:
        self._state = state
        self._actions = actions
        self._items = items
        self._movement = movement

        self._setup_actions()

        self.reset()

    def _add_action_result(self, result_type: ActionResultType, function_reference: object) -> None:
        """Add a result type to the action result map"""
        self._action_result_map[result_type] = function_reference

    def _setup_actions(self) -> None:
        """Initialize the action result map"""
        self._action_result_map = {}

        self._add_action_result(ActionResultType.NONE, None)

        self._add_action_result(ActionResultType.ADD_ZOMBIES, self._movement.add_zombies)
        self._add_action_result(ActionResultType.DEFEAT_ZOMBIES, self._defeat_zombies)
        self._add_action_result(ActionResultType.FLEE_ZOMBIES, self._flee_zombies)

        self._add_action_result(ActionResultType.SEARCH_ITEM, self._state.start_search_for_item)
        self._add_action_result(ActionResultType.FOUND_ITEM, self._state.find_item)
        self._add_action_result(ActionResultType.CHANGE_HP, self._state.change_hp)
        self._add_action_result(ActionResultType.FIND_TOTEM, self._take_totem)
        self._add_action_result(ActionResultType.BURY_TOTEM, self._bury_totem)

    # ---------

    def _parse_action_result(self, result: ActionResult) -> None:
        """Execute the corresponding method from the action result map"""
        if result.result_type is ActionResultType.NONE:
            return

        handler = self._action_result_map[result.result_type]
        if result.value is None:
            handler()
        else:
            handler(result.value)

    def _update_stats_from_items(self):
        """Update components when items have changed"""
        items = self._items.get_items()
        self._state.update_stats(items)

    def _flee_zombies(self, hp_change: int) -> None:
        """Update components when zombies are fled"""
        self._state.flee_zombies()
        self._state.change_hp(hp_change)
    def _defeat_zombies(self, hp_change: int) -> None:
        """Update components when zombies are defeated"""
        self._movement.defeat_zombies()
        self._state.change_hp(hp_change)

    def _take_totem(self) -> None:
        """Take the totem"""
        action_result = self._actions.draw_and_resolve_card()
        self._parse_action_result(action_result)
        self._state.take_totem()

    def _bury_totem(self) -> None:
        """Bury the totem"""
        action_result = self._actions.draw_and_resolve_card()
        self._parse_action_result(action_result)
        self._state.bury_totem()

    # --------

    def reset(self) -> None:
        """Reset all game components"""
        self._actions.reset()
        self._movement.reset()
        self._items.reset()
        self._state.reset()

    def move_player(self, direction: Direction) -> None:
        """Attempt to move the player in a given direction"""
        mode = self._state.get_mode()

        self._movement.move_player(mode, direction)

    def rotate_tile(self, direction: Direction) -> None:
        """Rotate the drawn tile in a given direction"""
        mode = self._state.get_mode()

        self._movement.rotate_placement_tile(mode, direction)

    def place_tile(self, direction: Direction) -> None:
        """Attempt to place the drawn tile"""
        mode = self._state.get_mode()

        placed = self._movement.lock_placement_tile(mode, direction)
        if not placed:
            return

        action_result = self._actions.resolve_moved()
        self._parse_action_result(action_result)
        self._state.update_state()

        self._state.check_win_loss(self._actions.is_time_up())

    def pick_zombie_door_attack(self, direction: str) -> None:
        """Trigger a zombie door attack in the selected direction"""
        self._movement.pick_zombie_breakthrough(direction)

    def attack(self) -> None:
        """Fight any zombies on the current tile"""
        num_zombies = self._movement.get_zombie_count()
        attack = self._state.get_attack()

        action_result = self._actions.resolve_attack(num_zombies, attack)
        self._parse_action_result(action_result)

        self._state.check_win_loss(self._actions.is_time_up())

    def flee(self, direction, with_oil: bool) -> None:
        """Flee to a previously explored tile"""
        if not self._movement.can_flee(direction):
            return

        mode = self._state.get_mode()
        num_zombies = self._movement.get_zombie_count()

        action_result = self._actions.resolve_flee(num_zombies, with_oil)
        self._parse_action_result(action_result)
        self._movement.move_player(mode, direction)

        self._state.check_win_loss(self._actions.is_time_up())

    def cower(self) -> None:
        """Hide and cower to regain hp"""
        action_result = self._actions.resolve_cower()
        self._parse_action_result(action_result)

        self._state.check_win_loss(self._actions.is_time_up())

    def end_turn(self) -> None:
        """End the current turn"""
        tile_effect = self._movement.get_tile_effect()

        action_result = self._actions.end_turn(tile_effect)
        self._parse_action_result(action_result)

        self._state.check_win_loss(self._actions.is_time_up())

    def perform_search_for_item(self) -> None:
        """Draw a new card to find an item"""
        action_result = self._actions.search_for_item()
        self._parse_action_result(action_result)

        self._state.check_win_loss(self._actions.is_time_up())

    def ignore_search_for_item(self) -> None:
        """Choose not to draw a card to find an item"""
        self._state.ignore_search_for_item()

    def take_item(self, item_id: int) -> None:
        """Add the found item to the items"""
        self._items.add(item_id)

        self._update_stats_from_items()

    def discard_item(self, slot_id: int) -> None:
        """Discard the chosen item from the items"""
        self._items.discard(slot_id)

        self._update_stats_from_items()

    def use_item(self, item_id) -> None:
        """Use the chosen item"""
        mode = self._state.get_mode()
        self._items.use(mode, item_id)

        self._update_stats_from_items()

