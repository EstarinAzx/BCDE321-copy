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
        if item_id not in self.held:
            raise ValueError(f"you are not carrying a {item_id}")
        self.held.remove(item_id)
