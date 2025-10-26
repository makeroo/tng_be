from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .types import PlayerColor, Direction, Position, FallDirection


class MoveType(str, Enum):
    place_tile = "place_tile"
    rotate_tile = "rotate_tile"
    stay = "stay"
    crawl = "crawl"
    optional_movement = "optional_movement"  # to move again if desidered (and nerves available)
    fall = "fall"  # select either row or column
    land = "land"  # return on board
    # charge = "charge"  # move into a monster
    discard_tile = "discard_tile"  # last action of the turn during the final flickers

    # decisions
    pass_key = "pass_key"
    block = "block"  # drop just 2 tiles instead of three, spending 1 nerve
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


class OptionalMovement(BaseModel):
    move: Literal[MoveType.optional_movement]
    move_again: bool


class Fall(BaseModel):
    move: Literal[MoveType.fall]
    direction: FallDirection


class Land(BaseModel):
    move: Literal[MoveType.land]
    place: int


class DiscardTile(BaseModel):
    move: Literal[MoveType.discard_tile]
    pos: Position | None  # use None to sustain


class PassKey(BaseModel):
    move: Literal[MoveType.pass_key]
    player: PlayerColor


class Block(BaseModel):
    move: Literal[MoveType.block]
    block: bool


class MoveAgain(BaseModel):
    move: Literal[MoveType.move_again]


class Move(BaseModel):
    player: PlayerColor
    param: (
        PlaceTile
        | RotateTile
        | Stay
        | Crawl
        | OptionalMovement
        | Fall
        | Land
        | DiscardTile
        | PassKey
        | Block
        | MoveAgain
    ) = Field(discriminator='move')
