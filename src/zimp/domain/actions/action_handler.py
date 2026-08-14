import random

from zimp.domain.common.result import Result
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.common.action_result import ActionResult
from zimp.domain.common.action_result_type import ActionResultType
from zimp.domain.common.game_mode import GameMode

from zimp.domain.actions.dev_card import DevCard, CardEffectType, CardEffect
from zimp.domain.actions.card_data import CARD_DATA


class ActionHandler:
    """Dev card deck & effects, combat resolution, room effects."""

    _END_TURN_HEAL = 1
    _FLEE_DAMAGE = -1

    _START_TIME = 0
    _MAX_TIME = 2

    _NUM_DISCARD = 2

    def __init__(self, cards: tuple[DevCard, ...] = CARD_DATA) -> None:
        self._validate_cards(cards)

        self._dev_cards = cards
        self._deck: list[DevCard] = list(cards)

        self._current_time = self._START_TIME
        self._is_time_up = False

        self._tile_effect_map: dict[TileEffect, ActionResult] = {}
        self._card_effect_map: dict[CardEffectType, ActionResultType] = {}

        self._setup_card_effect_map()
        self._setup_action_result_map()

    # -----------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------

    def _validate_cards(self, cards: tuple[DevCard, ...]):
        """Validates the card deck and raises an error if any problems are found"""
        if cards is None or not cards:
            raise ValueError("No dev cards configured")
        for card in cards:
            if not isinstance(card, DevCard):
                raise ValueError("Misconfigured dev card")

            if not isinstance(card.item, int) or card.item < 0:
                raise ValueError("Misconfigured card item")

            if len(card.effects) != 3:
                raise ValueError("Dev cards must have 3 effects")

            for effect in card.effects:
                if not isinstance(effect, CardEffect):
                    raise ValueError("Misconfigured card effect")

                if not isinstance(effect.effect_type, CardEffectType):
                    raise ValueError("Misconfigured card effect type")

                if not isinstance(effect.value, int):
                    raise ValueError("Misconfigured card effect value")
    
    def _add_tile_effect(self, effect: TileEffect, result: ActionResult) -> None:
        self._tile_effect_map[effect] = result

    def _setup_action_result_map(self) -> None:
        self._add_tile_effect(TileEffect.HEALTH, ActionResult(ActionResultType.CHANGE_HP, self._END_TURN_HEAL))
        self._add_tile_effect(TileEffect.SEARCH, ActionResult(ActionResultType.SEARCH_ITEM))
        self._add_tile_effect(TileEffect.FIND_TOTEM, ActionResult(ActionResultType.FIND_TOTEM))
        self._add_tile_effect(TileEffect.BURY_TOTEM, ActionResult(ActionResultType.BURY_TOTEM))
        self._add_tile_effect(TileEffect.NONE, ActionResult(ActionResultType.NONE))

    def _add_card_effect(self, effect: CardEffectType, result_type: ActionResultType) -> None:
        self._card_effect_map[effect] = result_type

    def _setup_card_effect_map(self) -> None:
        self._add_card_effect(CardEffectType.NONE, ActionResultType.NONE)
        self._add_card_effect(CardEffectType.HEALTH, ActionResultType.CHANGE_HP)
        self._add_card_effect(CardEffectType.ZOMBIES, ActionResultType.ADD_ZOMBIES)
        self._add_card_effect(CardEffectType.ITEM, ActionResultType.SEARCH_ITEM)

    def _advance_time(self) -> None:
        if self._current_time == self._MAX_TIME:
            self._is_time_up = True
        else:
            self._current_time += 1

    def _shuffle_deck(self) -> Result:
        """Shuffle the dev card deck and discard two"""
        if len(self._dev_cards) <= self._NUM_DISCARD:
            return Result.fail(ErrorCode.FATAL_ERROR)

        deck = list(self._dev_cards)
        random.shuffle(deck)
        self._deck = deck[self._NUM_DISCARD:]
        return Result.success(None)

    def _draw_card(self) -> Result:
        """Draw a dev card from the deck and return it, shuffling if required"""
        if not self._deck:
            shuffled = self._shuffle_deck()
            if shuffled.is_fail():
                return shuffled

            self._advance_time()
            if self._is_time_up:
                return Result.success(None)

        card = self._deck.pop()
        return Result.success(card)

    # -----------------------------------------------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------------------------------------------

    def reset(self) -> Result:
        """Reset the deck for a new game"""
        self._current_time = self._START_TIME
        self._is_time_up = False

        return self._shuffle_deck()

    def is_time_up(self) -> bool:
        """Returns whether it is past midnight"""
        return self._is_time_up

    def get_remaining_card_count(self) -> int:
        """Return the number of remaining dev cards in the deck"""
        return len(self._deck)

    def draw_and_resolve_card(self) -> Result:
        """Draw and resolve a new card"""
        draw = self._draw_card()
        if draw.is_fail() or draw.get_data() is None:
            return draw

        effects = draw.get_data().effects
        if not 0 <= self._current_time < len(effects):
            return Result.fail(ErrorCode.FATAL_ERROR)

        current_effect = effects[self._current_time]

        result_type = self._card_effect_map.get(current_effect.effect_type)
        if result_type is None:
            return Result.fail(ErrorCode.FATAL_ERROR)

        action = ActionResult(result_type, current_effect.value)
        return Result.success(action)

    def resolve_attack(self, zombie_count: int, attack: int) -> Result:
        """What occurs when the player has attempted to attack zombies"""
        if zombie_count < 0 or attack <= 0:
            return Result.fail(ErrorCode.FATAL_ERROR)

        base_damage = attack - zombie_count
        damage = max(0, base_damage)
        damage = min(4, damage)

        action = ActionResult(ActionResultType.DEFEAT_ZOMBIES, damage)
        return Result.success(action)

    def resolve_moved(self) -> Result:
        """What occurs when the player has successfully moved to a different room"""
        return self.draw_and_resolve_card()

    def resolve_flee(self, zombie_count: int, take_damage: bool) -> Result:
        """What occurs when the player has attempted to flee zombies"""
        if zombie_count < 0:
            return Result.fail(ErrorCode.FATAL_ERROR)

        if zombie_count == 0 or not take_damage:
            action = ActionResult(ActionResultType.NONE)
            return Result.success(action)

        action = ActionResult(ActionResultType.FLEE_ZOMBIES, self._FLEE_DAMAGE)
        return Result.success(action)

    def resolve_cower(self) -> Result:
        """What occurs when the player has attempted to cower"""
        action = ActionResult(ActionResultType.COWER)
        return Result.success(action)

    def search_for_item(self) -> Result:
        """After an event has found an item, draw the next card to see what it is and return its id."""
        draw = self._draw_card()
        if draw.is_fail():
            return draw

        item = draw.get_data().item
        if item is None:
            return Result.fail(ErrorCode.FATAL_ERROR)

        if not isinstance(item, int) or item < 0:
            return Result.fail(ErrorCode.FATAL_ERROR)

        action = ActionResult(ActionResultType.FOUND_ITEM, item)
        return Result.success(action)

    def end_turn(self, effect: TileEffect) -> Result:
        """Conclude the current turn and resolve room effects, then return the number of zombies to spawn"""
        action = self._tile_effect_map.get(effect)

        if action is None:
            return Result.fail(ErrorCode.FATAL_ERROR)

        return Result.success(action)