import random

from zimp.domain.common.mode import Mode
from zimp.domain.common.tile_effect import TileEffect
from zimp.support.events.tile_fake import Tile
from zimp.support.events.current_state_fake import CurrentState
from zimp.domain.events.dev_card import DevCard, EffectType, CardEffect
from zimp.domain.events.card_data import CARD_DATA


class EventHandler:
    """Dev card deck & effects, combat resolution, room effects."""

    __END_TURN_HEAL = 1
    __FLEE_DAMAGE = -1
    __COMBAT_BONUS = 1

    def __init__(self, cards = CARD_DATA) -> None:
        self.__dev_cards = cards
        self.__deck: list[DevCard] = list(cards)

    def reset(self):
        """Reset the deck for a new game"""
        self.__shuffle_deck()

    def __shuffle_deck(self) -> None:
        """Shuffle the dev card deck and discard two"""
        self.__deck.clear()
        self.__deck.extend(self.__dev_cards)
        random.shuffle(self.__deck)

        if len(self.__deck) <= 2:
            raise ValueError("Deck does not contain enough cards")

        self.__deck = self.__deck[2:]

    def __draw_card(self, state: CurrentState) -> DevCard:
        """Draw a dev card from the deck and return it, shuffling if required"""
        if not self.__deck:
            self.__shuffle_deck()
            state.advance_time()

        return self.__deck.pop()

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self.__deck)

    def draw_and_resolve_card(self, state: CurrentState, tile: Tile) -> CardEffect:
        """Draw and resolve a new card"""
        active_card = self.__draw_card(state)

        try:
            current_effect = active_card.effects[state.get_time()]
        except:
            raise ValueError("Invalid time")

        if current_effect.effect_type == EffectType.HP:
            state.change_hp(current_effect.value) # Contract assumption
        elif current_effect.effect_type == EffectType.ZOMBIES:
            state.set_mode(Mode.COMBAT) # Contract assumption
            tile.add_zombies(current_effect.value)
        elif current_effect.effect_type == EffectType.ITEM:
            state.set_mode(Mode.SEARCH_FOR_ITEM) # Contract assumption

        return current_effect

    def resolve_attack(self, state: CurrentState, tile: Tile) -> None:
        """Conclude combat with zombies in the current room"""
        damage = max(0, tile.get_zombie_count() - state.get_attack() - self.__COMBAT_BONUS) # Contract assumption
        state.change_hp(-damage) # Contract assumption

        tile.defeat_zombies()

    def resolve_flee(self, state: CurrentState, tile: Tile) -> None:
        """Flee zombies in the current room"""
        if tile.get_zombie_count() == 0:
            return

        state.change_hp(self.__FLEE_DAMAGE) # Contract assumption

    def search_for_item(self, state: CurrentState) -> int | None:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        new_card = self.__draw_card(state)

        state.set_mode(Mode.FOUND_ITEM) # Contract assumption
        return new_card.item

    def end_turn(self, state: CurrentState, tile: Tile) -> CardEffect | None:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""
        match tile.get_tile_effect():
            case TileEffect.HEALTH:
                state.change_hp(self.__END_TURN_HEAL) # Contract assumption
            case TileEffect.SEARCH:
                state.set_mode(Mode.SEARCH_FOR_ITEM) # Contact assumption
            case TileEffect.FIND_TOTEM:
                state.take_totem() # Contract assumption
                return self.draw_and_resolve_card(state, tile)
            case TileEffect.BURY_TOTEM:
                if state.has_got_totem(): # Contact assumption
                    state.bury_totem() # Contract assumption
                    return self.draw_and_resolve_card(state, tile)

        return None