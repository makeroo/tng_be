from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .types import PlayerColor, Direction, Position, FallDirection


class MoveType(str, Enum):
    place_tile = "place_tile"
    rotate_tile = "rotate_tile"
    stay = "stay"
    crawl = "crawl"
    fall = "fall"  # ie. select either row or column
    land = "land"  # return on board
    # TODO pass key
    # TODO block, ie. drop just 2 tiles instead of three (spending 1 nerve)
    # TODO charge (ie. move into a monster)
    # TODO sustain (ie. during final flickers do not consume a tile, spending 1 nerve)


class PlaceTile(BaseModel):
    move: Literal[MoveType.place_tile]
    pos: Position


class RotateTile(BaseModel):
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
