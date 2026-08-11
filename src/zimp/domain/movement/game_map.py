import random

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.movement.direction import Direction
from zimp.domain.movement.tile import Tile
from zimp.domain.movement.tile_data import TileData
from zimp.domain.movement.tile_effect import TileEffect
from zimp.support.fake_game_mode import GameMode


class GameMap:
    """GameMap class used to hold and calculate tile placement and player movement data."""

    def __init__(self, map_dimensions: tuple[int, int], starting_position: tuple[int, int],
                 randomizer_seed: int | None = None) -> None:
        self.__map_dimensions: tuple[int, int] = map_dimensions
        self.__starting_position: tuple[int, int] = starting_position
        self.__randomizer_seed: int | None = randomizer_seed
        self.__display_tiles: dict[tuple[int, int], Tile] = {}
        self.__player_position: tuple[int, int]
        # tile addition details
        self.__inside_tile_order: list[int]
        self.__outside_tile_order: list[int]
        self.__inside_tile_order_index: int
        self.__outside_tile_order_index: int
        self.__player_is_outside: bool
        # tile placement details
        self.__last_added_tile: Tile
        self.__last_move_direction: Direction
        self.__last_move_destination_position: tuple[int, int]

        # tile details
        self.__inside_tile_details = {
            1: Tile(1, (Direction.NORTH,)),
            2: Tile(2, (Direction.NORTH, Direction.WEST)),
            3: Tile(3, (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST), is_exit_tile=True),
            4: Tile(4, (Direction.NORTH, Direction.EAST, Direction.WEST)),
            5: Tile(5, (Direction.NORTH,)),
            6: Tile(6, (Direction.NORTH, Direction.EAST, Direction.WEST), TileEffect.HEALTH),
            7: Tile(7, (Direction.NORTH,), TileEffect.SEARCH),
            8: Tile(8, (Direction.EAST, Direction.WEST), TileEffect.FIND_TOTEM)
        }
        self.__outside_tile_details = {
            1: Tile(9, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            2: Tile(10, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            3: Tile(11, (Direction.NORTH, Direction.EAST, Direction.SOUTH), is_outside_tile=True, is_entry_tile=True),
            4: Tile(12, (Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            5: Tile(13, (Direction.EAST, Direction.SOUTH, Direction.WEST), TileEffect.HEALTH, is_outside_tile=True),
            6: Tile(14, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            7: Tile(15, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            8: Tile(16, (Direction.EAST, Direction.SOUTH), TileEffect.BURY_TOTEM, is_outside_tile=True)
        }

        # setup map
        self.__setup()

    def __setup(self) -> None:
        """Sets up the game map."""
        self.__inside_tile_order_index = 0
        self.__outside_tile_order_index = 0
        self.__player_is_outside = False
        self.__player_position = self.__starting_position
        self.__shuffle_tiles()
        self.__add_tile(self.__starting_position)  # add start tile
        self.__display_tiles[self.__starting_position].lock()  # lock first tile

    def __shuffle_tiles(self) -> None:
        """Shuffles order of inside/outside tiles."""
        random.seed(self.__randomizer_seed)
        inside_random_order = random.sample(range(1, 9), k=8)
        outside_random_order = random.sample(range(1, 9), k=8)

        # add inside/outside starting tiles to start of list
        inside_start_tile_index = 1
        outside_start_tile_index = 3
        inside_random_order.remove(inside_start_tile_index)
        outside_random_order.remove(outside_start_tile_index)
        inside_random_order.insert(0, inside_start_tile_index)
        outside_random_order.insert(0, outside_start_tile_index)
        self.__inside_tile_order = inside_random_order
        self.__outside_tile_order = outside_random_order

    def __add_tile(self, position: tuple[int, int]) -> ErrorCode | None:
        """Adds next tile to the displayed tiles.
        Args:
            position (tuple[int, int]): Position to add.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        if self.__player_is_outside:
            # gets next outside tile if player is outside
            index = self.__outside_tile_order[self.__outside_tile_order_index]
            new_tile = self.__outside_tile_details.get(index)
            self.__outside_tile_order_index += 1
        else:
            # gets next inside tile if player is inside
            index = self.__inside_tile_order[self.__inside_tile_order_index]
            new_tile = self.__inside_tile_details.get(index)
            self.__inside_tile_order_index += 1

        # error if no new tile
        if new_tile is None:
            return ErrorCode.FATAL_ERROR

        # add tile using position as key
        self.__display_tiles[position] = new_tile
        self.__last_added_tile = new_tile
        return None

    def __is_position_valid(self, position: tuple[int, int]) -> bool:
        """Checks if the given position is within the maps dimensions.
        Args:
            position (tuple[int, int]): Position to check.
        Returns:
            bool: True if the given position is within the maps dimensions, False if not.
        """
        if (position[0] < 0 or position[1] < 0 or position[0] >= self.__map_dimensions[0]
                or position[1] >= self.__map_dimensions[1]):
            return False  # position is invalid
        else:
            return True  # position is valid

    def __update_player_area(self, move_direction: Direction, current_tile: Tile) -> None:
        """Updates player area if transitioning between inside/outside areas through the entry/exit doors.
        Args:
            move_direction (Direction): Direction player is moving towards.
            current_tile (Tile): The tile the player is currently on.
        """
        # entry/exit have transition in north door
        moving_through_transition_door = move_direction == current_tile.get_rotation()
        if current_tile.is_exit() and moving_through_transition_door:
            self.__player_is_outside = True
        elif current_tile.is_entry() and moving_through_transition_door:
            self.__player_is_outside = False

    def __is_exit_clear(self, new_tile_direction: Direction) -> bool:
        """Checks if the exit tiles transition door (NORTH) points to an empty tile.
        Args:
            new_tile_direction (Direction): Direction the tile is rotated.
        Returns:
            bool: True if not the exit tile or the transition door points to an empty tile, False if not.
        """
        if not self.__last_added_tile.is_exit():
            return True  # if the tile is not an exit tile no need to check

        # get the position the exit tile arrow is pointing at
        next_tile_pos_result = self.__calculate_position(self.__last_move_destination_position, new_tile_direction)
        if next_tile_pos_result.is_fail():
            return False  # cant point to invalid position

        if self.__display_tiles.get(next_tile_pos_result.get_data()) is not None:
            return False  # exit arrow cant point to existing tile
        else:
            return True  # exit arrow pointing at blank tile

    def __is_entry_aligned(self, new_tile_direction: Direction) -> bool:
        """Checks if the entry tiles transition door (NORTH) points at the exit tile.
        Args:
            new_tile_direction (Direction): Direction the tile is rotated.
        Returns:
            bool: True if not the entry tile or the transition door points at anything other than the exit tile, False otherwise.
        """
        if not self.__last_added_tile.is_entry():
            return True  # if the tile is not an entry tile no need to check

        # get the position the entry tile arrow is pointing at
        next_tile_pos_result = self.__calculate_position(self.__last_move_destination_position, new_tile_direction)
        if next_tile_pos_result.is_fail():
            return False  # cant point to invalid position

        past_tile = self.__display_tiles.get(next_tile_pos_result.get_data())
        if past_tile is None or not past_tile.is_exit():
            return False  # entry arrow cant point to blank tile or tile that is NOT the exit
        else:
            return True  # entry arrow pointing at exit tile

    def __calculate_placement_tile_rotation(self) -> None:
        """Rotates new tile until doors are aligned."""
        original_rotation = self.__last_added_tile.get_rotation()

        # loop through each direction and rotate tile
        for i in range(4):
            new_tile_direction = Direction((original_rotation.value + (90 * i)) % 360)
            self.__last_added_tile.rotate(new_tile_direction)
            if self.__last_added_tile.has_door_in_opposite_direction(self.__last_move_direction):
                # if doors align check for entry and exit
                if not self.__is_exit_clear(new_tile_direction):
                    continue  # if exit is not clear then try new rotation
                if not self.__is_entry_aligned(new_tile_direction):
                    continue  # if entry is not aligned try new rotation
                break

    def __setup_placement_tile(self, move_direction: Direction, current_tile: Tile,
                               destination_position: tuple[int, int]) -> ErrorCode | None:
        """Adds next tile and sets up its rotation.
        Args:
            move_direction (Direction): Direction player is moving towards.
            current_tile (Tile): The tile the player is currently on.
            destination_position (tuple[int, int]): Position the player is moving towards.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        # check if player is transitioning between areas and add tile
        self.__update_player_area(move_direction, current_tile)
        add_error = self.__add_tile(destination_position)
        if add_error is not None:
            return add_error

        # save direction, position, and calculate new tile rotation
        self.__last_move_direction = move_direction
        self.__last_move_destination_position = destination_position
        self.__calculate_placement_tile_rotation()
        return None

    def __calculate_position(self, position: tuple[int, int], direction: Direction) -> Result:
        """Calculates the new position from the given position to the given direction.
        Args:
            position (tuple[int, int]): Current position.
            direction (Direction): Direction from the current position to the new position.
        Returns:
            Result: Success - new position. | Fail - ErrorCode.
        """
        # calculate new position
        new_pos: tuple[int, int]
        match direction:
            case Direction.NORTH:
                new_pos = (position[0] - 1, position[1])
            case Direction.SOUTH:
                new_pos = (position[0] + 1, position[1])
            case Direction.WEST:
                new_pos = (position[0], position[1] - 1)
            case _:
                new_pos = (position[0], position[1] + 1)

        # validates new position
        if not self.__is_position_valid(new_pos):
            return Result.fail(ErrorCode.INVALID_MOVE_OUT_OF_BOUNDS)

        return Result.success(new_pos)

    def __is_move_valid(self, current_tile: Tile, destination_tile: Tile, direction: Direction) -> ErrorCode | None:
        """Checks both tiles have aligned doors, the move is through the transition doors or both tiles are inside/outside.
        Args:
            current_tile (Tile): Current tile the player is on.
            destination_tile (Tile): Destination tile the player is trying to move to.
            direction (Direction): Direction from the current tile to the destination tile.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        doors_align = (current_tile.has_door_in_direction(direction)
                       and destination_tile.has_door_in_opposite_direction(direction))
        is_move_between_connection = ((current_tile.is_exit() and destination_tile.is_entry())
                                      or (destination_tile.is_exit() and current_tile.is_entry()))
        is_same_area = current_tile.is_outside() == destination_tile.is_outside()

        if not doors_align:
            return ErrorCode.INVALID_MOVE_NO_DOOR
        elif not (is_move_between_connection or is_same_area):
            return ErrorCode.INVALID_MOVE_ACROSS_AREAS
        else:
            return None  # valid move

    def __create_zombie_door(self, direction: Direction) -> None:
        """Creates zombie door on the current tile and adds zombies.
        Args:
            direction (Direction): Direction of zombie door.
        """
        self.__last_added_tile.add_zombie_door(direction)
        self.add_zombies(3)

    def __handle_move_to_blank_tile(self, direction: Direction, current_tile: Tile,
                                    destination_position: tuple[int, int]) -> ErrorCode | None:
        """Handles move to blank tile.
        Args:
            direction (Direction): Direction player is trying to move.
            current_tile (Tile): Current tile the player is on.
            destination_position (tuple[int, int]): Position the player is trying to move to.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        if current_tile.has_door_in_direction(direction):
            # door opens in direction
            setup_place_error = self.__setup_placement_tile(direction, current_tile, destination_position)
            if setup_place_error is not None:
                return setup_place_error  # return error
            return None  # no error - need placement mode
        else:
            return ErrorCode.INVALID_MOVE_NO_DOOR  # no door opens in direction

    def __handle_move_to_known_tile(self, direction: Direction, destination_tile: Tile, current_tile: Tile,
                                    destination_position: tuple[int, int]) -> ErrorCode | None:
        """Handles move to known tile.
        Args:
            direction (Direction): Direction player is trying to move.
            destination_tile (Tile): Destination tile the player is trying to move to.
            current_tile (Tile): Current tile the player is on.
            destination_position (tuple[int, int]): Position the player is trying to move to.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        move_error = self.__is_move_valid(current_tile, destination_tile, direction)
        if move_error is None:
            # valid move updates player
            self.__update_player_area(direction, current_tile)
            self.__player_position = destination_position
            return None  # no error - move was success
        else:
            return move_error  # invalid move

    def move_player(self, mode: GameMode, direction: Direction) -> Result:
        """Attempts to move the player in the given direction.

        The method does different actions depending on the mode:
        MOVE:
            Sets up tile placement if move is valid and destination is empty.
            Moves player if destination is known and move is valid.
        COMBAT:
            Moves player if destination is known and move is valid.
        ZOMBIE_DOOR:
            Adds zombie door and zombies on the current tile if the move is valid and the destination is empty.

        Args:
            mode (GameMode): Current game mode.
            direction (Direction): Direction the player wants to move.
        Returns:
              Result: Success - Needed GameMode or None. | Fail - ErrorCode.
        """
        # get tile player is currently on
        current_tile = self.__display_tiles.get(self.__player_position)
        if current_tile is None:
            return Result.fail(ErrorCode.FATAL_ERROR)  # tile player is on is missing

        # get new position
        destination_position_result = self.__calculate_position(self.__player_position, direction)
        if destination_position_result.is_fail():
            return destination_position_result  # error when trying to get position

        # get dest position and tile
        destination_position = destination_position_result.get_data()
        destination_tile = self.__display_tiles.get(destination_position)
        match mode:
            case GameMode.MOVE:
                if destination_tile is None:
                    # move to blank tile
                    error = self.__handle_move_to_blank_tile(direction, current_tile, destination_position)
                    if error is not None:
                        return Result.fail(error)  # invalid move
                    else:
                        return Result.success(GameMode.PLACEMENT)  # placement game mode needed
                else:
                    # move to known tile
                    error = self.__handle_move_to_known_tile(direction, destination_tile, current_tile,
                                                             destination_position)
                    if error is not None:
                        return Result.fail(error)  # invalid move
                    else:
                        return Result.success(None)  # successful move no mode needed
            case GameMode.COMBAT:
                if destination_tile is None:
                    return Result.fail(ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE)  # cant flee to unknown tile
                else:
                    # flee to known tile
                    error = self.__handle_move_to_known_tile(direction, destination_tile, current_tile,
                                                             destination_position)
                    if error is not None:
                        return Result.fail(error)  # invalid move
                    else:
                        return Result.success(GameMode.FLED)  # fled game mode needed
            case GameMode.ZOMBIE_DOOR:
                if destination_tile is None:
                    # create zombie door opening to desired destination
                    self.__create_zombie_door(direction)
                    return Result.success(None)  # no mode needed
                else:
                    return Result.fail(ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE)  # cant make door to known tile

    def rotate_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        # cannot rotate if locked
        if self.__last_added_tile.is_locked():
            return ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE

        # rotate tile and calculate next valid rotation
        self.__last_added_tile.rotate(Direction((self.__last_added_tile.get_rotation().value + 90) % 360))
        self.__calculate_placement_tile_rotation()
        return None

    def lock_placement_tile(self, mode: GameMode) -> ErrorCode | None:
        # lock tile placement and move player
        self.__last_added_tile.lock()
        self.__player_position = self.__last_move_destination_position

    def need_zombie_door(self, mode: GameMode) -> bool:
        pass

    def get_tile_data(self) -> list[TileData]:
        """Gets the data for all the tiles being displayed.
        Returns:
            list[TileData]: The tile data.
        """
        data = []
        for position, tile in self.__display_tiles.items():
            data.append(tile.get_data(position))
        return data

    def get_player_position(self) -> tuple[int, int]:
        return self.__player_position

    def get_zombie_count(self) -> int:
        """Gets the number of zombies on the tile the player is currently on.
        Returns:
            int: The number of zombies on the current tile.
        """
        return self.__display_tiles[self.__player_position].get_zombie_count()

    def defeat_zombies(self) -> None:
        pass

    def add_zombies(self, number_of_zombies: int) -> None:
        """Adds zombies to the tile the player is currently on.
        Args:
            number_of_zombies (int): The number of zombies to add.
        """
        self.__display_tiles[self.__player_position].add_zombies(number_of_zombies)

    def get_tile_effect(self) -> TileEffect:
        pass

    def get_map_dimensions(self) -> tuple[int, int]:
        return self.__map_dimensions

    def reset(self, map_dimensions: tuple[int, int] | None = None, starting_position: tuple[int, int] | None = None,
              randomizer_seed: int | None = None) -> ErrorCode | None:
        """Resets the game map.
        Args:
            map_dimensions (tuple[int, int] | None): Optional new map dimensions.
            starting_position (tuple[int, int] | None): Optional new starting position.
            randomizer_seed (int | None): Optional new randomizer seed, no seed will randomize the seed.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        if map_dimensions is not None:
            # set map dimensions
            self.__map_dimensions = map_dimensions

        if starting_position is not None:
            # set new starting pos
            self.__starting_position = starting_position

        # set new seed for tile randomizer
        self.__randomizer_seed = randomizer_seed

        # reset and clear all displayed tiles
        for position, tile in self.__display_tiles.items():
            tile.reset()
        self.__display_tiles.clear()
        self.__setup()
        return None  # reset was success
