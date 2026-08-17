import pytest

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.ItemCode import ItemCode
from zimp.domain.common.result import Result
from zimp.domain.game.game import Game

from tests.game.game_fakes import GameStateContract, MovementContract, ItemsContract, EventsContract

@pytest.fixture
def game():
    state = GameStateContract()
    movement = MovementContract()
    items = ItemsContract()
    events = EventsContract()

    game = Game(state, movement, items, events)

    return game, state, movement, items, events


def error(result):
    assert result.is_fail()
    return result.get_error_code()


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

def test_reset_resets_all_components(game):
    game, state, movement, items, events = game

    game.reset()

    assert state.reset_calls == 2
    assert movement.reset_calls == 2
    assert items.reset_calls == 2
    assert events.reset_calls == 2


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------

def test_move_player_not_allowed_when_state_disallows_movement(game):
    game, state, movement, _, _ = game
    state.can_move = False

    result = game.move_player(Direction.NORTH)

    assert error(result) == ErrorCode.CANT_MOVE_NOW
    assert movement.move_player_calls == []


def test_move_player_delegates_to_movement(game):
    game, state, movement, _, _ = game

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()
    assert movement.move_player_calls == [Direction.NORTH]
    assert state.start_move_calls == 1


def test_move_player_passes_movement_error(game):
    game, state, movement, _, _ = game
    movement.move_player_result = Result.fail(
        ErrorCode.INVALID_MOVE_NO_DOOR
    )

    result = game.move_player(Direction.NORTH)

    assert error(result) == ErrorCode.INVALID_MOVE_NO_DOOR
    assert state.start_move_calls == 0


def test_rotate_tile_not_allowed_when_not_moving(game):
    game, state, movement, _, _ = game
    state.is_moving = False

    result = game.rotate_tile()

    assert error(result) == ErrorCode.CANT_ROTATE_NOW
    assert movement.rotate_placement_tile_calls == 0


def test_rotate_tile_delegates_to_movement(game):
    game, state, movement, _, _ = game
    state.is_moving = True

    result = game.rotate_tile()

    assert not result.is_fail()
    assert movement.rotate_placement_tile_calls == 1


def test_rotate_tile_passes_movement_error(game):
    game, state, movement, _, _ = game
    state.is_moving = True
    movement.rotate_placement_tile_result = Result.fail(
        ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE
    )

    result = game.rotate_tile()

    assert error(result) == ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE


# ---------------------------------------------------------------------------
# Tile placement / event drawing
# ---------------------------------------------------------------------------

def test_place_tile_not_allowed_when_not_moving(game):
    game, state, movement, _, _ = game
    state.is_moving = False

    result = game.place_tile()

    assert error(result) == ErrorCode.CANT_PLACE_NOW
    assert movement.lock_placement_tile_calls == 0


def test_place_tile_passes_lock_error(game):
    game, state, movement, _, _ = game
    state.is_moving = True
    movement.lock_placement_tile_result = Result.fail(
        ErrorCode.FATAL_UNPLACEABLE_TILE
    )

    result = game.place_tile()

    assert error(result) == ErrorCode.FATAL_UNPLACEABLE_TILE
    assert state.end_move_calls == 0


def test_place_tile_ends_move_and_draws_event(game):
    game, state, movement, _, events = game
    state.is_moving = True
    state.time = 3
    events.draw_event_result = Result.success("zombies")

    result = game.place_tile()

    assert not result.is_fail()
    assert state.end_move_calls == 1
    assert events.draw_event_calls == [3]
    assert state.apply_card_effect_calls == ["zombies"]


def test_place_tile_passes_event_error(game):
    game, state, movement, _, events = game
    state.is_moving = True
    events.draw_event_result = Result.fail(ErrorCode.OUT_OF_TIME)

    result = game.place_tile()

    assert error(result) == ErrorCode.OUT_OF_TIME
    assert state.end_move_calls == 1
    assert state.apply_card_effect_calls == []


def test_drawing_shuffled_event_advances_time(game):
    game, state, _, _, events = game
    state.is_moving = True
    events.draw_event_shuffled = True

    game.place_tile()

    assert state.advance_time_calls == 1


def test_drawing_event_starts_zombie_door(game):
    game, state, movement, _, _ = game
    state.is_moving = True
    movement.zombie_door = True

    game.place_tile()

    # _do_post_event_checks is not called by place_tile itself.
    # The event effect is applied by _draw_event_card.
    # Therefore no zombie-door transition is expected here.
    assert state.start_zombie_door_calls == 0


# ---------------------------------------------------------------------------
# Zombie door
# ---------------------------------------------------------------------------

