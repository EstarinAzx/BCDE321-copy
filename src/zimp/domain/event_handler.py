from dataclasses import dataclass
from enum import Enum, auto
import random

from zimp.domain.enums import Mode, EndTurnEffects

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

        self._shuffle_deck()

    def _shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
        self.deck.clear()
        self.deck.extend(self.dev_cards)
        random.shuffle(self.deck)
        self.deck = self.deck[2:]

    def _draw_card(self, state) -> DevCard | None:
        """Draw a dev card from the deck"""
        if not self.deck:
            if state.time == 2:
                return None
            state.time += 1
            self._shuffle_deck()

        return self.deck.pop()

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self.deck)

    def resolve_card(self, state, tile) -> None:
        active_card = self._draw_card(state)
        print(active_card)
        if active_card is None:
            return

        current_effect = active_card.effects[state.time]

        if current_effect.effect == EffectType.HP:
            state.hp += current_effect.value
        elif current_effect.effect == EffectType.ZOMBIES:
            state.mode = Mode.COMBAT
            tile.num_zombies = current_effect.value
        elif current_effect.effect == EffectType.ITEM:
            state.mode = Mode.SEARCH_FOR_ITEM

    def resolve_attack(self, state, tile) -> None:
        """Conclude combat with zombies in the current room"""
        damage = max(0, tile.num_zombies - state.attack - 1)
        state.hp -= damage

        tile.num_zombies = 0

    def resolve_flee(self, state) -> None:
        """Flee zombies in the current room"""
        state.hp -= 1

    def search_for_item(self, state) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        new_card = self._draw_card(state)
        if new_card is None:
            return None

        state.mode = Mode.FOUND_ITEM
        return new_card.item

    def end_turn(self, state, tile)  -> None:
        """Conclude the current turn and resolve room effects"""
        if tile.end_effect == EndTurnEffects.HP:
            state.hp += 1
        elif tile.end_effect == EndTurnEffects.ITEM:
            state.mode = Mode.SEARCH_FOR_ITEM
        elif tile.end_effect == EndTurnEffects.FIND_TOTEM:
            self.resolve_card(state, tile)
            state.have_totem = True
        elif tile.end_effect == EndTurnEffects.BURY_TOTEM and state.have_totem:
            self.resolve_card(state, tile)
            state.buried_totem = True