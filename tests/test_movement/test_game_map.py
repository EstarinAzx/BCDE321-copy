import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.movement.game_map import GameMap
from zimp.domain.movement.direction import Direction
from zimp.support.fake_game_mode import GameMode


# ========================== Good Day ========================== #


def test_init_when_given_valid_map_dimensions_sets_map_size() -> None:
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


def test_reset_when_given_valid_map_dimensions_sets_map_size() -> None:
    # Arrange
    new_map_dimensions = (4, 4)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))

    # Act
    result = movement.reset(map_dimensions=new_map_dimensions)

    # Assert
    assert result is None
    assert movement.get_map_dimensions() == new_map_dimensions


def test_reset_when_given_no_map_dimensions_no_change_occurs() -> None:
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


def test_reset_when_given_no_starting_position_no_change_occurs() -> None:
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


def test_move_player_when_given_move_mode_valid_move_to_empty_tile_returns_placement_mode():
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


def test_move_player_when_given_move_mode_valid_move_to_known_tile_moves_player():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    new_player_position = (1, 2)
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.SOUTH)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() is None
    assert movement.get_player_position() == new_player_position


def test_move_player_when_given_combat_mode_valid_move_to_known_tile_returns_flee_mode():
    # Arrange
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


def test_move_player_when_given_zombie_door_mode_valid_move_to_empty_tile_creates_zombie_door_in_correct_direction():
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


def test_move_player_when_given_zombie_door_mode_valid_move_to_empty_tile_adds_zombies_to_current_tile():
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


def test_need_zombie_door_when_normal_door_open_to_empty_tile_returns_false():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_need_zombie_door_when_no_normal_door_open_to_empty_tile_returns_true():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_only_normal_door_open_points_to_out_of_bounds_returns_true():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 0), randomizer_seed=42)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_only_open_door_is_exit_door_returns_true():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 0), randomizer_seed=1)
    movement.move_player(GameMode.MOVE, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(GameMode.MOVE, Direction.EAST)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_no_open_normal_door_and_all_insides_explored_returns_false():
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 0), randomizer_seed=4)
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


def test_need_zombie_door_when_no_open_normal_door_and_all_outsides_explored_returns_false():
    # Arrange
    movement = GameMap(map_dimensions=(5, 3), starting_position=(4, 0), randomizer_seed=1)
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


# ========================== Bad Day ========================== #


def test_move_player_when_given_move_mode_invalid_move_to_empty_tile_with_no_door_returns_door_error():
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


def test_move_player_when_given_move_mode_invalid_move_to_known_tile_with_no_door_returns_door_error():
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


def test_move_player_when_given_move_mode_invalid_move_to_cross_area_tile_returns_cross_area_error():
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


def test_move_player_when_given_combat_mode_invalid_move_to_empty_tile_returns_flee_error():
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


def test_move_player_when_given_combat_mode_invalid_move_to_known_tile_with_no_door_returns_door_error():
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


def test_move_player_when_given_combat_mode_invalid_move_to_cross_area_tile_returns_cross_area_error():
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


def test_move_player_when_given_zombie_door_mode_invalid_move_to_know_tile_returns_zombie_door_error():
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
