from zimp.domain.common.tile_effect import TileEffect


class Tile:
    def __init__(self):
        self._num_zombies = 0
        self._tile_effect = TileEffect.NONE

    def get_tile_effect(self):
        return self._tile_effect

    def set_tile_effect(self, new_tile_effect):
        self._tile_effect = new_tile_effect

    def get_zombie_count(self) -> int:
        return self._num_zombies

    def add_zombies(self, new_zombies: int) -> None:
        self._num_zombies = new_zombies

    def defeat_zombies(self) -> None:
        self._num_zombies = 0