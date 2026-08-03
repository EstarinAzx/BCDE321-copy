from dataclasses import dataclass
from enum import Enum, auto
import random

from zimp.domain.enums import Mode, TileEffects

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
)

class EventHandler:
    """Dev card deck & effects, combat resolution, room effects."""
    def __init__(self):
        self.devCards = CARDS
        self.deck = []
        self.activeCard: DevCard | None = None

    def shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
        self.deck.clear()
        self.deck.extend(self.devCards)
        random.shuffle(self.deck)
        self.deck = self.deck[2:]

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self.deck)

    def draw_card(self, state, tile) -> None:
        """Draw a dev card from the deck"""
        if len(self.deck) == 0:
            return

        self.activeCard = self.deck.pop()

        if self.activeCard is None:
            return

        card = self.activeCard.effects[state.time]

        if card.effect == EffectType.HP:
            state.hp += card.value
        elif card.effect == EffectType.ZOMBIES:
            state.mode = Mode.COMBAT
            tile.num_zombies = card.value
        elif card.effect == EffectType.ITEM:
            state.mode = Mode.SEARCH_FOR_ITEM

    def resolve_attack(self, state, tile) -> None:
        """Conclude combat with zombies in the current room"""
        state.hp += 1 + state.attack - tile.num_zombies
        tile.num_zombies = 0

    def resolve_flee(self, state) -> None:
        """Flee zombies in the current room"""
        state.hp -= 1

    def search_for_item(self, state) -> int:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        new_card = self.deck.pop()
        state.mode = Mode.FOUND_ITEM
        return new_card.item

    def end_turn(self, state, tile)  -> None:
        """Conclude the current turn and resolve room effects"""
        self.activeCard = None

        if tile.end_effect == TileEffects.HP:
            state.hp += 1
        elif tile.end_effect == TileEffects.ITEM:
            state.mode = Mode.SEARCH_FOR_ITEM
        elif tile.end_effect == TileEffects.FIND_TOTEM:
            self.draw_card(state, tile)
            state.have_totem = True
        elif tile.end_effect == TileEffects.BURY_TOTEM:
            self.draw_card(state, tile)
            state.buried_totem = True