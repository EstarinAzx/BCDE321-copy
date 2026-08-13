import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.movement.game_map import GameMap
from zimp.domain.movement.direction import Direction
from zimp.domain.movement.tile_effect import TileEffect
from zimp.support.movement.fake_game_mode import GameMode


# ========================== Good Day ========================== #


def test_init_when_given_valid_map_dimensions_sets_map_dimensions() -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act
    movement = GameMap(map_dimensions=map_dimensions, starting_position=(2, 2))

    # Assert
    assert movement.get_map_dimensions() == map_dimensions


def test_init_when_given_valid_starting_position_sets_player_position() -> None:
    # Arrange
    starting_position = (2, 2)

    # Act
    movement = GameMap(map_dimensions=(4, 5), starting_position=starting_position)

    # Assert
    assert movement.get_player_position() == starting_position


def test_init_when_given_valid_seed_keeps_tile_order_consistent() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    seed = 42
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    second_tile_id = 2

    # Act
    movement_one = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                           randomizer_seed=seed)
    movement_one.move_player(move_game_mode, move_direction)
    tile_data_one = movement_one.get_tile_data()
    movement_two = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                           randomizer_seed=seed)
    movement_two.move_player(move_game_mode, move_direction)
    tile_data_two = movement_two.get_tile_data()

    # Assert
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_one)
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_two)


def test_init_when_given_no_starting_position_default_starting_position_is_used() -> None:
    # Arrange
    default_starting_position = (2, 4)

    # Act
    movement = GameMap(map_dimensions=(5, 5))

    # Assert
    assert movement.get_player_position() == default_starting_position


def test_init_when_given_no_map_dimensions_default_map_dimensions_is_used() -> None:
    # Arrange
    default_map_dimensions = (5, 5)

    # Act
    movement = GameMap(starting_position=(2, 4))

    # Assert
    assert movement.get_map_dimensions() == default_map_dimensions


def test_reset_when_given_valid_map_dimensions_sets_map_dimensions() -> None:
    # Arrange
    new_map_dimensions = (4, 4)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))

    # Act
    result = movement.reset(map_dimensions=new_map_dimensions)

    # Assert
    assert result is None
    assert movement.get_map_dimensions() == new_map_dimensions


def test_reset_when_given_no_map_dimensions_previous_map_dimensions_are_used() -> None:
    # Arrange
    map_dimensions = (4, 4)
    movement = GameMap(map_dimensions=map_dimensions, starting_position=(2, 2))

    # Act
    result = movement.reset()

    # Assert
    assert result is None
    assert movement.get_map_dimensions() == map_dimensions


def test_reset_when_given_valid_starting_position_sets_player_position() -> None:
    # Arrange
    new_starting_position = (1, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))

    # Act
    result = movement.reset(starting_position=new_starting_position)

    # Assert
    assert result is None
    assert movement.get_player_position() == new_starting_position


def test_reset_when_given_no_starting_position_previous_map_dimensions_are_used() -> None:
    # Arrange
    starting_position = (1, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position)

    # Act
    result = movement.reset()

    # Assert
    assert result is None
    assert movement.get_player_position() == starting_position


def test_reset_when_given_valid_seed_keeps_tile_order_consistent() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    seed = 42
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    second_tile_id = 2
    movement = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                       randomizer_seed=seed)
    movement.move_player(move_game_mode, move_direction)
    tile_data_one = movement.get_tile_data()

    # Act
    result = movement.reset(randomizer_seed=seed)
    movement.move_player(move_game_mode, move_direction)
    tile_data_two = movement.get_tile_data()

    # Assert
    assert result is None
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_one)
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_two)


def test_reset_clears_all_discovered_tiles() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=42)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    result = movement.reset()

    # Assert
    assert len(movement.get_tile_data()) == 1
    assert result is None


def test_reset_clears_all_zombies() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=42)
    movement.add_zombies(3)

    # Act
    result = movement.reset()

    # Assert
    assert movement.get_zombie_count() == 0
    assert result is None


def test_move_player_when_given_move_mode_valid_move_to_empty_tile_returns_placement_mode() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    placement_game_mode = GameMode.PLACEMENT

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() == placement_game_mode


def test_move_player_when_given_move_mode_valid_move_to_known_tile_returns_none_and_moves_player() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    new_player_position = (2, 1)
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.SOUTH)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() is None
    assert movement.get_player_position() == new_player_position


