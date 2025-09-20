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
    # charge = "charge"  # move into a monster
    # spend_nerve = "spend_nerve"
    discard_tile = "discard_tile"  # last action of the turn during the final flickers

    # decisions
    pass_key = "pass_key"
    block = "block"  # drop just 2 tiles instead of three, spending 1 nerve
    sustain = "sustain"  # don't drop any tiles during the final flickers
    move_again = "move_again"


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


class DiscardTile(BaseModel):
    move: Literal[MoveType.discard_tile]
    pos: Position


class PassKey(BaseModel):
    move: Literal[MoveType.pass_key]
    player: PlayerColor


class Block(BaseModel):
    move: Literal[MoveType.block]


class Sustain(BaseModel):
    move: Literal[MoveType.sustain]


class MoveAgain(BaseModel):
    move: Literal[MoveType.move_again]


class Move(BaseModel):
    player: PlayerColor
    param: (
        PlaceTile
        | RotateTile
        | Stay
        | Crawl
        | Fall
        | Land
        | DiscardTile
        | PassKey
        | Block
        | Sustain
        | MoveAgain
    ) = Field(discriminator='move')
