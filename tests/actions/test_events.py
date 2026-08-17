import pytest

from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.events.events import Events


# -----------------------------------------------------------------------------------------------------------
# Setup fixtures
# -----------------------------------------------------------------------------------------------------------

@pytest.fixture
def sample_cards():
    return (
        DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.ITEM),
                CardEffect(CardEffectType.ZOMBIES, 6),
            ),
            0,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.ZOMBIES, 4),
                CardEffect(CardEffectType.HEALTH, -1),
                CardEffect(CardEffectType.ITEM),
            ),
            1,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.ITEM),
                CardEffect(CardEffectType.ZOMBIES, 4),
                CardEffect(CardEffectType.HEALTH, -1),
            ),
            2,
        ),
    )


@pytest.fixture
def deck(sample_cards):
    """A fresh Events instance for each test."""
    return Events(sample_cards)


@pytest.fixture
def none_deck():
    return (
        DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            0,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            0,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            0,
        ),
    )


# -----------------------------------------------------------------------------------------------------------
# Constructor / validation
# -----------------------------------------------------------------------------------------------------------

class TestValidateCards:
    def test_none_cards_raises_value_error(self):
        with pytest.raises(ValueError, match="No dev cards configured"):
            Events(None)  # type: ignore[arg-type]

    def test_empty_cards_raises_value_error(self):
        with pytest.raises(ValueError, match="No dev cards configured"):
            Events(())

    def test_less_than_two_cards_raises_runtime_error(self):
        card = DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            0,
        )

        with pytest.raises(RuntimeError, match="Dev card deck must have at least 2 cards"):
            Events((card,))

    def test_non_dev_card_raises_value_error(self):
        with pytest.raises(ValueError, match="Misconfigured dev card"):
            Events((object(), object(), object()))  # type: ignore[arg-type]

    def test_negative_item_id_raises_value_error(self):
        card = DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            -1,
        )

        with pytest.raises(ValueError, match="Misconfigured card item"):
            Events((card, card, card))

    def test_non_int_item_id_raises_value_error(self):
        card = DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            "bad",  # type: ignore[arg-type]
        )

        with pytest.raises(ValueError, match="Misconfigured card item"):
            Events((card, card, card))

    def test_wrong_effect_count_raises_value_error(self):
        card = DevCard(
            (# type: ignore[arg-type]
                CardEffect(CardEffectType.NONE),
            ),
            0,
        )

        with pytest.raises(ValueError, match="Dev cards must have 3 effects"):
            Events((card, card, card))

    def test_non_card_effect_in_effects_raises_value_error(self):
        card = DevCard(
            (# type: ignore[arg-type]
                CardEffect(CardEffectType.NONE),
                "bad",
                CardEffect(CardEffectType.NONE),
            ),
            0,
        )

        with pytest.raises(ValueError, match="Misconfigured card effect"):
            Events((card, card, card))

    def test_non_card_effect_type_raises_value_error(self):
        card = DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect("bad"),  # type: ignore[arg-type]
                CardEffect(CardEffectType.NONE),
            ),
            0,
        )

        with pytest.raises(ValueError, match="Misconfigured card effect type"):
            Events((card, card, card))

    def test_non_int_effect_value_raises_value_error(self):
        card = DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.HEALTH, "bad"),  # type: ignore[arg-type]
                CardEffect(CardEffectType.NONE),
            ),
            0,
        )

        with pytest.raises(ValueError, match="Misconfigured card effect value"):
            Events((card, card, card))


# -----------------------------------------------------------------------------------------------------------
# Initial state
# -----------------------------------------------------------------------------------------------------------

class TestInitialState:
    def test_constructor_creates_handler(self):
        handler = Events()

        assert handler is not None

    def test_initial_count_matches_deck(self, deck, sample_cards):
        assert deck.get_remaining_card_count() == len(sample_cards)

    def test_custom_card_deck(self, deck, sample_cards):
        assert deck.get_remaining_card_count() == len(sample_cards)


# -----------------------------------------------------------------------------------------------------------
# Reset
# -----------------------------------------------------------------------------------------------------------

class TestReset:
    def test_reset_discards_two_cards(self, deck, sample_cards):
        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2

    def test_reset_restores_deck_to_full_shuffled_size(self, deck, sample_cards):
        # Draw a card first.
        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == len(sample_cards) - 1

        # Reset starts a fresh shuffled deck and discards two cards.
        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2

    def test_reset_can_be_called_multiple_times(self, deck, sample_cards):
        deck.reset()
        deck.reset()
        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2


# -----------------------------------------------------------------------------------------------------------
# Remaining card count
# -----------------------------------------------------------------------------------------------------------

