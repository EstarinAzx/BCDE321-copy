from dataclasses import dataclass
from enum import Enum
from typing import runtime_checkable, Protocol

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.common.game_mode import GameMode
from zimp.domain.common.direction import Direction


@dataclass(frozen=True)
class TileData:
    """TileData class used to hold essential information about individual tiles."""
    id: int
    position: tuple[int, int]
    rotation: Direction
    zombie_door: Direction | None
    zombie_count: int
    is_locked: bool

@runtime_checkable
class MovementContract(Protocol):
    """Contract for movement"""

    def move_player(self, mode: GameMode, direction: Direction) -> Result:
        """Move player in given direction"""

    def rotate_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        """Rotate the placement tile"""

    def lock_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        """Lock the rotation of the placement tile"""

    def need_zombie_door(self) -> bool:
        """Check if map needs a zombie door"""

    def get_tile_data(self) -> list[TileData]:
        """Get data for displayed tiles"""

    def get_player_position(self) -> tuple[int, int]:
        """Gets players position"""

    def get_zombie_count(self) -> int:
        """Get zombie count on current tile"""

    def defeat_zombies(self) -> None:
        """Defeat zombies on current tile"""

    def add_zombies(self, number_of_zombies: int) -> None:
        """Add zombies to current tile"""

    def get_tile_effect(self) -> TileEffect:
        """Get tile effect of current tile"""

    def get_map_dimensions(self) -> tuple[int, int]:
        """Get the map dimensions"""

    def reset(self, map_dimensions: tuple[int, int] | None = None, starting_position: tuple[int, int] | None = None,
              randomizer_seed: int | None = None) -> ErrorCode | None:
        """Reset tiles and optionally set map dimensions, player starting position, and/or tile randomizer seed"""