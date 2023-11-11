from enum import Enum


class PlayerColor(Enum):
    red = "red"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"


class Direction(Enum):
    n = "n"
    e = "e"
    s = "s"
    w = "w"

    def rotate(self, d: 'Direction') -> 'Direction':
        new_index = (direction_index[self] + direction_index[d]) % 4

        return all_directions[new_index]

    def neighbor(self, x: int, y: int, edge_length: int) -> tuple[int, int]:
        dx, dy = neighbors[self]

        return (x + dx) % edge_length, (y + dy) % edge_length


all_directions = [d for d in Direction]
direction_index = {d: idx for idx, d in enumerate(Direction)}
neighbors = {
    Direction.n: (0, -1),
    Direction.e: (+1, 0),
    Direction.s: (0, +1),
    Direction.w: (-1, 0),
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
