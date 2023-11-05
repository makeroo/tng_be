from typing import NamedTuple

from .types import Tile, Direction, PlayerColor


class Cell(NamedTuple):
    tile: Tile | None
    direction: Direction
    players: list[PlayerColor]


class Board(NamedTuple):
    cells: list[Cell]
    edge_length: int  # can be 6 (up to 4 players) or 7 (5 players)


class Player(NamedTuple):
    color: PlayerColor

    has_key: bool
    nerves: int
    has_light: bool

    # player position:
    # both None -> initial turn, not yet on map
    # both int -> on map
    # only one int -> falling
    x: int | None
    y: int | None


class Phase(Enum):
    place_start = 0
    rotate_start = 1
    discover_tiles = 2
    rotate_tile = 3


class Game(NamedTuple):
    board: Board
    tile_holder: list[Tile]
    draw_index: int  # index in the tile_holder deck

    players: list[Player]

    turn: int  # index in the players array

    phase: Phase
