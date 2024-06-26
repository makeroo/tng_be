from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .types import PlayerColor, Direction, Position, FallDirection


class MoveType(str, Enum):
    place_tile = "place_tile"
    rotate_tile = "rotate_tile"
    stay = "stay"
    crawl = "crawl"
    fall = "fall"  # select either row or column
    land = "land"  # return on board
    # TODO pass_key = "pass_key"
    # TODO block = "block" # drop just 2 tiles instead of three, spending 1 nerve
    # TODO charge = "charge" # move into a monster
    # TODO sustain = "sustain" # during final flickers do not consume a tile, spending 1 nerve


class PlaceTile(BaseModel):
    """
    Draw a tile from the tile holder and place on board.
    """

    move: Literal[MoveType.place_tile]
    pos: Position


class RotateTile(BaseModel):
    """
    Orient the last placed tile on board.
    """

    move: Literal[MoveType.rotate_tile]
    direction: Direction


class Stay(BaseModel):
    move: Literal[MoveType.stay]


class Crawl(BaseModel):
    move: Literal[MoveType.crawl]
    direction: Direction


class Fall(BaseModel):
    move: Literal[MoveType.fall]
    direction: FallDirection


class Land(BaseModel):
    move: Literal[MoveType.land]
    place: int


class Move(BaseModel):
    player: PlayerColor
    param: PlaceTile | RotateTile | Stay | Crawl | Fall | Land = Field(discriminator='move')
