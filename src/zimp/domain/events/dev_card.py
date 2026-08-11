from dataclasses import dataclass
from enum import Enum, auto

class EffectType(Enum):
    NONE = auto()
    HP = auto()
    ZOMBIES = auto()
    ITEM = auto()

@dataclass(frozen=True)
class CardEffect:
    effect: EffectType
    value: int = 0

@dataclass(frozen=True)
class DevCard:
    effects: tuple[CardEffect, CardEffect, CardEffect]
    item: int