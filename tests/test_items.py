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


def test_using_a_machete_gives_attack_not_health() -> None:
    inventory = Inventory()
    inventory.add("machete")

    effect = inventory.use("machete")

    assert effect.attack == 2
    assert effect.health == 0


def test_using_an_item_you_do_not_hold_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="can_of_soda"):
        inventory.use("can_of_soda")

    assert inventory.held == ["machete"]
