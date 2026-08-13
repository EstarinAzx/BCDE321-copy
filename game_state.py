from dataclasses import dataclass
from zimp.domain.common.mode import Mode

@dataclass
class GameState:

    last_move: str | None = None
    turn_number: int = 0
    mode: Mode = Mode.NONE
    attack: int = 1
    health: int = 6
    hour: int = 0
    has_totem: bool = False
    buried_totem: bool = False
    cowered_this_turn: bool = False
    time_ran_out: bool = False

    def reset(self) -> None:
        self.last_move = None
        self.turn_number = 0
        self.mode = Mode.NONE
        self.attack = 1
        self.health = 6
        self.hour = 0
        self.has_totem = False
        self.buried_totem = False
        self.cowered_this_turn = False
        self.time_ran_out = False

    def advance_time(self, hours: int = 1) -> None:
        self.hour += hours
        if self.hour >= 2:
            self.time_ran_out = True

    def change_hp(self, amount: int) -> None:
        self.health += amount
        if self.health < 0:
            self.health = 0

    def take_totem(self) -> None:
        self.has_totem = True

    def bury_totem(self) -> None:
        if self.has_totem:
            self.buried_totem = True
            self.has_totem = False

    def cower(self) -> tuple[int, bool]:
        if self.cowered_this_turn:
            return 0, False

        self.change_hp(3)
        self.cowered_this_turn = True
        return 3, True

    def is_won(self) -> bool:
        return self.buried_totem and self.health > 0

    def is_lost(self) -> bool:
        if self.mode == Mode.LOST:
            return True

        if self.health <= 0:
            return True

        if self.time_ran_out:
            return True

        return False

    def get_hp(self) -> str:
        return f" HP: {self.health}"

    def get_attack(self) -> str:
        return f"ATK: {self.attack}"

    def get_stats(self) -> str:
        return f"HP: {self.health}, ATK: {self.attack}, Hour: {self.hour}, Totem: {self.buried_totem}"

    def get_time(self) -> str:
        return f"Hour: {self.hour}"

    def has_got_totem(self) -> bool:
        return self.has_totem

    def set_mode(self, new_mode: Mode) -> None:
        if not isinstance(new_mode, Mode):
            raise ValueError(f"Invalid mode: {new_mode}")

        self.mode = new_mode

    def check_win_loss(self) -> Mode:
        if self.mode in (Mode.WON, Mode.LOST):
            return self.mode

        if self.is_won():
            self.mode = Mode.WON
            return self.mode

        if self.is_lost():
            self.mode = Mode.LOST
            return self.mode

        return self.mode

