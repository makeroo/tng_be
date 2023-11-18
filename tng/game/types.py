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

Direction.n.connected_to = Direction.s
Direction.e.connected_to = Direction.w
Direction.s.connected_to = Direction.n
Direction.w.connected_to = Direction.e


class Tile(Enum):
    start = "start"
    key = "key"
    gate = "gate"
    wax_eater = "wax_eater"
    straight_passage = "straight_passage"
    t_passage = "t_passage"
    four_way_passage = "four_way_passage"

    pit = "pit"


for t, dirs in {
    Tile.start: [Direction.s, Direction.w],
    Tile.key: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.gate: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.wax_eater: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.straight_passage: [Direction.n, Direction.s],
    Tile.t_passage: [Direction.e, Direction.s, Direction.w],
    Tile.four_way_passage: [Direction.n, Direction.e, Direction.s, Direction.w],
    Tile.pit: [Direction.n, Direction.e, Direction.s, Direction.w],
}.items():
    t.open_directions = dirs
