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
    pass_key = "pass_key"
    block = "block"  # drop just 2 tiles instead of three, spending 1 nerve
    charge = "charge"  # move into a monster
    spend_nerve = "spend_nerve"
    discard_tile = "discard_tile"  # last action of the turn during the final flickers


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


class PassKey(BaseModel):
    move: Literal[MoveType.pass_key]
    player: PlayerColor


class Block(BaseModel):
    move: Literal[MoveType.block]


class Charge(BaseModel):
    move: Literal[MoveType.charge]
    direction: Direction


class SpendNerve(BaseModel):
    move: Literal[MoveType.spend_nerve]


class DiscardTile(BaseModel):
    move: Literal[MoveType.discard_tile]
    pos: Position


class Move(BaseModel):
    player: PlayerColor
    param: (
        PlaceTile
        | RotateTile
        | Stay
        | Crawl
        | Fall
        | Land
        | PassKey
        | Block
        | Charge
        | SpendNerve
        | DiscardTile
    ) = Field(discriminator='move')
