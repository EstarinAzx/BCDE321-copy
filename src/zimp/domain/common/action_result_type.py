from enum import Enum, auto

class ActionResultType(Enum):
    NONE = auto()

    ADD_ZOMBIES = auto()
    DEFEAT_ZOMBIES = auto()
    FLEE_ZOMBIES = auto()
    COWER = auto()

    SEARCH_ITEM = auto()
    FOUND_ITEM = auto()

    CHANGE_HP = auto()
    FIND_TOTEM = auto()
    BURY_TOTEM = auto()