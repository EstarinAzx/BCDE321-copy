import pytest

from zimp.domain.items import Inventory


def test_added_item_is_held() -> None:
    inventory = Inventory()

    inventory.add("machete")

    assert inventory.held == ["machete"]


def test_third_item_is_rejected_when_two_held() -> None:
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("candle")

    with pytest.raises(ValueError):
        inventory.add("chainsaw")

    assert inventory.held == ["machete", "candle"]


def test_discarded_item_is_no_longer_held() -> None:
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("candle")

    inventory.discard("machete")

    assert inventory.held == ["candle"]


def test_discarding_an_item_you_do_not_hold_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="chainsaw"):
        inventory.discard("chainsaw")

    assert inventory.held == ["machete"]


def test_using_a_can_of_soda_gives_two_health() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")

    effect = inventory.use("can_of_soda")

    assert effect.health == 2


def test_holding_a_machete_gives_a_two_point_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("machete")

    assert inventory.attack_bonus() == 2


def test_empty_hands_give_no_attack_bonus() -> None:
    assert Inventory().attack_bonus() == 0


def test_a_carried_consumable_gives_no_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")

    assert inventory.attack_bonus() == 0


def test_carrying_two_weapons_applies_only_the_stronger_one() -> None:
    inventory = Inventory()
    inventory.add("golf_club")
    inventory.add("machete")

    assert inventory.attack_bonus() == 2


def test_holding_a_chainsaw_gives_a_three_point_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    assert inventory.attack_bonus() == 3


def test_chainsaw_still_has_fuel_for_its_second_battle() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()

    assert inventory.attack_bonus() == 3


def test_chainsaw_gives_no_bonus_once_its_fuel_is_spent() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.attack_bonus() == 0


def test_a_spent_chainsaw_is_still_carried() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.held == ["chainsaw"]


def test_a_weaker_weapon_is_used_once_the_chainsaw_is_spent() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")
    inventory.add("machete")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.attack_bonus() == 2


def test_using_an_item_you_do_not_hold_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="can_of_soda"):
        inventory.use("can_of_soda")

    assert inventory.held == ["machete"]