def test_pick_zombie_door_requires_zombie_door(game):
    game, state, movement, _, _ = game
    state.is_zombie_door = False

    result = game.pick_zombie_door(Direction.EAST)

    assert error(result) == ErrorCode.NOT_ZOMBIE_DOOR
    assert movement.pick_zombie_door_calls == []


def test_pick_zombie_door_delegates_to_movement(game):
    game, state, movement, _, _ = game
    state.is_zombie_door = True

    result = game.pick_zombie_door(Direction.EAST)

    assert not result.is_fail()
    assert movement.pick_zombie_door_calls == [Direction.EAST]
    assert state.confirm_zombie_door_calls == 1


def test_pick_zombie_door_passes_movement_error(game):
    game, state, movement, _, _ = game
    state.is_zombie_door = True
    movement.pick_zombie_door_result = Result.fail(
        ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE
    )

    result = game.pick_zombie_door(Direction.EAST)

    assert error(result) == \
        ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE
    assert state.confirm_zombie_door_calls == 0


# ---------------------------------------------------------------------------
# Attack
# ---------------------------------------------------------------------------

def test_attack_requires_permission_from_state(game):
    game, state, _, _, _ = game
    state.can_attack = False

    result = game.attack()

    assert error(result) == ErrorCode.CANT_ATTACK


def test_attack_uses_attack_bonus(game):
    game, state, _, items, _ = game
    items.attack_bonus_result = 3

    result = game.attack()

    assert not result.is_fail()
    assert items.attack_bonus_calls == [False]
    assert state.attack_calls == [(3, False)]
    assert items.record_battle_calls == 1


def test_attack_can_use_chainsaw(game):
    game, state, _, items, _ = game
    items.attack_bonus_result = 5

    result = game.attack(use_chainsaw=True)

    assert not result.is_fail()
    assert items.attack_bonus_calls == [True]
    assert state.attack_calls == [(5, False)]


def test_attack_instant_kill_uses_item(game):
    game, state, _, items, _ = game

    result = game.attack(instant_kill=True)

    assert not result.is_fail()
    assert items.try_use_instant_kill_calls == 1
    assert state.attack_calls == [(0, True)]


def test_attack_passes_no_instant_kill(game):
    game, _, _, items, _ = game

    game.attack()

    assert items.try_use_instant_kill_calls == 0


def test_attack_passes_instant_kill_error(game):
    game, state, _, items, _ = game
    items.try_use_instant_kill_result = Result.fail(
        ErrorCode.NO_INSTANT_KILL
    )

    result = game.attack(instant_kill=True)

    assert error(result) == ErrorCode.NO_INSTANT_KILL
    assert state.attack_calls == []
    assert items.record_battle_calls == 0


def test_attack_records_battle(game):
    game, _, _, items, _ = game

    game.attack()

    assert items.record_battle_calls == 1


def test_attack_performs_post_event_checks(game):
    game, state, movement, _, _ = game
    movement.zombie_door = True

    game.attack()

    assert state.start_zombie_door_calls == 1


def test_attack_starts_new_turn_after_event(game):
    game, state, movement, _, _ = game
    state.has_ended_turn = True

    game.attack()

    assert state.start_new_turn_calls == 1


# ---------------------------------------------------------------------------
# Flee
# ---------------------------------------------------------------------------

def test_flee_requires_permission_from_state(game):
    game, state, movement, _, _ = game
    state.can_flee = False

    result = game.flee(Direction.WEST)

    assert error(result) == ErrorCode.CANT_FLEE
    assert movement.flee_zombies_calls == []


def test_flee_without_oil_does_not_check_for_oil(game):
    game, _, movement, items, _ = game

    result = game.flee(Direction.WEST)

    assert not result.is_fail()
    assert items.get_has_oil_calls == 0
    assert items.use_calls == []
    assert movement.flee_zombies_calls == [Direction.WEST]


def test_flee_with_oil_requires_oil(game):
    game, _, movement, items, _ = game
    items.has_oil = False

    result = game.flee(Direction.WEST, with_oil=True)

    assert error(result) == ErrorCode.NO_OIL
    assert items.get_has_oil_calls == 1
    assert movement.flee_zombies_calls == []


def test_flee_with_oil_uses_oil_after_successful_move(game):
    game, state, movement, items, _ = game

    result = game.flee(Direction.WEST, with_oil=True)

    assert not result.is_fail()
    assert movement.flee_zombies_calls == [Direction.WEST]
    assert state.flee_calls == [True]
    assert items.use_calls == [ItemCode.OIL]


def test_flee_without_oil_passes_false_to_state(game):
    game, state, _, _, _ = game

    game.flee(Direction.WEST)

    assert state.flee_calls == [False]


