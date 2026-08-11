class Tile:
    def __init__(self):
        self._num_zombies = 0

    def set_zombies(self, new_zombies: int) -> None:
        self._num_zombies = new_zombies