def test_move_player_when_given_combat_mode_valid_move_to_known_tile_returns_flee_mode_and_moves_player() -> None:
    # Arrange
    new_player_position = (2, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
    combat_game_mode = GameMode.COMBAT
    move_direction = Direction.SOUTH
    flee_mode = GameMode.FLED
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(combat_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() == flee_mode
    assert movement.get_player_position() == new_player_position


def test_move_player_when_given_zombie_door_mode_valid_move_to_empty_tile_creates_zombie_door_in_correct_direction() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    zombie_door_game_mode = GameMode.ZOMBIE_DOOR
    move_direction = Direction.EAST
    second_tile_id = 5
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(zombie_door_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() is None
    assert any(tile.id == second_tile_id and tile.zombie_door == move_direction for tile in movement.get_tile_data())


def test_move_player_when_given_zombie_door_mode_valid_move_to_empty_tile_adds_zombies_to_current_tile() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    zombie_door_game_mode = GameMode.ZOMBIE_DOOR
    move_direction = Direction.EAST
    zombie_count = 3
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(zombie_door_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() is None
    assert movement.get_zombie_count() == zombie_count


def test_need_zombie_door_when_normal_door_open_to_empty_tile_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_need_zombie_door_when_no_normal_door_open_to_empty_tile_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_only_normal_door_open_points_to_out_of_bounds_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 2), randomizer_seed=42)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_only_open_door_is_exit_door_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 2), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_no_open_normal_door_and_all_insides_explored_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=4)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_need_zombie_door_when_no_open_normal_door_and_all_outsides_explored_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_rotate_placement_tile_doors_are_rotated_and_returns_none() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=42)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    second_tile_id = 2
    first_rotation_direction = Direction.WEST
    second_rotation_direction = Direction.SOUTH

    # Act
    tile_data_one = movement.get_tile_data()
    rotate_result = movement.rotate_placement_tile(GameMode.PLACEMENT)
    tile_data_two = movement.get_tile_data()

    # Assert
    assert rotate_result is None
    assert any(tile.id == second_tile_id and tile.rotation == first_rotation_direction for tile in tile_data_one)
    assert any(tile.id == second_tile_id and tile.rotation == second_rotation_direction for tile in tile_data_two)


def test_rotate_placement_tile_rotated_exit_door_transition_is_not_blocked() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    second_tile_id = 3
    first_rotation_direction = Direction.NORTH
    second_rotation_direction = Direction.EAST
    third_rotation_direction = Direction.NORTH

    # Act
    tile_data_one = movement.get_tile_data()
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    tile_data_two = movement.get_tile_data()
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    tile_data_three = movement.get_tile_data()

    # Assert
    assert any(tile.id == second_tile_id and tile.rotation == first_rotation_direction for tile in tile_data_one)
    assert any(tile.id == second_tile_id and tile.rotation == second_rotation_direction for tile in tile_data_two)
    assert any(tile.id == second_tile_id and tile.rotation == third_rotation_direction for tile in tile_data_three)


def test_rotate_placement_tile_rotated_entry_door_transition_aligns_with_exit() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    third_tile_id = 11
    rotation_direction = Direction.EAST

    # Act
    tile_data_one = movement.get_tile_data()
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    tile_data_two = movement.get_tile_data()

    # Assert
    assert any(tile.id == third_tile_id and tile.rotation == rotation_direction for tile in tile_data_one)
    assert any(tile.id == third_tile_id and tile.rotation == rotation_direction for tile in tile_data_two)


def test_lock_placement_tile_is_locked_and_returns_none() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    second_tile_id = 3

    # Act
    lock_result = movement.lock_placement_tile(GameMode.PLACEMENT)
    tile_data = movement.get_tile_data()

    # Assert
    assert lock_result is None
    assert any(tile.id == second_tile_id and tile.is_locked for tile in tile_data)


def test_lock_placement_tile_player_is_moved() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(1, 4), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    player_position = (1, 3)

    # Act
    movement.lock_placement_tile(GameMode.PLACEMENT)
    result = movement.get_player_position()

    # Assert
    assert result == player_position


def test_get_tile_effect_returns_current_tile_effect() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=2)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    tile_effect = TileEffect.FIND_TOTEM

    # Act
    effect_result = movement.get_tile_effect()

    # Assert
    assert effect_result == tile_effect


