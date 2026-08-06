from dataclasses import dataclass


@dataclass
class Effect:
    """What using an item does to the player.

    Returned to the caller rather than applied directly, so the inventory
    never reaches into another component's state.
    """

    health: int = 0
    attack: int = 0


EFFECTS: dict[str, Effect] = {
    "can_of_soda": Effect(health=2),
    "machete": Effect(attack=2),
}


class Inventory:
    """The player's pockets."""

    CAPACITY = 2

    def __init__(self) -> None:
        self.held: list[str] = []

    def add(self, item_id: str) -> None:
        if len(self.held) >= self.CAPACITY:
            raise ValueError("you are already carrying two items")
        self.held.append(item_id)

    def discard(self, item_id: str) -> None:
        self._require_held(item_id)
        self.held.remove(item_id)

    def use(self, item_id: str) -> Effect:
        self._require_held(item_id)
        return EFFECTS[item_id]

    def _require_held(self, item_id: str) -> None:
        if item_id not in self.held:
            raise ValueError(f"you are not carrying a {item_id}")
