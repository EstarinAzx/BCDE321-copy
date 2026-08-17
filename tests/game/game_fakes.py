from zimp.domain.common.direction import Direction

from zimp.domain.common.result import Result


class GameStateContract:
    """Fake game state used by Game integration tests."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.can_move = True
        self.is_moving = False
        self.is_zombie_door = False
        self.can_attack = True
        self.can_flee = True
        self.is_searching_item = False
        self.has_found_item = False
        self.can_end_turn = True
        self.is_doing_events = False
        self.has_ended_turn = False
        self.has_won = False
        self.has_lost = False
        self.time = 0

        self.reset_calls = getattr(self, "reset_calls", 0) + 1

        self.apply_card_effect_calls = []
        self.advance_time_calls = 0
        self.start_zombie_door_calls = 0
        self.start_new_turn_calls = 0
        self.start_move_calls = 0
        self.end_move_calls = 0
        self.confirm_zombie_door_calls = 0
        self.attack_calls = []
        self.flee_calls = []
        self.find_item_calls = 0
        self.end_searching_item_calls = 0
        self.end_found_item_calls = 0
        self.drink_soda_calls = 0
        self.cower_calls = 0
        self.do_end_turn_effect_calls = []

    def get_time(self):
        return self.time

    def apply_card_effect(self, card) -> None:
        self.apply_card_effect_calls.append(card)

    def advance_time(self) -> None:
        self.advance_time_calls += 1

    def get_has_ended_turn(self) -> bool:
        return self.has_ended_turn

    def start_zombie_door(self) -> None:
        self.start_zombie_door_calls += 1

    def start_new_turn(self) -> None:
        self.start_new_turn_calls += 1

    def get_can_move(self) -> bool:
        return self.can_move

    def start_move(self) -> None:
        self.start_move_calls += 1
        self.is_moving = True

    def get_is_moving(self) -> bool:
        return self.is_moving

    def end_move(self) -> None:
        self.end_move_calls += 1
        self.is_moving = False

    def get_is_zombie_door(self) -> bool:
        return self.is_zombie_door

    def confirm_zombie_door(self) -> None:
        self.confirm_zombie_door_calls += 1
        self.is_zombie_door = False

    def get_can_attack(self) -> bool:
        return self.can_attack

    def attack(self, attack_bonus, instant_kill: bool) -> Result:
        self.attack_calls.append((attack_bonus, instant_kill))
        return Result.success(None)

    def get_can_flee(self) -> bool:
        return self.can_flee

    def flee(self, with_oil: bool) -> None:
        self.flee_calls.append(with_oil)

    def get_is_searching_item(self) -> bool:
        return self.is_searching_item

    def find_item(self) -> None:
        self.find_item_calls += 1
        self.has_found_item = True

    def end_searching_item(self) -> None:
        self.end_searching_item_calls += 1
        self.is_searching_item = False

    def get_has_found_item(self) -> bool:
        return self.has_found_item

    def end_found_item(self) -> None:
        self.end_found_item_calls += 1
        self.has_found_item = False

    def drink_soda(self) -> None:
        self.drink_soda_calls += 1

    def get_can_end_turn(self) -> bool:
        return self.can_end_turn

    def cower(self) -> Result:
        self.cower_calls += 1
        return Result.success(None)

    def do_end_turn_effect(self, tile_effect) -> None:
        self.do_end_turn_effect_calls.append(tile_effect)

    def get_is_doing_events(self) -> bool:
        return self.is_doing_events

    def check_is_won(self) -> bool:
        return self.has_won

    def check_is_lost(self) -> bool:
        return self.has_lost

from zimp.domain.common.direction import Direction
from zimp.domain.common.result import Result


class MovementContract:
    """Fake movement used by Game integration tests."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.move_player_result = Result.success(None)
        self.rotate_placement_tile_result = Result.success(None)
        self.lock_placement_tile_result = Result.success(None)
        self.pick_zombie_door_result = Result.success(None)
        self.flee_zombies_result = Result.success(None)
        self.zombie_door = False
        self.tile_effect = None

        self.reset_calls = getattr(self, "reset_calls", 0) + 1
        self.move_player_calls = []
        self.rotate_placement_tile_calls = 0
        self.lock_placement_tile_calls = 0
        self.check_is_zombie_door_calls = 0
        self.pick_zombie_door_calls = []
        self.flee_zombies_calls = []
        self.get_tile_effect_calls = 0

    def move_player(self, direction: Direction) -> Result:
        self.move_player_calls.append(direction)
        return self.move_player_result

    def rotate_placement_tile(self) -> Result:
        self.rotate_placement_tile_calls += 1
        return self.rotate_placement_tile_result

    def lock_placement_tile(self) -> Result:
        self.lock_placement_tile_calls += 1
        return self.lock_placement_tile_result

    def check_is_zombie_door(self) -> bool:
        self.check_is_zombie_door_calls += 1
        return self.zombie_door

    def pick_zombie_door(self, direction: Direction) -> Result:
        self.pick_zombie_door_calls.append(direction)
        return self.pick_zombie_door_result

    def flee_zombies(self, direction: Direction) -> Result:
        self.flee_zombies_calls.append(direction)
        return self.flee_zombies_result

    def get_tile_effect(self):
        self.get_tile_effect_calls += 1
        return self.tile_effect