class TestGetRemainingCardCount:
    def test_returns_initial_count(self, deck, sample_cards):
        assert deck.get_remaining_card_count() == len(sample_cards)

    def test_decreases_after_draw_event(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_event(0)

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_decreases_after_draw_item(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_decreases_after_waste_time(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.waste_time()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_can_become_empty(self, sample_cards):
        handler = Events(sample_cards)

        for _ in range(len(sample_cards)):
            result, shuffled = handler.waste_time()

            assert not result.is_fail()
            assert shuffled is False

        assert handler.get_remaining_card_count() == 0


# -----------------------------------------------------------------------------------------------------------
# Draw event
# -----------------------------------------------------------------------------------------------------------

class TestDrawEvent:
    def test_returns_success_with_effect(self, deck):
        result, shuffled = deck.draw_event(0)

        assert not result.is_fail()
        assert shuffled is False
        assert isinstance(result.get_data(), CardEffect)

    def test_returns_effect_at_requested_time(self, deck):
        result, shuffled = deck.draw_event(1)

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == CardEffect(CardEffectType.ITEM)

    def test_returns_effect_at_last_valid_time(self, deck):
        result, shuffled = deck.draw_event(2)

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == CardEffect(CardEffectType.ZOMBIES, 6)

    @pytest.mark.parametrize("time", [-1, 3, 99])
    def test_invalid_time_returns_fatal_error(self, deck, time):
        result, shuffled = deck.draw_event(time)

        assert result.is_fail()
        assert result.get_error_code() == ErrorCode.FATAL_ERROR
        assert shuffled is False

    def test_invalid_time_still_consumes_card(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_event(-1)

        assert result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1


# -----------------------------------------------------------------------------------------------------------
# Draw item
# -----------------------------------------------------------------------------------------------------------

class TestDrawItem:
    def test_returns_item_id(self, deck):
        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert isinstance(result.get_data(), int)
        assert result.get_data() == 0

    def test_returns_next_card_item_after_draw(self, deck):
        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False

        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == 1


# -----------------------------------------------------------------------------------------------------------
# Waste time
# -----------------------------------------------------------------------------------------------------------

class TestWasteTime:
    def test_returns_card(self, deck):
        result, shuffled = deck.waste_time()

        assert not result.is_fail()
        assert shuffled is False
        assert isinstance(result.get_data(), DevCard)

    def test_returns_first_card(self, sample_cards):
        handler = Events(sample_cards)

        result, shuffled = handler.waste_time()

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == sample_cards[0]

    def test_draws_cards_in_order(self, sample_cards):
        handler = Events(sample_cards)

        result1, shuffled1 = handler.waste_time()
        result2, shuffled2 = handler.waste_time()
        result3, shuffled3 = handler.waste_time()

        assert shuffled1 is False
        assert shuffled2 is False
        assert shuffled3 is False

        assert result1.get_data() == sample_cards[0]
        assert result2.get_data() == sample_cards[1]
        assert result3.get_data() == sample_cards[2]

        assert handler.get_remaining_card_count() == 0


# -----------------------------------------------------------------------------------------------------------
# Shuffling
# -----------------------------------------------------------------------------------------------------------

class TestShuffle:
    def test_drawing_from_empty_deck_shuffles(self, sample_cards):
        handler = Events(sample_cards)

        # Exhaust the initial deck.
        for _ in range(len(sample_cards)):
            result, shuffled = handler.waste_time()
            assert not result.is_fail()
            assert shuffled is False

        assert handler.get_remaining_card_count() == 0

        # The next draw must shuffle and discard two cards.
        result, shuffled = handler.waste_time()

        assert not result.is_fail()
        assert shuffled is True
        assert isinstance(result.get_data(), DevCard)
        assert handler.get_remaining_card_count() == len(sample_cards) - 3

    def test_shuffle_discards_two_cards(self, sample_cards):
        handler = Events(sample_cards)

        handler.reset()

        assert handler.get_remaining_card_count() == len(sample_cards) - 2

    def test_shuffle_flag_only_true_when_shuffle_occurs(self, sample_cards):
        handler = Events(sample_cards)

        result1, shuffled1 = handler.waste_time()
        result2, shuffled2 = handler.waste_time()
        result3, shuffled3 = handler.waste_time()

        assert not result1.is_fail()
        assert not result2.is_fail()
        assert not result3.is_fail()

        assert shuffled1 is False
        assert shuffled2 is False
        assert shuffled3 is False

        # Deck is now empty, so the next draw triggers a shuffle.
        result4, shuffled4 = handler.waste_time()

        assert not result4.is_fail()
        assert shuffled4 is True

    def test_reset_does_not_report_shuffle(self, sample_cards):
        handler = Events(sample_cards)

        # reset() has no return value, so only verify its resulting state.
        handler.reset()

        assert handler.get_remaining_card_count() == len(sample_cards) - 2