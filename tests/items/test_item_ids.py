import pytest

from zimp.domain.common.item_ids import (
    CARD_ITEM_IDS,
    IMPLEMENTED_ITEMS,
    RULEBOOK_ITEMS,
    item_id_for_card,
)
from zimp.domain.items.inventory import CONSUMABLE_EFFECTS, WEAPON_ATTACK


def test_every_implemented_item_is_a_rulebook_item() -> None:
    assert IMPLEMENTED_ITEMS <= set(RULEBOOK_ITEMS)


def test_implemented_items_match_what_the_inventory_actually_knows() -> None:
    known = set(WEAPON_ATTACK) | set(CONSUMABLE_EFFECTS)

    assert IMPLEMENTED_ITEMS == known


def test_rulebook_item_names_are_unique() -> None:
    assert len(set(RULEBOOK_ITEMS)) == len(RULEBOOK_ITEMS)


def test_every_mapped_card_produces_a_rulebook_item() -> None:
    """Guards the mapping as it is filled in, one card at a time."""
    assert set(CARD_ITEM_IDS.values()) <= set(RULEBOOK_ITEMS)


def test_no_two_cards_map_to_the_same_item() -> None:
    assert len(set(CARD_ITEM_IDS.values())) == len(CARD_ITEM_IDS)


def test_an_unmapped_card_is_refused_rather_than_guessed() -> None:
    unmapped = next(n for n in range(100) if n not in CARD_ITEM_IDS)

    with pytest.raises(ValueError, match=str(unmapped)):
        item_id_for_card(unmapped)