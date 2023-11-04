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
    o = "o"


class Tile(Enum):
    start = "start"
    key = "key"
    gate = "gate"
    wax_eater = "wax_eater"
    straight_passage = "straight_passage"
    t_passage = "t_passage"
    four_way_passage = "four_way_passage"

    pit = "pit"
