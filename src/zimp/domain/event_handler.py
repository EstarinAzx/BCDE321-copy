from dataclasses import dataclass
from enum import Enum, auto
import random

from zimp.domain.enums import Mode, EndTurnEffects
from zimp.domain.current_state import CurrentState

class EffectType(Enum):
    NONE = auto()
    HP = auto()
    ZOMBIES = auto()
    ITEM = auto()

@dataclass(frozen=True)
class CardEffect:
    effect: EffectType
    value: int = 0

@dataclass(frozen=True)
class DevCard:
    effects: tuple[CardEffect, CardEffect, CardEffect]
    item: int

CARDS = (
    DevCard(
        (CardEffect(EffectType.NONE),
        CardEffect(EffectType.HP, 1),
        CardEffect(EffectType.ZOMBIES, 3)),
        0,
    ),
DevCard(
        (CardEffect(EffectType.NONE),
        CardEffect(EffectType.HP, 1),
        CardEffect(EffectType.ZOMBIES, 3)),
        0,
    ),
)

class EventHandler:
    """Dev card deck & effects, combat resolution, room effects."""
    def __init__(self):
        self.dev_cards = CARDS
        self.deck: list[DevCard] = []

        self.shuffle_deck()

    def shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
        self.deck.clear()
        self.deck.extend(self.dev_cards)
        random.shuffle(self.deck)
        self.deck = self.deck[2:]

    def draw_card(self, state: CurrentState) -> DevCard | None:
        """Draw a dev card from the deck and return it"""
        if not self.deck:
            if state.get_time() == 2:
                return None
            state.advance_time() # Contact assumption
            self.shuffle_deck()

        return self.deck.pop()

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self.deck)

    def resolve_card(self, state: CurrentState) -> int:
        """Draw and resolve a new card, then return the number of zombies to spawn"""
        active_card = self.draw_card(state)

        if active_card is None:
            return 0

        current_effect = active_card.effects[state.time]

        if current_effect.effect == EffectType.HP:
            state.change_hp(current_effect.value) # Contact assumption
        elif current_effect.effect == EffectType.ZOMBIES:
            state.set_mode(Mode.COMBAT) # Contact assumption
            return current_effect.value
        elif current_effect.effect == EffectType.ITEM:
            state.set_mode(Mode.SEARCH_FOR_ITEM) # Contact assumption

        return 0

    def resolve_attack(self, state: CurrentState, num_zombies: int) -> None:
        """Conclude combat with zombies in the current room"""
        damage = max(0, num_zombies - state.get_attack() - 1)
        state.change_hp(-damage) # Contact assumption

    def resolve_flee(self, state: CurrentState) -> None:
        """Flee zombies in the current room"""
        state.change_hp(-1) # Contact assumption

    def search_for_item(self, state: CurrentState) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        new_card = self.draw_card(state)
        if new_card is None:
            return None

        state.set_mode(Mode.FOUND_ITEM) # Contact assumption
        return new_card.item

    def end_turn(self, state: CurrentState, tile_end_effect: EndTurnEffects) -> int:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""
        if tile_end_effect == EndTurnEffects.HP:
            state.change_hp(1) # Contact assumption
        elif tile_end_effect == EndTurnEffects.ITEM:
            state.set_mode(Mode.SEARCH_FOR_ITEM) # Contact assumption
        elif tile_end_effect == EndTurnEffects.FIND_TOTEM:
            state.take_totem() # Contact assumption
            return self.resolve_card(state)
        elif tile_end_effect == EndTurnEffects.BURY_TOTEM and state.has_got_totem(): # Contact assumption
            state.bury_totem() # Contact assumption
            return self.resolve_card(state)

        return 0