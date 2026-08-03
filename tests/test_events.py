import pytest
from zimp.domain.event_handler import EventHandler, DevCard, CardEffect, EffectType
from zimp.domain.enums import Mode, TileEffects

class MockTile:
    def __init__(self, tile_effect = None):
        self.num_zombies = 0
        self.end_effect: TileEffects | None = tile_effect

class MockState:
    def __init__(self, time=0, mode=Mode.DEV_CARD):
        self.time = time
        self.mode = mode
        self.hp = 5
        self.attack = 1
        self.have_totem = False
        self.buried_totem = False


@pytest.fixture
def handler():
    event_handler = EventHandler()
    event_handler.devCards = (
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
            3,
        ),
    )
    event_handler.deck = list(event_handler.devCards)
    return event_handler

def test_shuffled_deck_is_correct_length(handler):
    handler.shuffle_deck()

    assert len(handler.deck) == 1

def test_get_remaining_card_count(handler):
    handler.shuffle_deck()

    assert handler.get_remaining_card_count() == 1

def test_enter_room_draws_card(handler):
    state = MockState()
    tile = MockTile()

    handler.shuffle_deck()
    handler.draw_card(state, tile)

    assert handler.activeCard is not None
    assert handler.get_remaining_card_count() == 0

def test_hp_card_changes_player_hp(handler):
    state = MockState(0)
    tile = MockTile()

    handler.draw_card(state, tile)

    assert state.hp == 4

def test_zombie_card_adds_zombies(handler):
    state = MockState(1)
    tile = MockTile()

    handler.draw_card(state, tile)

    assert tile.num_zombies == 4

def test_item_card_changes_mode_to_search(handler):
    state = MockState(2)
    tile = MockTile()

    handler.draw_card(state, tile)

    assert state.mode == Mode.SEARCH_FOR_ITEM

def test_resolve_attack_kills_zombies_and_changes_hp(handler):
    state = MockState()
    tile = MockTile()

    tile.num_zombies = 3

    handler.resolve_attack(state, tile)

    assert tile.num_zombies == 0
    assert state.hp == 4

def test_resolve_flee_changes_hp(handler):
    state = MockState()

    handler.resolve_flee(state)

    assert state.hp == 4

def test_search_for_item_draws_card(handler):
    state = MockState(2)
    tile = MockTile()

    handler.draw_card(state, tile)
    handler.search_for_item(state)

    assert len(handler.deck) == 1

def test_search_for_item_returns_item(handler):
    state = MockState(2)
    tile = MockTile()

    handler.draw_card(state, tile)
    item = handler.search_for_item(state)

    assert item == 2

def test_end_turn_hp_effect(handler):
    state = MockState()
    tile = MockTile(TileEffects.HP)

    handler.end_turn(state, tile)

    assert state.hp == 6

def test_end_turn_item_changes_mode(handler):
    state = MockState()
    tile = MockTile(TileEffects.ITEM)

    handler.end_turn(state, tile)

    assert state.mode == Mode.SEARCH_FOR_ITEM

def test_end_turn_find_totem_finds_totem(handler):
    state = MockState()
    tile = MockTile(TileEffects.FIND_TOTEM)

    handler.end_turn(state, tile)

    assert state.have_totem == True

def test_end_turn_bury_totem_buries_totem(handler):
    state = MockState()
    tile = MockTile(TileEffects.BURY_TOTEM)
    state.have_totem = True

    handler.end_turn(state, tile)

    assert state.buried_totem == True