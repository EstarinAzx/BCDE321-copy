from enum import Enum, auto


class ErrorCode(Enum):
    """MOVEMENT ERRORS"""
    DEPLETED_INSIDE_TILES = auto()
    DEPLETED_OUTSIDE_TILES = auto()
    INVALID_POSITION = auto()
    OUT_OF_BOUNDS_MOVE = auto()
    MISALIGNED_DOOR_MOVE = auto()
    CROSS_AREA_MOVE = auto()
    # Movement Mode Errors
    MOVE_IN_PLACEMENT_MODE = auto()
    ROTATE_TILE_NOT_IN_PLACEMENT_MODE = auto()
    PLACE_TILE_NOT_IN_PLACEMENT_MODE = auto()
    MOVE_TO_KNOWN_TILE_IN_ZOMBIE_DOOR_MODE = auto()
    MOVE_TO_UNKNOWN_TILE_IN_FLEE_MODE = auto()

    # GENERAL
    FATAL_ERROR = auto()

