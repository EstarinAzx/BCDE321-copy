from typing import runtime_checkable, Protocol

from zimp.domain.common.direction import Direction
from zimp.domain.common.result import Result
from zimp.domain.common.tile_effect import TileEffect


@runtime_checkable
class MovementContract(Protocol):
    """Contract for movement"""

    def move(self, direction: Direction) -> Result:
        """Attempt to move the player in the given direction"""

    def flee(self, direction: Direction) -> Result:
        """Attempt to flee the player in the given direction"""

    def create_zombie_door(self, direction: Direction) -> Result:
        """Attempt to create a zombie door in the given direction"""

    def rotate_placement_tile(self) -> Result:
        """Rotate the placement tile"""

    def lock_placement_tile(self) -> Result:
        """Lock the rotation of the placement tile"""

    def need_zombie_door(self) -> bool:
        """Check if map needs a zombie door"""

    def is_placement_mode_on(self) -> bool:
        """Check if the placement mode is on"""

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
              randomizer_seed: int | None = None) -> Result:
        """Reset tiles and optionally set map dimensions, player starting position, and/or tile randomizer seed"""

    # new methods
    def pick_zombie_door(self, direction: Direction) -> Result:
        pass
    def flee_zombies(self, direction: Direction) -> Result:
        pass