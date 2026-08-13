from enum import Enum, auto


class GameMode(Enum):
    MOVE = auto()
    PLACEMENT = auto()
    FLED = auto()
    COMBAT = auto()
    ZOMBIE_DOOR = auto()
