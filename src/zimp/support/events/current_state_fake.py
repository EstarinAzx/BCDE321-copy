from dataclasses import dataclass
from zimp.domain.common.game_mode import GameMode

@dataclass
class CurrentState:
    def __init__(self, time=0, mode=GameMode.DEV_CARD):
        self._time = time
        self._mode = mode
        self._hp = 5
        self._attack = 1
        self._have_totem = False
        self._buried_totem = False

    def get_hp(self) -> int:
        return self._hp

    def change_hp(self, hp_change: int) -> None:
        self._hp += hp_change

    def get_attack(self) -> int:
        return self._attack

    def set_attack(self, new_attack: int) -> None:
        self._attack = new_attack

    def get_time(self) -> int:
        return self._time

    def advance_time(self) -> None:
        self._time += 1

    def get_mode(self) -> GameMode:
        return self._mode

    def set_mode(self, new_mode: GameMode) -> None:
        self._mode = new_mode

    def take_totem(self) -> None:
        self._have_totem = True

    def bury_totem(self) -> None:
        self._buried_totem = True

    def has_got_totem(self) -> bool:
        return self._have_totem

    def has_buried_totem(self) -> bool:
        return self._buried_totem