def test_get_tile_effect_returns_tile_effect_none_if_no_effect() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=42)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    tile_effect = TileEffect.NONE

    # Act
    effect_result = movement.get_tile_effect()

    # Assert
    assert effect_result == tile_effect


def test_defeat_zombies_removes_all_zombies_only_on_current_tile() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=42)
    first_tile_z_count = 4
    second_tile_z_count = 0
    move_direction = Direction.SOUTH
    movement.add_zombies(first_tile_z_count)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.add_zombies(first_tile_z_count)

    # Act
    movement.defeat_zombies()
    second_tile_z_result = movement.get_zombie_count()
    movement.move_player(GameMode.MOVE, move_direction)
    first_tile_z_result = movement.get_zombie_count()

    # Assert
    assert first_tile_z_result == first_tile_z_count
    assert second_tile_z_result == second_tile_z_count


# ========================== Bad Day ========================== #


@pytest.mark.parametrize("game_mode", [GameMode.PLACEMENT, GameMode.FLED, "PLAYING", -1000, ()])
def test_move_player_when_given_invalid_game_mode_returns_game_mode_error(game_mode) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    move_direction = Direction.NORTH
    game_mode_error = ErrorCode.INVALID_VALUE_GAME_MODE

    # Act
    move_result = movement.move_player(game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == game_mode_error


@pytest.mark.parametrize("direction", ["UP", -1000, ()])
def test_move_player_when_given_invalid_direction_returns_direction_error(direction) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    game_mode = GameMode.MOVE
    direction_error = ErrorCode.INVALID_VALUE_DIRECTION

    # Act
    move_result = movement.move_player(game_mode, direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == direction_error


@pytest.mark.parametrize("mode", [GameMode.MOVE, GameMode.COMBAT, GameMode.ZOMBIE_DOOR])
def test_move_player_when_given_all_valid_modes_invalid_move_out_of_bounds_returns_out_of_bounds_error(mode) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 0))
    move_direction = Direction.NORTH
    out_of_bounds_error = ErrorCode.INVALID_MOVE_OUT_OF_BOUNDS

    # Act
    move_result = movement.move_player(mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == out_of_bounds_error


def test_move_player_when_given_move_mode_invalid_move_to_empty_tile_with_no_door_returns_door_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    move_game_mode = GameMode.MOVE
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == door_error


def test_move_player_when_given_move_mode_invalid_move_to_known_tile_with_no_door_returns_door_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.WEST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == door_error


def test_move_player_when_given_move_mode_invalid_move_to_cross_area_tile_returns_cross_area_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.EAST
    cross_area_error = ErrorCode.INVALID_MOVE_ACROSS_AREAS
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.WEST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == cross_area_error


def test_move_player_when_given_move_mode_valid_move_when_all_inside_explored_returns_depleted_inside_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=4)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.EAST
    depleted_inside_error = ErrorCode.DEPLETED_INSIDE_TILES
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == depleted_inside_error


def test_move_player_when_given_move_mode_valid_move_when_all_outside_explored_returns_depleted_outside_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(4, 5), starting_position=(0, 4), randomizer_seed=1)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    depleted_outside_error = ErrorCode.DEPLETED_OUTSIDE_TILES
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == depleted_outside_error


