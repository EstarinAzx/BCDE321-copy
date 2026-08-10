import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.movement.map import Movement
from zimp.domain.movement.direction import Direction
from zimp.support.fake_game_mode import GameMode


# ========================== Good Day ========================== #


def test_when_move_mode_valid_move_to_empty_tile_returns_placement_mode():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2))
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    placement_game_mode = GameMode.PLACEMENT

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is False
    assert move_result.get_data() == placement_game_mode


def test_when_move_mode_valid_move_to_known_tile_moves_player():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_game_mode = GameMode.MOVE
    move_direction = Direction.NORTH
    new_player_position = (1, 2)
    movement.move_player(move_game_mode, Direction.NORTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)
    movement.move_player(move_game_mode, Direction.SOUTH)
    movement.lock_placement_tile(GameMode.PLACEMENT)

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_data() is None
    assert movement.get_player_position() == new_player_position


def test_when_combat_mode_valid_move_to_known_tile_returns_flee_mode():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
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


def test_when_zombie_door_mode_valid_move_to_empty_tile_creates_zombie_door_in_correct_direction():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
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


def test_when_zombie_door_mode_valid_move_to_empty_tile_adds_zombies_to_current_tile():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
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


# ========================== Bad Day ========================== #


def test_when_move_mode_invalid_move_to_empty_tile_with_no_door_returns_door_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2))
    move_game_mode = GameMode.MOVE
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR

    # Act
    move_result = movement.move_player(move_game_mode, move_direction)

    # Assert
    assert move_result.is_fail() is True
    assert move_result.get_error_code() == door_error


def test_when_move_mode_invalid_move_to_known_tile_with_no_door_returns_door_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
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


def test_when_move_mode_invalid_move_to_cross_area_tile_returns_cross_area_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
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


def test_when_combat_mode_invalid_move_to_empty_tile_returns_flee_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
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


def test_when_combat_mode_invalid_move_to_known_tile_with_no_door_returns_door_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
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


def test_when_combat_mode_invalid_move_to_cross_area_tile_returns_cross_area_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
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


def test_when_zombie_door_mode_invalid_move_to_know_tile_returns_zombie_door_error():
    # Arrange
    movement = Movement(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
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
