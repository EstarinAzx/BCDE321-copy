import pytest

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.game.game import Game

from zimp.domain.game_state.game_state import GameState
from zimp.domain.events.events import Events
from zimp.domain.items.items import Items
from zimp.domain.movement.movement import Movement

@pytest.fixture
def game():
    state = GameState()
    movement = Movement()
    items = Items()
    events = Events()

    game = Game(state, movement, items, events)

    return game, state, movement, items, events

# Reset
def test_reset_resets_all_components(game):
    game, state, movement, items, actions = game

    # TODO modify all 4 components

    game.reset()

    # TODO assert all 4 components are in reset state

# move_player
def test_move_is_allowed_at_start(game):
    game, _, _, _, _ = game

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

def test_move_success_doesnt_allow_another_move(game):
    game, _, _, _, _ = game
    game.move_player(Direction.NORTH)

    result = game.move_player(Direction.SOUTH)

    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

def test_can_only_move_north_at_start(game):
    game, _, _, _, _ = game

    result = game.move_player(Direction.SOUTH)

    assert result.get_error_code() == ErrorCode.INVALID_MOVE_NO_DOOR

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

def test_cant_move_after_placing_tile(game):
    game, _, movement, _, _ = game

    game.move_player(Direction.NORTH)
    game.place_tile()

    result = game.move_player(Direction.SOUTH)
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

# rotate_tile
def test_can_rotate_after_move(game):
    game, _, movement, _, _ = game

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

    result = game.rotate_tile()

    assert not result.is_fail()

def test_rotate_tile_only_allowed_after_move(game):
    game, _, movement, _, _ = game

    result = game.rotate_tile()
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

    game.move_player(Direction.NORTH)
    game.rotate_tile()

    assert not result.is_fail()

def test_move_failure_doesnt_allow_rotate(game):
    game, _, movement, _, _ = game

    result = game.move_player(Direction.SOUTH)
    assert result.is_fail()

    result = game.rotate_tile()
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

#place_tile
def test_place_tile_works_after_move(game):
    game, _, _, _, _ = game

    game.move_player(Direction.NORTH)
    result = game.place_tile()

    assert not result.is_fail()

def test_cant_place_tile_if_havent_moved(game):
    game, _, movement, _, _ = game

    result = game.place_tile()

    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

def test_place_tile_without_zombie_door_draws_card(game):
    game, _, movement, _, actions = game
    start_cards = actions.get_remaining_card_count()
    # TODO not zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    assert actions.get_remaining_card_count() == start_cards - 1

def test_place_tile_with_zombie_door_does_zombie_door(game):
    game, _, movement, _, actions = game
    # TODO zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    # TODO assert zombie door

# Zombie door
def test_zombie_door_pick_works_in_zombie_door_mode(game):
    game, _, movement, _, actions = game
    # TODO

def test_zombie_door_pick_only_allowed_in_zombie_door_mode(game):
    game, _, _, _, _ = game
    # TODO not zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    result = game.pick_zombie_door(Direction.NORTH)
    assert result.is_fail()
    # TODO
    #assert result.get_error_code() == ErrorCode.NOT_ZOMBIE_DOOR


#attack
def test_attack_in_combat_works(game):
    game, _, _, _, _ = game

def test_attack_with_machete_calculates_damage_correctly(game):
    game, _, _, _, _ = game

def test_attack_during_move_fails(game):
    game, _, _, _, _ = game

def test_attack_during_item_search_fails(game):
    game, _, _, _, _ = game

def test_attack_with_chainsaw_and_fuel_works(game):
    game, _, _, _, _ = game

def test_attack_with_chainsaw_without_fuel_fails(game):
    game, _, _, _, _ = game

def test_attack_with_chainsaw_without_chainsaw_fails(game):
    game, _, _, _, _ = game

def test_attack_with_instant_kill_does_no_damage(game):
    game, _, _, _, _ = game

def test_attack_with_instant_kill_without_items_fails(game):
    game, _, _, _, _ = game

#flee
def test_flee_from_combat_works(game):
    game, _, _, _, _ = game

def test_flee_to_unexplored_tile_fails(game):
    game, _, _, _, _ = game

def test_flee_with_oil_does_no_damage(game):
    game, _, _, _, _ = game

def test_flee_with_oil_without_oil_fails(game):
    game, _, _, _, _ = game

def test_flee_during_item_search_fails(game):
    game, _, _, _, _ = game

def test_flee_during_combat_fails(game):
    game, _, _, _, _ = game

#end_turn
def test_end_turn_with_health_heals(game):
    game, _, _, _, _ = game

def test_end_turn_with_item_lets_item_search(game):
    game, _, _, _, _ = game

def test_end_turn_with_find_totem_draws_card_and_doesnt_win(game):
    game, _, _, _, _ = game

def test_end_turn_with_bury_totem_with_totem_draws_card_and_wins(game):
    game, _, _, _, _ = game

def test_end_turn_with_bury_totem_without_totem_fails(game):
    game, _, _, _, _ = game

def test_end_turn_during_move_fails(game):
    game, _, _, _, _ = game

def test_end_turn_during_combat_fails(game):
    game, _, _, _, _ = game

def test_end_turn_during_item_search_fails(game):
    game, _, _, _, _ = game


#search_for_item
def test_search_for_item_returns_item(game):
    game, _, _, _, _ = game

def test_search_for_item_fails_when_not_searching(game):
    game, _, _, _, _ = game

#ignore_search_for_item
def test_ignore_search_during_search_works(game):
    game, _, _, _, _ = game

def test_ignore_search_not_during_search_fails(game):
    game, _, _, _, _ = game

#take_item
def test_take_item_with_found_gives_that_item(game):
    game, _, _, _, _ = game

def test_take_item_with_no_found_item_fails(game):
    game, _, _, _, _ = game

def test_take_item_with_full_inventory_fails(game):
    game, _, _, _, _ = game

#discard_item
def test_discard_item_with_item_works(game):
    game, _, _, _, _ = game

def test_discard_item_with_no_item_fails(game):
    game, _, _, _, _ = game

def test_discard_item_with_invalid_slot_id_fails(game):
    game, _, _, _, _ = game

#use_item
def test_use_gasoline_with_gasoline_and_chainsaw_refuels(game):
    game, _, _, _, _ = game
    #empty chainsaw, attack with chainsaw, then refuel, attack with chainsaw

def test_use_soda_heals(game):
    game, _, _, _, _ = game

def test_use_other_items_fails(game):
    game, _, _, _, _ = game

def test_use_gasoline_without_gasoline_fails(game):
    game, _, _, _, _ = game

def test_use_gasoline_without_chainsaw_fails(game):
    game, _, _, _, _ = game

def test_use_soda_without_soda_fails(game):
    game, _, _, _, _ = game


#check_win_loss
def test_end_turn_with_buried_totem_wins(game):
    game, _, _, _, _ = game

def test_exhaust_hp_loses(game):
    game, _, _, _, _ = game

def test_out_of_time_loses(game):
    game, _, _, _, _ = game

def test_not_buried_hp_left_not_out_of_time_does_nothing(game):
    game, _, _, _, _ = game

def test_end_turn_with_bury_totem_without_totem_doesnt_win(game):
    game, _, _, _, _ = game
