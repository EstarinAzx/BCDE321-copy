class Tile:
    def __init__(self):
        self._num_zombies = 0

    def get_zombie_count(self) -> int:
        return self._num_zombies

    def add_zombies(self, new_zombies: int) -> None:
        self._num_zombies = new_zombies

    def defeat_zombies(self) -> None:
        self._num_zombies = 0