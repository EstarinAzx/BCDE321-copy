from dataclasses import dataclass
from zimp.domain.enums import Mode

@dataclass
class CurrentState:
    """State object owned by GameState"""
    def change_hp(self, hp_change: int) -> None:
        """"""
    def get_attack(self):
        """"""
    def get_time(self):
        """"""
    def advance_time(self):
        """"""
    def set_mode(self, new_mode: Mode):
        """"""
    def take_totem(self):
        """"""
    def bury_totem(self):
        """"""
    def has_got_totem(self):
        """"""
