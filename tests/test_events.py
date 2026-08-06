import pytest
from zimp.domain.event_handler import EventHandler, DevCard, CardEffect, EffectType
from zimp.domain.enums import Mode, EndTurnEffects

# =================== Setup ===================

class MockState:
    def __init__(self, time=0, mode=Mode.DEV_CARD):
        self.time = time
        self.mode = mode
        self.hp = 5
        self.attack = 1
        self.have_totem = False
        self.buried_totem = False
    def change_hp(self, hp_change: int) -> None:
        self.hp += hp_change
    def get_attack(self):
        return self.attack
    def get_time(self):
        return self.time
    def advance_time(self):
        self.time += 1
    def set_mode(self, new_mode: Mode):
        self.mode = new_mode
    def take_totem(self):
        self.have_totem = True
    def bury_totem(self):
        self.buried_totem = True
    def has_got_totem(self):
        return self.have_totem


@pytest.fixture
def handler():
    event_handler = EventHandler()
    event_handler.dev_cards = (
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
    event_handler.deck = list(event_handler.dev_cards)
    return event_handler

# =================== Success ===================

def test_shuffle_deck_contains_expected_cards(handler):
    handler.shuffle_deck()

    assert len(handler.deck) == 1
    assert all(isinstance(card, DevCard) for card in handler.deck)

def test_draw_last_card_from_deck(handler):
    state = MockState()
    handler.deck = [handler.dev_cards[0]]

    card = handler.draw_card(state)

    assert card == handler.dev_cards[0]
    assert len(handler.deck) == 0

def test_get_remaining_card_count(handler):
    handler.shuffle_deck()

    assert handler.get_remaining_card_count() == 1

def test_draw_card_removes_card(handler):
    state = MockState()

    card = handler.draw_card(state)

    assert card is not None
    assert handler.get_remaining_card_count() == 2

def test_hp_card_changes_player_hp(handler):
    state = MockState(time=0)

    handler.resolve_card(state)

    assert state.hp == 4

def test_zombie_card_returns_zombies_count(handler):
    state = MockState(time=1)

    zombie_count = handler.resolve_card(state)

    assert zombie_count == 4
    assert state.mode == Mode.COMBAT

def test_item_card_changes_mode_to_search(handler):
    state = MockState(time=2)

    handler.resolve_card(state)

    assert state.mode == Mode.SEARCH_FOR_ITEM

def test_resolve_attack_changes_hp(handler):
    state = MockState()
    num_zombies = 3

    handler.resolve_attack(state, num_zombies)

    assert state.hp == 4

def test_resolve_attack_with_no_zombies_does_not_damage_player(handler):
    state = MockState()
    num_zombies = 0

    handler.resolve_attack(state, num_zombies)

    assert state.hp == 5

def test_resolve_attack_when_player_is_stronger_than_zombies(handler):
    state = MockState()
    state.attack = 10
    num_zombies = 3

    handler.resolve_attack(state, num_zombies)

    assert state.hp == 5

def test_resolve_flee_changes_hp(handler):
    state = MockState()

    handler.resolve_flee(state)

    assert state.hp == 4

def test_resolve_flee_multiple_times(handler):
    state = MockState()

    handler.resolve_flee(state)
    handler.resolve_flee(state)

    assert state.hp == 3

def test_resolve_item_card_consumes_card(handler):
    state = MockState(time=2)

    starting_count = len(handler.deck)

    handler.resolve_card(state)

    assert len(handler.deck) == starting_count - 1
    assert state.mode == Mode.SEARCH_FOR_ITEM

def test_search_for_item_returns_item(handler):
    state = MockState()

    item = handler.search_for_item(state)

    assert item == 3
    assert state.mode == Mode.FOUND_ITEM

def test_end_turn_with_no_effect_changes_nothing(handler):
    state = MockState()
    end_effect = EndTurnEffects.NONE

    handler.end_turn(state, end_effect)

    assert state.hp == 5
    assert state.mode == Mode.DEV_CARD

def test_end_turn_hp_effect(handler):
    state = MockState()
    end_effect = EndTurnEffects.HP

    handler.end_turn(state, end_effect)

    assert state.hp == 6

def test_end_turn_item_changes_mode(handler):
    state = MockState()
    end_effect = EndTurnEffects.ITEM

    handler.end_turn(state, end_effect)

    assert state.mode == Mode.SEARCH_FOR_ITEM

def test_end_turn_find_totem_finds_totem(handler):
    state = MockState()
    end_effect = EndTurnEffects.FIND_TOTEM

    handler.end_turn(state, end_effect)

    assert state.have_totem == True

def test_end_turn_bury_totem_buries_totem(handler):
    state = MockState()
    end_effect = EndTurnEffects.BURY_TOTEM
    state.have_totem = True

    handler.end_turn(state, end_effect)

    assert state.buried_totem == True

# =================== Failure ===================

def test_draw_empty_deck_advances_time(handler):
    state = MockState(time=0)
    handler.deck = []

    handler.draw_card(state)

    assert state.time == 1

def test_draw_empty_deck_after_final_time_returns_none(handler):
    state = MockState(time=2)
    handler.deck = []

    card = handler.draw_card(state)

    assert card is None
    assert state.time == 2

def test_resolve_card_after_final_time_with_empty_deck(handler):
    state = MockState()

    handler.deck = []
    state.time = 2

    num_zombies = handler.resolve_card(state)

    assert state.hp == 5
    assert num_zombies == 0

def test_search_for_item_after_final_time_when_deck_empty(handler):
    state = MockState()

    handler.deck = []
    state.time = 2

    item = handler.search_for_item(state)

    assert item is None

def test_end_turn_invalid_effect_does_nothing(handler):
    state = MockState()

    handler.end_turn(state, "INVALID")

    assert state.hp == 5
    assert state.mode == Mode.DEV_CARD

def test_cannot_bury_totem_without_totem(handler):
    state = MockState()
    end_effect = EndTurnEffects.BURY_TOTEM

    handler.end_turn(state, end_effect)

    assert state.buried_totem is False