from zimp.domain.common.result import Result


class ItemsContract:
    """Fake items used by Game integration tests."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.try_use_instant_kill_result = Result.success(None)
        self.attack_bonus_result = 0
        self.keep_found_item_result = Result.success(None)
        self.discard_result = Result.success((Result.success(None), False))
        self.use_result = Result.success(None)
        self.has_oil = True

        self.reset_calls = getattr(self, "reset_calls", 0) + 1
        self.try_use_instant_kill_calls = 0
        self.attack_bonus_calls = []
        self.record_battle_calls = 0
        self.find_item_calls = []
        self.keep_found_item_calls = 0
        self.dont_take_item_calls = 0
        self.discard_calls = []
        self.use_calls = []
        self.get_has_oil_calls = 0

    def try_use_instant_kill(self) -> Result:
        self.try_use_instant_kill_calls += 1
        return self.try_use_instant_kill_result

    def attack_bonus(self, use_chainsaw: bool):
        self.attack_bonus_calls.append(use_chainsaw)
        return self.attack_bonus_result

    def record_battle(self) -> None:
        self.record_battle_calls += 1

    def get_has_oil(self) -> bool:
        self.get_has_oil_calls += 1
        return self.has_oil

    def use_item(self, item_id) -> Result:
        self.use_calls.append(item_id)
        return Result.success(None)

    def find_item(self, item) -> None:
        self.find_item_calls.append(item)

    def keep_found_item(self) -> Result:
        self.keep_found_item_calls += 1
        return self.keep_found_item_result

    def dont_take_item(self) -> None:
        self.dont_take_item_calls += 1

    def discard(self, slot_id: int = -1) -> Result:
        self.discard_calls.append(slot_id)
        return self.discard_result

    def use(self, item_id: int) -> Result:
        self.use_calls.append(item_id)
        return self.use_result

from zimp.domain.common.result import Result


class EventsContract:
    """Fake events used by Game integration tests."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.draw_event_result = Result.success("event")
        self.draw_event_shuffled = False

        self.draw_item_result = Result.success("item")
        self.draw_item_shuffled = False

        self.waste_time_result = Result.success(None)
        self.waste_time_shuffled = False

        self.reset_calls = getattr(self, "reset_calls", 0) + 1
        self.draw_event_calls = []
        self.draw_item_calls = 0
        self.waste_time_calls = 0

    def draw_event(self, time):
        self.draw_event_calls.append(time)
        return self.draw_event_result, self.draw_event_shuffled

    def draw_item(self):
        self.draw_item_calls += 1
        return self.draw_item_result, self.draw_item_shuffled

    def waste_time(self):
        self.waste_time_calls += 1
        return self.waste_time_result, self.waste_time_shuffled