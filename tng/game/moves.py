from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .types import PlayerColor, Direction, Position, FallDirection


class MoveType(str, Enum):
    place_tile = "place_tile"
    rotate_tile = "rotate_tile"
    stay = "stay"
    walk = "walk"
    fall = "fall"  # ie. select either row or column
    drop = "drop"  # ie. return on board
    # TODO pass key


class PlaceTile(BaseModel):
    move: Literal[MoveType.place_tile]
    pos: Position


class RotateTile(BaseModel):
    move: Literal[MoveType.rotate_tile]
    direction: Direction


class Stay(BaseModel):
    move: Literal[MoveType.stay]


class Walk(BaseModel):
    move: Literal[MoveType.walk]
    direction: Direction


class Fall(BaseModel):
    move: Literal[MoveType.fall]
    direction: FallDirection


class Drop(BaseModel):
    move: Literal[MoveType.drop]
    place: int


class Move(BaseModel):
    player: PlayerColor
    param: PlaceTile | RotateTile | Stay | Walk | Fall | Drop = Field(discriminator='move')