def test_move_player_when_given_combat_mode_invalid_move_to_empty_tile_returns_flee_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
    combat_game_mode = GameMode.COMBAT
    move_direction = Direction.EAST
    flee_error = ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(combat_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == flee_error


def test_move_player_when_given_combat_mode_invalid_move_to_known_tile_with_no_door_returns_door_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    combat_game_mode = GameMode.COMBAT
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.rotate_placement_tile(GameMode.PLACEMENT)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(combat_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == door_error


def test_move_player_when_given_combat_mode_invalid_move_to_cross_area_tile_returns_cross_area_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
    combat_game_mode = GameMode.COMBAT
    move_direction = Direction.EAST
    cross_area_error = ErrorCode.INVALID_MOVE_ACROSS_AREAS
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.WEST)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(combat_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == cross_area_error


def test_move_player_when_given_zombie_door_mode_invalid_move_to_know_tile_returns_zombie_door_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    zombie_door_game_mode = GameMode.ZOMBIE_DOOR
    move_direction = Direction.SOUTH
    zombie_door_error = ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(zombie_door_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == zombie_door_error


@pytest.mark.parametrize("game_mode", [GameMode.MOVE, GameMode.FLED, "PLAYING", -1000, (), None])
def test_rotate_placement_tile_when_given_invalid_mode_returns_mode_error(game_mode):
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    mode_error = ErrorCode.INVALID_MODE_ROTATE_TILE

    # Act
    rotate_result = movement.rotate_placement_tile(game_mode)

    # Assert
    assert rotate_result == mode_error


def test_rotate_placement_tile_rotating_a_locked_tile_returns_rotate_tile_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    rotate_tile_error = ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE
    placement_mode = GameMode.PLACEMENT

    # Act
    rotate_result = movement.rotate_placement_tile(placement_mode)

    # Assert
    assert rotate_result == rotate_tile_error


@pytest.mark.parametrize("game_mode", [GameMode.MOVE, GameMode.FLED, "PLAYING", -1000, (), None])
def test_lock_placement_tile_when_given_invalid_mode_returns_mode_error(game_mode) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    mode_error = ErrorCode.INVALID_MODE_LOCK_TILE

    # Act
    rotate_result = movement.lock_placement_tile(game_mode)

    # Assert
    assert rotate_result == mode_error


@pytest.mark.parametrize("map_dimensions", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_init_when_given_invalid_map_dimensions_type_raises_type_error(map_dimensions: tuple[int, int]) -> None:
    # Arrange
    starting_position = (2, 2)

    # Act & Assert
    with pytest.raises(TypeError, match="Invalid map dimensions type, must be a tuple of two integers"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("map_dimensions", [(0, 0), (-1, 3), (5, -1), (1, 1)])
def test_init_when_given_invalid_map_dimensions_value_raises_value_error(map_dimensions: tuple[int, int]) -> None:
    # Arrange
    starting_position = (2, 2)

    # Act & Assert
    with pytest.raises(ValueError, match="Map dimensions must be greater than 4x4"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("starting_position", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_init_when_given_invalid_starting_position_type_raises_type_error(starting_position: tuple[int, int]) -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act & Assert
    with pytest.raises(TypeError, match="Invalid starting position type, must be a tuple of two integers"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("starting_position", [(-1, 3), (5, -1), (4, 5)])
def test_init_when_given_invalid_starting_position_value_raises_value_error(starting_position: tuple[int, int]) -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act & Assert
    with pytest.raises(ValueError, match="Starting position must be within the map dimensions"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


def test_init_when_given_invalid_randomizer_seed_value_raises_value_error() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    invalid_seed = "42"

    # Act & Assert
    with pytest.raises(TypeError, match="Randomizer seed must be an integer"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position, randomizer_seed=invalid_seed)


@pytest.mark.parametrize("map_dimensions", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_reset_when_given_invalid_map_dimensions_returns_map_dimensions_type_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_TYPE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("map_dimensions", [(0, 0), (-1, 3), (5, -1), (3, 4)])
def test_reset_when_given_invalid_map_dimensions_returns_map_dimensions_value_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(2, 1), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_VALUE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("map_dimensions", [(2, 2), (2, 4), (4, 2), (4, 4)])
def test_reset_when_given_invalid_map_dimensions_with_existing_starting_position_returns_map_dimensions_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 4), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_VALUE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("starting_position", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_reset_when_given_invalid_starting_position_returns_starting_position_type_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_TYPE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("starting_position", [(-1, 3), (4, -1), (1, 5), (5, 1)])
def test_reset_when_given_invalid_starting_position_returns_starting_position_value_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("starting_position", [(6, 6), (2, 6), (6, 2), (5, 5)])
def test_reset_when_given_invalid_starting_position_with_existing_map_dimensions_returns_starting_position_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("map_dimensions, starting_position",
                         [((4, 4), (2, 4)), ((4, 4), (4, 2)), ((3, 3), (2, 2)), ((4, 4), (-1, -1))])
def test_reset_when_given_invalid_starting_position_and_map_dimensions_returns_starting_position_error(
        map_dimensions: tuple[int, int], starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(map_dimensions=map_dimensions, starting_position=starting_position)

    # Assert
    assert result == starting_position_error


def test_reset_when_given_invalid_randomizer_seed_value_returns_randomizer_seed_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    invalid_seed = "42"
    randomizer_seed_error = ErrorCode.INVALID_TYPE_RANDOMIZER_SEED

    # Act
    result = movement.reset(randomizer_seed=invalid_seed)

    # Assert
    assert result == randomizer_seed_error
