from dataclasses import dataclass


@dataclass
class Effect:
    """What using an item does to the player.

    Returned to the caller rather than applied directly, so the inventory
    never reaches into another component's state.
    """

    health: int = 0
    attack: int = 0


# Weapons are passive: they raise the attack score while carried, and are
# never "used". Only one may be applied in combat, even if two are carried.
WEAPON_ATTACK: dict[str, int] = {
    "golf_club": 1,
    "machete": 2,
    "chainsaw": 3,
}

# Consumables are active: the player uses them and they are spent.
CONSUMABLE_EFFECTS: dict[str, Effect] = {
    "can_of_soda": Effect(health=2),
}


class Inventory:
    """The player's pockets."""

    CAPACITY = 2
    CHAINSAW_BATTLES = 2

    def __init__(self) -> None:
        self.held: list[str] = []
        self.chainsaw_fuel = self.CHAINSAW_BATTLES

    def add(self, item_id: str) -> None:
        if len(self.held) >= self.CAPACITY:
            raise ValueError("you are already carrying two items")
        self.held.append(item_id)

    def discard(self, item_id: str) -> None:
        self._require_held(item_id)
        self.held.remove(item_id)

    def use(self, item_id: str) -> Effect:
        self._require_held(item_id)
        if item_id not in CONSUMABLE_EFFECTS:
            raise ValueError(f"a {item_id} is not something you can use")
        return CONSUMABLE_EFFECTS[item_id]

    def record_battle(self) -> None:
        """Burn a battle's worth of chainsaw fuel, if a chainsaw is carried."""
        if "chainsaw" in self.held and self.chainsaw_fuel > 0:
            self.chainsaw_fuel -= 1

    def attack_bonus(self) -> int:
        bonuses = [
            WEAPON_ATTACK[item]
            for item in self.held
            if item in WEAPON_ATTACK and self._has_fuel(item)
        ]
        if not bonuses:
            return 0
        # Only one weapon may be used in combat, so the player takes the best.
        return max(bonuses)

    def _has_fuel(self, item_id: str) -> bool:
        """Only the chainsaw runs out; every other weapon works indefinitely."""
        return item_id != "chainsaw" or self.chainsaw_fuel > 0

    def _require_held(self, item_id: str) -> None:
        if item_id not in self.held:
            raise ValueError(f"you are not carrying a {item_id}")
