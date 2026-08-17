from typing import Protocol, runtime_checkable

from zimp.domain.common.ItemCode import ItemCode
from zimp.domain.common.result import Result


@runtime_checkable
class ItemsContract(Protocol):
    """Contract used by the application layer to reach the player's inventory.

    Illegal actions raise ValueError carrying a message meant for the player;
    the controller turns that into visible text rather than handling codes.
    """

    #def add(self, item_id: str) -> None:
    #    """Take an item into the inventory, or refuse if both pockets are full."""

    #def discard(self, item_id: str) -> None:
    #    """Drop a held item, or refuse if it is not held."""

    #def use(self, item_id: str) -> Effect:
    #    """Spend a held consumable and report what should happen to the player."""

    def held_items(self) -> list[str]:
        """What the player is carrying."""

    #def attack_bonus(self) -> int:
    #    """The attack a held weapon adds, counting only the best single weapon.
    #
    #    Combat adds this to the player's base attack. An empty chainsaw
    #    contributes nothing.
    #    """

    def record_battle(self) -> None:
        """Tell the inventory a battle happened so the chainsaw burns fuel.

        Combat must call this or the chainsaw never runs out.
        """

    # New methods
    def attack_bonus(self, with_chainsaw: bool) -> int:
        pass
    def try_use_instant_kill(self) -> Result:
        pass
    def get_has_oil(self) -> bool:
        pass
    def find_item(self, item_id: ItemCode) -> None:
        pass
    def keep_found_item(self) -> Result:
        pass
    def dont_take_item(self) -> None:
        pass
    def discard_item(self, slot_id: int) -> None:
        pass
    def use_item(self, item_id: ItemCode) -> None:
        pass