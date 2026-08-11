import pytest
from zimp.domain.events.event_handler import EventHandler
from zimp.domain.events.dev_card import DevCard, CardEffect, EffectType
from zimp.domain.events.current_state_fake import CurrentState
from zimp.domain.events.tile_fake import Tile
from zimp.domain.common.mode import Mode
from zimp.domain.common.end_turn_effects import EndTurnEffects

# =================== Setup ===================

TEST_DECK = (
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

@pytest.fixture
def handler():
    event_handler = EventHandler()
    event_handler.dev_cards = TEST_DECK
    event_handler.deck = list(event_handler.dev_cards)
    return event_handler

# =================== Success ===================

def test_shuffle_deck_contains_expected_cards(handler):
    handler.shuffle_deck()

    assert len(handler.deck) == len(TEST_DECK) - 2
    assert all(isinstance(card, DevCard) for card in handler.deck)

def test_draw_last_card_from_deck(handler):
    state = CurrentState()
    tile = Tile()
    handler.deck = [handler.dev_cards[0]]

    handler.draw_and_resolve_card(state, tile)

    assert len(handler.deck) == 0

def test_draw_when_deck_empty(handler):
    state = CurrentState()
    tile = Tile()
    handler.deck = []

    handler.draw_and_resolve_card(state, tile)

    assert len(handler.deck) == len(TEST_DECK) - 3

def test_get_remaining_card_count(handler):
    handler.shuffle_deck()

    assert handler.get_remaining_card_count() == 1

def test_draw_card_removes_card(handler):
    state = CurrentState()
    tile = Tile()

    card = handler.draw_and_resolve_card(state, tile)

    assert card is not None
    assert handler.get_remaining_card_count() == 2

def test_hp_card_changes_player_hp(handler):
    state = CurrentState(time=0)
    tile = Tile()

    handler.draw_and_resolve_card(state, tile)

    assert state.get_hp() == 4

def test_zombie_card_returns_zombies_count(handler):
    state = CurrentState(time=1)
    tile = Tile()

    effect = handler.draw_and_resolve_card(state, tile)

    assert effect.value == 4
    assert state.get_mode() == Mode.COMBAT

def test_item_card_changes_mode_to_search(handler):
    state = CurrentState(time=2)
    tile = Tile()

    handler.draw_and_resolve_card(state, tile)

    assert state.get_mode() == Mode.SEARCH_FOR_ITEM

def test_resolve_attack_changes_hp(handler):
    state = CurrentState()
    tile = Tile()
    tile.set_zombies(3)

    handler.resolve_attack(state, tile)

    assert state.get_hp() == 4

def test_resolve_attack_with_no_zombies_does_not_damage_player(handler):
    state = CurrentState()
    tile = Tile()

    handler.resolve_attack(state, tile)

    assert state.get_hp() == 5

def test_resolve_attack_when_player_is_stronger_than_zombies(handler):
    state = CurrentState()
    state.set_attack(10)
    tile = Tile()
    tile.set_zombies(3)

    handler.resolve_attack(state, tile)

    assert state.get_hp() == 5

def test_resolve_flee_with_zombies_changes_hp(handler):
    state = CurrentState()
    tile = Tile()
    tile.set_zombies(3)

    handler.resolve_flee(state, tile)

    assert state.get_hp() == 4

def test_resolve_flee_multiple_times(handler):
    state = CurrentState()
    tile = Tile()
    tile.set_zombies(3)

    handler.resolve_flee(state, tile)
    handler.resolve_flee(state, tile)

    assert state.get_hp() == 3

def test_resolve_flee_with_no_zombies_doesnt_change_hp(handler):
    state = CurrentState()
    tile = Tile()

    handler.resolve_flee(state, tile)

    assert state.get_hp() == 5

def test_resolve_item_card_consumes_card(handler):
    state = CurrentState(time=2)
    tile = Tile()

    starting_count = len(handler.deck)

    handler.draw_and_resolve_card(state, tile)

    assert len(handler.deck) == starting_count - 1
    assert state.get_mode() == Mode.SEARCH_FOR_ITEM

def test_search_for_item_returns_item(handler):
    state = CurrentState()

    item = handler.search_for_item(state)

    assert item == 3
    assert state.get_mode() == Mode.FOUND_ITEM

def test_end_turn_with_no_effect_changes_nothing(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.NONE
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.get_hp() == 5
    assert state.get_mode() == Mode.DEV_CARD

def test_end_turn_hp_effect(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.HP
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.get_hp() == 6

def test_end_turn_item_changes_mode(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.ITEM
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.get_mode() == Mode.SEARCH_FOR_ITEM

def test_end_turn_find_totem_finds_totem(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.FIND_TOTEM
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.has_got_totem() == True

def test_end_turn_bury_totem_buries_totem(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.BURY_TOTEM
    state.take_totem()
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.has_buried_totem() == True

# =================== Failure ===================

def test_end_turn_invalid_effect_raises_error(handler):
    state = CurrentState()
    tile = Tile()

    with pytest.raises(ValueError) as error:
        handler.end_turn(state, "INVALID", tile)

    assert state.get_hp() == 5
    assert state.get_mode() == Mode.DEV_CARD

def test_cannot_bury_totem_without_totem(handler):
    state = CurrentState()
    end_effect = EndTurnEffects.BURY_TOTEM
    tile = Tile()

    handler.end_turn(state, end_effect, tile)

    assert state.has_buried_totem() == False