import pytest

from zimp.support.game.game_state_fake import GameState
from zimp.support.game.items_fake import Items
from zimp.domain.actions.action_handler import ActionHandler
from zimp.support.game.movement_fake import Movement
from zimp.domain.game.game import Game

@pytest.fixture
def handler():
    state = GameState()
    items = Items()
    actions = ActionHandler()
    movement = Movement()

    game = Game(state, actions, items, movement)
    return game

#reset

#move_player

#rotate_tile

#place_tile

#pick_zombie_door_attack

#attack

#flee

#cower

#end_turn

#perform_search_for_item

#ignore_search_for_item

#take_item

#discard_item

#use_item