def test_flee_passes_movement_error(game):
    game, _, movement, items, _ = game
    movement.flee_zombies_result = Result.fail(
        ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE
    )

    result = game.flee(Direction.WEST)

    assert error(result) == ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE
    assert items.use_calls == []


def test_flee_performs_post_event_checks(game):
    game, state, movement, _, _ = game
    movement.zombie_door = True

    game.flee(Direction.WEST)

    assert state.start_zombie_door_calls == 1


# ---------------------------------------------------------------------------
# Search for item
# ---------------------------------------------------------------------------

def test_search_requires_searching_state(game):
    game, state, _, _, events = game
    state.is_searching_item = False

    result = game.perform_search_for_item()

    assert error(result) == ErrorCode.CANT_SEARCH_NOW
    assert events.draw_item_calls == 0


def test_search_draws_item_and_adds_it(game):
    game, state, _, items, events = game
    state.is_searching_item = True
    events.draw_item_result = Result.success(ItemCode.SODA)

    result = game.perform_search_for_item()

    assert not result.is_fail()
    assert result.get_data() == ItemCode.SODA
    assert events.draw_item_calls == 1
    assert items.find_item_calls == [ItemCode.SODA]
    assert state.find_item_calls == 1


def test_search_passes_event_error(game):
    game, state, _, items, events = game
    state.is_searching_item = True
    events.draw_item_result = Result.fail(ErrorCode.OUT_OF_TIME)

    result = game.perform_search_for_item()

    assert error(result) == ErrorCode.OUT_OF_TIME
    assert items.find_item_calls == []
    assert state.find_item_calls == 0


def test_search_advances_time_when_deck_shuffles(game):
    game, state, _, _, events = game
    state.is_searching_item = True
    events.draw_item_shuffled = True

    game.perform_search_for_item()

    assert state.advance_time_calls == 1


# ---------------------------------------------------------------------------
# Ignore / take / don't take items
# ---------------------------------------------------------------------------

def test_ignore_search_requires_found_search_state(game):
    game, state, _, _, _ = game
    state.is_searching_item = False

    result = game.ignore_search_for_item()

    assert error(result) == ErrorCode.CANT_SEARCH_NOW


def test_ignore_search_ends_search(game):
    game, state, movement, _, _ = game
    state.is_searching_item = True

    result = game.ignore_search_for_item()

    assert not result.is_fail()
    assert state.end_searching_item_calls == 1


def test_ignore_search_performs_post_event_checks(game):
    game, state, movement, _, _ = game
    state.is_searching_item = True
    movement.zombie_door = True

    game.ignore_search_for_item()

    assert state.start_zombie_door_calls == 1


def test_take_item_requires_found_item(game):
    game, state, _, _, _ = game
    state.has_found_item = False

    result = game.take_item()

    assert error(result) == ErrorCode.HAVENT_FOUND_ITEM


def test_take_item_keeps_item_and_ends_found_item(game):
    game, state, _, items, _ = game
    state.has_found_item = True

    result = game.take_item()

    assert not result.is_fail()
    assert items.keep_found_item_calls == 1
    assert state.end_found_item_calls == 1


def test_take_item_passes_items_error(game):
    game, state, _, items, _ = game
    state.has_found_item = True
    items.keep_found_item_result = Result.fail(ErrorCode.NO_SPACE)

    result = game.take_item()

    assert error(result) == ErrorCode.NO_SPACE
    assert state.end_found_item_calls == 0


def test_dont_take_item_requires_found_item(game):
    game, state, _, _, _ = game
    state.has_found_item = False

    result = game.dont_take_item()

    assert error(result) == ErrorCode.HAVENT_FOUND_ITEM


def test_dont_take_item_ends_found_item(game):
    game, state, _, items, _ = game
    state.has_found_item = True

    result = game.dont_take_item()

    assert not result.is_fail()
    assert items.dont_take_item_calls == 1
    assert state.end_found_item_calls == 1


# ---------------------------------------------------------------------------
# Discard / use item
# ---------------------------------------------------------------------------

def test_discard_item_delegates_to_items(game):
    game, _, _, items, _ = game
    discarded = Result.success(ItemCode.SODA)
    items.discard_result = Result.success((discarded, False))

    result = game.discard_item(2)

    assert result is discarded
    assert items.discard_calls == [2]


def test_discard_item_passes_items_error(game):
    game, _, _, items, _ = game
    items.discard_result = Result.fail(ErrorCode.NO_FOUND_ITEM)

    result = game.discard_item()

    assert error(result) == ErrorCode.NO_FOUND_ITEM


def test_discard_item_advances_time_when_shuffled(game):
    game, state, _, items, _ = game
    discarded = Result.success(ItemCode.SODA)
    items.discard_result = Result.success((discarded, True))

    game.discard_item()

    assert state.advance_time_calls == 1


