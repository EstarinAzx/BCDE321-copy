import random

from zimp.domain.common.mode import Mode
from zimp.domain.common.end_turn_effects import EndTurnEffects
from zimp.domain.events.tile_fake import Tile
from zimp.domain.events.current_state_fake import CurrentState
from zimp.domain.events.dev_card import DevCard, EffectType, CardEffect
from zimp.domain.events.card_data import CARD_DATA


class EventHandler:
    """Dev card deck & effects, combat resolution, room effects."""

    __END_TURN_HEAL = 1
    __FLEE_DAMAGE = -1
    __COMBAT_BONUS = 1

    def __init__(self):
        self.dev_cards = CARD_DATA
        self.deck: list[DevCard] = []

        self.shuffle_deck()

    def shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
        self.deck.clear()
        self.deck.extend(self.dev_cards)
        random.shuffle(self.deck)

        if len(self.deck) <= 2:
            raise ValueError("Deck does not contain enough cards")

        self.deck = self.deck[2:]

    def __draw_card(self) -> DevCard:
        """Draw a dev card from the deck and return it, shuffling if required"""
        if not self.deck:
            self.shuffle_deck()

        return self.deck.pop()

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self.deck)

    def draw_and_resolve_card(self, state: CurrentState, tile: Tile) -> CardEffect:
        """Draw and resolve a new card"""
        active_card = self.__draw_card()

        try:
            current_effect = active_card.effects[state.get_time()]
        except:
            raise ValueError("Invalid time")

        if current_effect.effect == EffectType.HP:
            state.change_hp(current_effect.value) # Contract assumption
        elif current_effect.effect == EffectType.ZOMBIES:
            state.set_mode(Mode.COMBAT) # Contract assumption
            tile.set_zombies(current_effect.value)
        elif current_effect.effect == EffectType.ITEM:
            state.set_mode(Mode.SEARCH_FOR_ITEM) # Contract assumption

        return current_effect

    def resolve_attack(self, state: CurrentState, num_zombies: int) -> None:
        """Conclude combat with zombies in the current room"""
        damage = max(0, num_zombies - state.get_attack() - self.__COMBAT_BONUS) # Contract assumption
        state.change_hp(-damage) # Contract assumption

    def resolve_flee(self, state: CurrentState, num_zombies: int) -> None:
        """Flee zombies in the current room"""
        if num_zombies == 0:
            return

        state.change_hp(self.__FLEE_DAMAGE) # Contract assumption

    def search_for_item(self, state: CurrentState) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        new_card = self.__draw_card()

        state.set_mode(Mode.FOUND_ITEM) # Contract assumption
        return new_card.item

    def end_turn(self, state: CurrentState, tile_end_effect: EndTurnEffects, tile: Tile) -> CardEffect | None:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""
        match tile_end_effect:
            case EndTurnEffects.HP:
                state.change_hp(self.__END_TURN_HEAL) # Contract assumption
            case EndTurnEffects.ITEM:
                state.set_mode(Mode.SEARCH_FOR_ITEM) # Contact assumption
            case EndTurnEffects.FIND_TOTEM:
                state.take_totem() # Contract assumption
                return self.draw_and_resolve_card(state, tile)
            case EndTurnEffects.BURY_TOTEM:
                if state.has_got_totem(): # Contact assumption
                    state.bury_totem() # Contract assumption
                    return self.draw_and_resolve_card(state, tile)
            case EndTurnEffects.NONE:
                return None
            case _:
                raise ValueError("Unknown end turn effect")

        return None