from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .types import PlayerColor, Direction


class MoveType(str, Enum):
    place_tile = "place_tile"
    rotate_tile = "rotate_tile"
    stay = "stay"
    walk = "walk"


class PlaceTile(BaseModel):
    move: Literal[MoveType.place_tile]
    x: int
    y: int


class RotateTile(BaseModel):
    move: Literal[MoveType.rotate_tile]
    direction: Direction


class Stay(BaseModel):
    move: Literal[MoveType.stay]


class Walk(BaseModel):
    move: Literal[MoveType.stay]
    direction: Direction


class Move(BaseModel):
    player: PlayerColor
    param: PlaceTile | RotateTile = Field(discriminator='move')
