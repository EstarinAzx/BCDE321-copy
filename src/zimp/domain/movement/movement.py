from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.movement.direction import Direction
from zimp.domain.movement.tile_data import TileData
from zimp.domain.movement.tile_effect import TileEffect
from zimp.support.fake_game_mode import GameMode


class Movement:
    def __init__(self, map_dimensions: tuple[int, int] | None = None, starting_position: tuple[int, int] | None = None,
                 randomizer_seed: int | None = None) -> None:
        pass

    def move_player(self, mode: GameMode, direction: Direction) -> Result:
        pass

    def rotate_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        pass

    def lock_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        pass

    def need_zombie_door(self, mode: GameMode) -> bool:
        pass

    def get_tile_data(self) -> list[TileData]:
        pass

    def get_player_position(self) -> tuple[int, int]:
        pass

    def get_zombie_count(self) -> int:
        pass

    def defeat_zombies(self) -> None:
        pass

    def add_zombies(self, number_of_zombies: int) -> None:
        pass

    def get_tile_effect(self) -> TileEffect:
        pass

    def reset(self, map_dimensions: tuple[int, int] | None = None, starting_position: tuple[int, int] | None = None,
              randomizer_seed: int | None = None) -> ErrorCode | None:
        pass
