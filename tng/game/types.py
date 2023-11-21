from enum import Enum
from typing import NamedTuple


class PlayerColor(Enum):
    red = "red"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"


class Position(NamedTuple):
    x: int
    y: int

    def idx(self, edge_length: int) -> int:
        return self.y * edge_length + self.x

    def add(self, dx: int, dy: int, edge_length: int) -> 'Position':
        return Position((self.x + dx) % edge_length, (self.y + dy) % edge_length)


class Direction(Enum):
    n = "n"
    e = "e"
    s = "s"
    w = "w"

    def rotate(self, d: 'Direction') -> 'Direction':
        new_index = (direction_index[self] + direction_index[d]) % 4

        return all_directions[new_index]

    def neighbor(self, pos: Position, edge_length: int) -> Position:
        dx, dy = neighbors[self]

        return pos.add(dx, dy, edge_length)


class FallDirection(Enum):
    row = 'row'
    column = 'column'


all_directions = [d for d in Direction]
direction_index = {d: idx for idx, d in enumerate(Direction)}
neighbors = {
    Direction.n: (0, -1),
    Direction.e: (+1, 0),
    Direction.s: (0, +1),
    Direction.w: (-1, 0),
}

connected_to = {
    Direction.n: Direction.s,
    Direction.e: Direction.w,
    Direction.s: Direction.n,
    Direction.w: Direction.e,
}


class Tile(Enum):
    start = "start"
    key = "key"
    gate = "gate"
    wax_eater = "wax_eater"
    straight_passage = "straight_passage"
    t_passage = "t_passage"
    four_way_passage = "four_way_passage"

    pit = "pit"


is_crumbling = {
    Tile.start: True,
    Tile.key: True,
    Tile.gate: False,
    Tile.wax_eater: False,
    Tile.straight_passage: True,
    Tile.t_passage: False,
    Tile.four_way_passage: False,
    Tile.pit: False,
}

is_monster = {
    Tile.start: False,
    Tile.key: False,
    Tile.gate: False,
    Tile.wax_eater: True,
    Tile.straight_passage: False,
    Tile.t_passage: False,
    Tile.four_way_passage: False,
    Tile.pit: False,
}

open_directions = {
    Tile.start: [Direction.s, Direction.w],
    Tile.key: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.gate: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.wax_eater: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.straight_passage: [Direction.n, Direction.s],
    Tile.t_passage: [Direction.e, Direction.s, Direction.w],
    Tile.four_way_passage: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.pit: [Direction.n, Direction.e, Direction.s, Direction.w],
}
