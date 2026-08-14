import pytest
from zimp.domain.actions.action_handler import EventHandler
from zimp.domain.actions.dev_card import DevCard, CardEffect, EffectType
from zimp.support.events.current_state_fake import CurrentState
from zimp.support.events.tile_fake import Tile
from zimp.domain.common.game_mode import Mode
from zimp.domain.common.tile_effect import TileEffect

# =================== Setup ===================

TEST_ITEM_ID = 7

TEST_DECK = (
        DevCard(
            (CardEffect(EffectType.HP, 1),
             CardEffect(EffectType.ZOMBIES, 1),
             CardEffect(EffectType.ITEM)),
            3,
        ),
        DevCard(
            (CardEffect(EffectType.NONE),
             CardEffect(EffectType.HP, 1),
             CardEffect(EffectType.ZOMBIES, 3)),
            1,
        ),
        DevCard(
            (CardEffect(EffectType.NONE),
             CardEffect(EffectType.HP, 1),
             CardEffect(EffectType.ZOMBIES, 2)),
            2,
        ),
        DevCard(
            (CardEffect(EffectType.HP, -1),
             CardEffect(EffectType.ZOMBIES, 4),
             CardEffect(EffectType.ITEM)),
            TEST_ITEM_ID,
        ),
    )

@pytest.fixture
def handler():
    event_handler = EventHandler(TEST_DECK)
    return event_handler

@pytest.fixture
def state():
    state = CurrentState()
    return state

@pytest.fixture
def tile():
    tile = Tile()
    return tile

# =================== Success ===================

def test_get_remaining_card_count(handler):
    handler.reset()

    assert handler.get_remaining_card_count() == len(TEST_DECK) - 2

def test_reset_deck_contains_expected_cards(handler):
    handler.reset()

    assert all(isinstance(card, DevCard) for card in TEST_DECK)

def test_draw_last_card_from_deck(handler, state, tile):

    handler.draw_and_resolve_card(state, tile)
    handler.draw_and_resolve_card(state, tile)
    handler.draw_and_resolve_card(state, tile)
    handler.draw_and_resolve_card(state, tile)

    assert handler.get_remaining_card_count() == 0

def test_draw_card_removes_card(handler, state, tile):
    start_deck_size = handler.get_remaining_card_count()
    card = handler.draw_and_resolve_card(state, tile)
    end_deck_size = handler.get_remaining_card_count()

    assert card is not None
    assert end_deck_size == start_deck_size - 1

def test_hp_card_changes_player_hp(handler, state, tile):
    effect = handler.draw_and_resolve_card(state, tile)

    assert effect.effect_type == EffectType.HP
    assert effect.value == -1
    assert state.get_hp() == 4

def test_zombie_card_spawns_zombies(handler, state, tile):
    state.advance_time()
    tile.add_zombies(0)

    effect = handler.draw_and_resolve_card(state, tile)

    assert effect.effect_type == EffectType.ZOMBIES
    assert effect.value == 4
    assert state.get_mode() == Mode.COMBAT

def test_item_card_changes_mode_to_search(handler, state, tile):
    state.advance_time()
    state.advance_time()

    effect = handler.draw_and_resolve_card(state, tile)

    assert effect.effect_type == EffectType.ITEM
    assert state.get_mode() == Mode.SEARCH_FOR_ITEM

def test_resolve_attack_changes_hp_correctly(handler, state, tile):
    start_hp = state.get_hp()
    tile.add_zombies(3)

    handler.resolve_attack(state, tile)

    assert state.get_hp() == start_hp - 1

def test_resolve_attack_with_no_zombies_does_not_damage_player(handler, state, tile):
    start_hp = state.get_hp()
    handler.resolve_attack(state, tile)

    assert state.get_hp() == start_hp

def test_search_for_item_returns_item(handler, state):
    item = handler.search_for_item(state)

    assert item == TEST_ITEM_ID
    assert state.get_mode() == Mode.FOUND_ITEM

def test_resolve_attack_when_player_is_stronger_than_zombies(handler, state, tile):
    start_hp = state.get_hp()
    state.set_attack(10)
    tile.add_zombies(3)

    handler.resolve_attack(state, tile)

    assert state.get_hp() == start_hp

def test_resolve_flee_with_zombies_changes_hp(handler, state, tile):
    start_hp = state.get_hp()
    tile.add_zombies(3)

    handler.resolve_flee(state, tile)

    assert state.get_hp() == start_hp - 1

def test_resolve_flee_multiple_times(handler, state, tile):
    start_hp = state.get_hp()
    tile.add_zombies(3)

    handler.resolve_flee(state, tile)
    handler.resolve_flee(state, tile)

    assert state.get_hp() == start_hp - 2

def test_resolve_flee_with_no_zombies_doesnt_change_hp(handler, state, tile):
    start_hp = state.get_hp()

    handler.resolve_flee(state, tile)

    assert state.get_hp() == start_hp

def test_end_turn_with_no_effect_changes_nothing(handler, state, tile):
    start_hp = state.get_hp()
    start_mode = state.get_mode()

    handler.end_turn(state, tile)

    assert state.get_hp() == start_hp
    assert state.get_mode() == start_mode

def test_end_turn_hp_effect(handler, state, tile):
    start_hp = state.get_hp()
    tile.set_tile_effect(TileEffect.HEALTH)

    handler.end_turn(state, tile)

    assert state.get_hp() == start_hp + 1

def test_end_turn_item_changes_mode(handler, state, tile):
    tile.set_tile_effect(TileEffect.SEARCH)

    handler.end_turn(state, tile)

    assert state.get_mode() == Mode.SEARCH_FOR_ITEM

def test_end_turn_find_totem_finds_totem(handler, state, tile):
    start_totem = state.has_got_totem()
    tile.set_tile_effect(TileEffect.FIND_TOTEM)

    handler.end_turn(state, tile)

    assert start_totem == False
    assert state.has_got_totem() == True

def test_end_turn_bury_totem_buries_totem(handler, state, tile):
    tile.set_tile_effect(TileEffect.BURY_TOTEM)
    start_buried = state.has_buried_totem()
    state.take_totem()

    handler.end_turn(state, tile)

    assert start_buried == False
    assert state.has_buried_totem() == True

# =================== Failure ===================

def test_end_turn_invalid_effect_raises_error(handler, state, tile):
    start_hp = state.get_hp()
    start_mode = state.get_mode()
    tile.set_tile_effect("INVALID")

    effect = handler.end_turn(state, tile)

    assert effect is None
    assert state.get_hp() == start_hp
    assert state.get_mode() == start_mode

def test_cannot_bury_totem_without_totem(handler, state, tile):
    start_totem = state.has_got_totem()
    tile.set_tile_effect(TileEffect.BURY_TOTEM)

    handler.end_turn(state, tile)

    assert start_totem == False
    assert state.has_buried_totem() == False

def test_draw_when_deck_empty(state, tile):
    handler = EventHandler([])

    with pytest.raises(ValueError):
        handler.draw_and_resolve_card(state, tile)

    assert handler.get_remaining_card_count() == 0