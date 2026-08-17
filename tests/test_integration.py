import pytest

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.game.game import Game

from zimp.domain.events.events import Events
from zimp.domain.items.items import Items
from zimp.domain.movement.movement import Movement

@pytest.fixture
def game():
    movement = Movement()
    items = Items()
    actions = Events()

    game = Game(movement, items, actions)

    return game, movement, items, actions

# Reset
def test_reset_resets_all_components(game):
    game, movement, items, actions = game

    # TODO modify all 3 components
    result = game.reset()

    assert not result.is_fail()
    # TODO assert all 3 components are in reset state

# move_player
def test_move_is_allowed_at_start(game):
    game, _, _, _ = game

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

def test_move_success_doesnt_allow_another_move(game):
    game, _, _, _ = game
    game.move_player(Direction.NORTH)

    result = game.move_player(Direction.SOUTH)

    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

def test_can_only_move_north_at_start(game):
    game, _, _, _ = game

    result = game.move_player(Direction.SOUTH)

    assert result.get_error_code() == ErrorCode.INVALID_MOVE_NO_DOOR

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

def test_cant_move_after_placing_tile(game):
    game, movement, _, _ = game

    game.move_player(Direction.NORTH)
    game.place_tile()

    result = game.move_player(Direction.SOUTH)
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

# rotate_tile
def test_can_rotate_after_move(game):
    game, movement, _, _ = game

    result = game.move_player(Direction.NORTH)

    assert not result.is_fail()

    result = game.rotate_tile()

    assert not result.is_fail()

def test_rotate_tile_only_allowed_after_move(game):
    game, movement, _, _ = game

    result = game.rotate_tile()
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

    game.move_player(Direction.NORTH)
    game.rotate_tile()

    assert not result.is_fail()

def test_move_failure_doesnt_allow_rotate(game):
    game, movement, _, _ = game

    result = game.move_player(Direction.SOUTH)
    assert result.is_fail()

    result = game.rotate_tile()
    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

#place_tile
def test_place_tile_works_after_move(game):
    game, _, _, _ = game

    game.move_player(Direction.NORTH)
    result = game.place_tile()

    assert not result.is_fail()

def test_cant_place_tile_if_havent_moved(game):
    game, movement, _, _ = game

    result = game.place_tile()

    assert result.get_error_code() == ErrorCode.WRONG_GAME_MODE

def test_place_tile_without_zombie_door_draws_card(game):
    game, movement, _, actions = game
    start_cards = actions.get_remaining_card_count()
    # TODO not zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    assert actions.get_remaining_card_count() == start_cards - 1

def test_place_tile_with_zombie_door_does_zombie_door(game):
    game, movement, _, actions = game
    # TODO zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    # TODO assert zombie door

# Zombie door
def test_zombie_door_pick_works_in_zombie_door_mode(game):
    game, movement, _, actions = game
    # TODO

def test_zombie_door_pick_only_allowed_in_zombie_door_mode(game):
    game, _, _, _ = game
    # TODO not zombie door
    game.move_player(Direction.NORTH)
    result = game.place_tile()
    assert not result.is_fail()

    result = game.pick_zombie_door(Direction.NORTH)
    assert result.is_fail()
    # TODO
    #assert result.get_error_code() == ErrorCode.NOT_ZOMBIE_DOOR


#attack
#+normal attack
#+attack with machete
#-attacking during move
#-attacking during item search
#+attack with chainsaw and fuel
#-attack with chainsaw with no fuel
#-attack with chainsaw without chainsaw
#-attacking with instant kill without items

#flee
#+flee works
#+flee with oil works
#-flee with oil when no oil
#-flee to unexplored tile
#-flee during item search
#-flee during move

#end_turn
#+end with health heals
#+end with item search lets item search
#+end with find totem draws card and doesnt win
#+end with find totem and bury totem draws card and wins
#-end with bury totem and no have totem does nothing
#-end turn during move fails
#-end turn during combat fails
#-end turn during item search fails

#search_for_item
#+returns an item
#+allows ending turn after but not before
#-fails when not searching for item
#-fails if out of time

#ignore_search_for_item
#+during search for item works
#+allows ending turn after but not before
#-not during search for item fails
#-fails if out of time

#take_item
#+after finding item gives you that item
#-havent found item fails
#-inventory full fails

#discard_item
#+with item discards it (check attack_bonus after discarding weapon)
#-no item to discard fails
#-invalid slot id fails

#use_item
#+using gasoline refuels chainsaw (empty chainsaw, check attack, then refuel, check attack)
#+using soda heals
#-using any other item fails
#-using gasoline/soda when you dont have them fails

#check_win_loss
#+end turn with find totem then bury totem and resolve card wins
#+exhaust hp loses
#+out of time loses
#+none of the above does nothing
#-end turn with bury totem without find doesnt win
