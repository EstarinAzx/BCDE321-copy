from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result

from zimp.domain.common.contract_items import ItemsContract
from zimp.domain.common.contract_movement import MovementContract
from zimp.domain.common.contract_events import EventsContract
from zimp.domain.common.contract_game_state import GameStateContract

from zimp.domain.common.ItemCode import ItemCode


class Game:
    """Boundary class connecting the controller to domain components"""

    def __init__(self,
                 state: GameStateContract,
                 movement: MovementContract,
                 items: ItemsContract,
                 events: EventsContract
                 ) -> None:
        self._state = state
        self._events = events
        self._items = items
        self._movement = movement

        self.reset()

    def _draw_event_card(self) -> Result:
        draw_result, shuffled = self._events.draw_event(self._state.get_time())
        if not draw_result.is_fail():
            self._state.apply_card_effect(draw_result.get_data())
            if shuffled:
                self._state.advance_time()

        return draw_result

    def _do_post_event_checks(self) -> None:
        if self._movement.need_zombie_door():
            self._state.start_zombie_door()

        if self._state.get_has_ended_turn():
            self._state.start_new_turn()

    def reset(self) -> None:
        """Reset all game components"""
        self._state.reset()
        self._events.reset()
        self._movement.reset()
        self._items.reset()

    def move_player(self, direction: Direction) -> Result:
        """Attempt to move the player in a given direction"""
        if not self._state.get_can_move():
            return Result.fail(ErrorCode.CANT_MOVE_NOW)

        move_attempt = self._movement.move(direction)
        if not move_attempt.is_fail():
            self._state.start_move()

        return move_attempt

    def rotate_tile(self) -> Result:
        """Rotate the drawn tile in a given direction"""
        if not self._state.get_is_moving():
            return Result.fail(ErrorCode.CANT_ROTATE_NOW)

        return self._movement.rotate_placement_tile()

    def place_tile(self) -> Result:
        """Attempt to place the drawn tile"""
        if not self._state.get_is_moving():
            return Result.fail(ErrorCode.CANT_PLACE_NOW)

        place_move = self._movement.lock_placement_tile()
        if place_move.is_fail():
            return place_move

        self._state.end_move()

        return self._draw_event_card()

    def pick_zombie_door(self, direction: Direction) -> Result:
        """Trigger a zombie door attack in the selected direction"""
        if not self._state.get_is_zombie_door():
            return Result.fail(ErrorCode.NOT_ZOMBIE_DOOR)

        pick_door = self._movement.pick_zombie_door(direction)
        if not pick_door.is_fail():
            self._state.confirm_zombie_door()

        return pick_door

    def attack(self, use_chainsaw: bool = False, instant_kill:bool = False) -> Result:
        """Fight any zombies on the current tile"""
        if not self._state.get_can_attack():
            return Result.fail(ErrorCode.CANT_ATTACK)

        if instant_kill:
            instant_kill_attempt = self._items.try_use_instant_kill()
            if instant_kill_attempt.is_fail():
                return instant_kill_attempt

        attack_bonus = self._items.attack_bonus(use_chainsaw)

        self._state.attack(attack_bonus, instant_kill)
        self._items.record_battle()

        self._do_post_event_checks()

        return Result.success(None)

    def flee(self, direction: Direction, with_oil: bool = False) -> Result:
        """Flee to a previously explored tile"""
        if not self._state.get_can_flee():
            return Result.fail(ErrorCode.CANT_FLEE)

        if with_oil and not self._items.get_has_oil():
            return Result.fail(ErrorCode.NO_OIL)

        flee_move = self._movement.flee_zombies(direction)
        if flee_move.is_fail():
            return flee_move

        self._state.flee(with_oil)

        if with_oil:
            self._items.use_item(ItemCode.OIL)

        self._do_post_event_checks()
        return Result.success(None)

    def perform_search_for_item(self) -> Result:
        """Draw a new card to find an item"""
        if not self._state.get_is_searching_item():
            return Result.fail(ErrorCode.CANT_SEARCH_NOW)

        draw_result, shuffled = self._events.draw_item()
        if not draw_result.is_fail():
            self._items.find_item(draw_result.get_data())
            self._state.find_item()

            if shuffled:
                self._state.advance_time()

        return draw_result

    def ignore_search_for_item(self) -> Result:
        """Choose not to draw a card to find an item"""
        if not self._state.get_is_searching_item():
            return Result.fail(ErrorCode.CANT_SEARCH_NOW)

        self._state.end_searching_item()

        self._do_post_event_checks()

        return Result.success(None)

    def take_item(self) -> Result:
        """Add the found item to the items"""
        if not self._state.get_has_found_item():
            return Result.fail(ErrorCode.HAVENT_FOUND_ITEM)

        add_item = self._items.keep_found_item() # Should return error if an item hasn't been found or no space
        if add_item.is_fail():
            return add_item

        self._state.end_found_item()

        self._do_post_event_checks()

        return Result.success(None)

    def dont_take_item(self) -> Result:
        if not self._state.get_has_found_item():
            return Result.fail(ErrorCode.HAVENT_FOUND_ITEM)

        self._items.dont_take_item()
        self._state.end_found_item()

        self._do_post_event_checks()

        return Result.success(None)

    def discard_item(self, slot_id: int = -1) -> Result:
        """Discard the chosen item from the items"""
        discard_result = self._items.discard(slot_id)
        if discard_result.is_fail():
            return discard_result

        discarded, shuffled = discard_result.get_data()
        if shuffled:
            self._state.advance_time()

        return discarded

    def use_item(self, item_id: int) -> Result:
        """Use the chosen item (gasoline or soda)"""
        use = self._items.use(item_id)
        if not use.is_fail():
            if item_id == ItemCode.SODA:
                self._state.drink_soda()

        return use

    def end_turn(self, is_cower: bool = False) -> Result:
        """End the current turn, optionally cowering"""
        if not self._state.get_can_end_turn():
            return Result.fail(ErrorCode.CANT_END_TURN_NOW)

        if is_cower:
            cower_action = self._state.cower()
            if cower_action.is_fail():
                return cower_action

            cower_event, shuffled = self._events.waste_time()
            if cower_event.is_fail():
                return cower_event
            if shuffled:
                self._state.advance_time()

        tile_effect = self._movement.get_tile_effect()
        self._state.do_end_turn_effect(tile_effect)

        if self._state.get_is_doing_events():
            return self._draw_event_card()
        else:
            self._state.start_new_turn()
            return Result.success(None)

    def check_win_loss(self) -> Result:
        """To be called after each action; determines if the player has won or lost"""
        if self._state.check_is_won():
            return Result.success("You win!")
        elif self._state.check_is_lost():
            return Result.success("You lose!")

        return Result.fail(ErrorCode.NOT_WON_OR_LOST)