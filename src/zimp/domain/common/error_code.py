from enum import Enum, auto


class ErrorCode(Enum):
    """MOVEMENT ERRORS"""
    DEPLETED_INSIDE_TILES = auto()
    DEPLETED_OUTSIDE_TILES = auto()
    INVALID_POSITION = auto()
    INVALID_MOVE_OUT_OF_BOUNDS = auto()
    INVALID_MOVE_NO_DOOR = auto()
    INVALID_MOVE_ACROSS_AREAS = auto()
    INVALID_MOVE_FLEE_TO_UNKNOWN = auto()
    INVALID_MOVE_ZOMBIE_DOOR_ON_KNOWN_TILE = auto()
    INVALID_MODE_MOVEMENT = auto()
    INVALID_MODE_ROTATE_TILE = auto()
    INVALID_MODE_PLACE_TILE = auto()

    """GENERAL ERRORS"""
    FATAL_ERROR = auto()