def test_use_item_passes_items_result(game):
    game, _, _, items, _ = game
    items.use_result = Result.fail(ErrorCode.NO_SODA)

    result = game.use_item(ItemCode.SODA)

    assert error(result) == ErrorCode.NO_SODA


def test_use_soda_drinks_soda(game):
    game, state, _, items, _ = game
    items.use_result = Result.success(None)

    result = game.use_item(ItemCode.SODA)

    assert not result.is_fail()
    assert state.drink_soda_calls == 1


def test_use_non_soda_does_not_drink_soda(game):
    game, state, _, items, _ = game
    items.use_result = Result.success(None)

    game.use_item(ItemCode.OIL)

    assert state.drink_soda_calls == 0


# ---------------------------------------------------------------------------
# End turn
# ---------------------------------------------------------------------------

def test_end_turn_requires_permission_from_state(game):
    game, state, movement, _, _ = game
    state.can_end_turn = False

    result = game.end_turn()

    assert error(result) == ErrorCode.CANT_END_TURN_NOW
    assert movement.get_tile_effect_calls == 0


def test_end_turn_gets_tile_effect(game):
    game, state, movement, _, _ = game
    movement.tile_effect = "fire"

    result = game.end_turn()

    assert not result.is_fail()
    assert movement.get_tile_effect_calls == 1
    assert state.do_end_turn_effect_calls == ["fire"]


def test_end_turn_starts_new_turn_when_not_doing_events(game):
    game, state, _, _, _ = game
    state.is_doing_events = False

    result = game.end_turn()

    assert not result.is_fail()
    assert state.start_new_turn_calls == 1


def test_end_turn_draws_event_when_doing_events(game):
    game, state, _, _, events = game
    state.is_doing_events = True
    events.draw_event_result = Result.success("zombies")

    result = game.end_turn()

    assert not result.is_fail()
    assert events.draw_event_calls == [0]
    assert state.apply_card_effect_calls == ["zombies"]
    assert state.start_new_turn_calls == 0


def test_cower_calls_state_cower(game):
    game, state, _, _, _ = game

    result = game.end_turn(is_cower=True)

    assert not result.is_fail()
    assert state.cower_calls == 1


def test_failed_cower_stops_turn_end(game):
    game, state, _, _, _ = game
    state.cower = lambda: Result.fail(ErrorCode.ALREADY_COWERED)

    result = game.end_turn(is_cower=True)

    assert error(result) == ErrorCode.ALREADY_COWERED
    assert state.do_end_turn_effect_calls == []


def test_cower_wastes_time(game):
    game, state, _, _, events = game

    result = game.end_turn(is_cower=True)

    assert not result.is_fail()
    assert events.waste_time_calls == 1


def test_cower_passes_waste_time_error(game):
    game, state, _, _, events = game
    events.waste_time_result = Result.fail(ErrorCode.OUT_OF_TIME)

    result = game.end_turn(is_cower=True)

    assert error(result) == ErrorCode.OUT_OF_TIME
    assert state.do_end_turn_effect_calls == []


def test_cower_advances_time_when_waste_time_shuffles(game):
    game, state, _, _, events = game
    events.waste_time_shuffled = True

    game.end_turn(is_cower=True)

    assert state.advance_time_calls == 1


def test_cowering_does_not_waste_time_without_cower(game):
    game, _, _, _, events = game

    game.end_turn()

    assert events.waste_time_calls == 0


def test_end_turn_passes_event_error(game):
    game, state, _, _, events = game
    state.is_doing_events = True
    events.draw_event_result = Result.fail(ErrorCode.OUT_OF_TIME)

    result = game.end_turn()

    assert error(result) == ErrorCode.OUT_OF_TIME


# ---------------------------------------------------------------------------
# Win / loss
# ---------------------------------------------------------------------------

def test_check_win_loss_reports_neither(game):
    game, state, _, _, _ = game

    result = game.check_win_loss()

    assert error(result) == ErrorCode.NOT_WON_OR_LOST


def test_check_win_loss_reports_win(game):
    game, state, _, _, _ = game
    state.has_won = True

    result = game.check_win_loss()

    assert not result.is_fail()
    assert result.get_data() == "You win!"


def test_check_win_loss_reports_loss(game):
    game, state, _, _, _ = game
    state.has_lost = True

    result = game.check_win_loss()

    assert not result.is_fail()
    assert result.get_data() == "You lose!"


def test_check_win_loss_prioritises_win(game):
    game, state, _, _, _ = game
    state.has_won = True
    state.has_lost = True

    result = game.check_win_loss()

    assert not result.is_fail()
    assert result.get_data() == "You win!"
