from enum import Enum, auto

class EndTurnEffects(Enum):
    NONE = auto(),
    HP = auto(),
    ITEM = auto(),
    FIND_TOTEM = auto(),
    BURY_TOTEM = auto(),