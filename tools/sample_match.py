from random import Random

from pydantic import BaseModel

from tng.game.factory import GameFactory
from tng.game.fsm import TNGFSM
from tng.game.types import PlayerColor, Direction, Position, FallDirection
from tng.game.moves import Move, PlaceTile, MoveType, RotateTile, Walk, Stay, Fall, Drop
from tng.game.game import Game

from print_game import print_game, print_move


class GameData(BaseModel):
    move_idx: int
    move: Move | None
    resulting_game: Game

    def __str__(self) -> str:
        return f'move: {self.move_idx} {print_move(self.move) if self.move else "-"}\n\n{print_game(self.resulting_game)}\n\n'


def run_sample_match():
    factory = GameFactory(Random(1))

    game = factory.new_game(
        PlayerColor.blue, PlayerColor.red, PlayerColor.green, PlayerColor.purple
    )

    moves = [
        # start macro phase
        Move(  # 0
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=4)),
        ),
        Move(  # 1
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 2
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=3)),
        ),
        Move(  # 3
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.w),
        ),
        Move(  # 4
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=2, y=4)),
        ),
        Move(  # 5
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 6
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=2)),
        ),
        Move(  # 7
            player=PlayerColor.red,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 8
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=2, y=2)),
        ),
        Move(  # 9
            player=PlayerColor.red,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.s),
        ),
        Move(  # 10
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=2, y=1)),
        ),
        Move(  # 11
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.w),
        ),
        Move(  # 12
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=1)),
        ),
        Move(  # 13
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 14
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=5, y=1)),
        ),
        Move(  # 15
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 16
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=5, y=2)),
        ),
        Move(  # 17
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 18
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=4, y=1)),
        ),
        Move(  # 19
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.s),
        ),
        # in game macro phase, move turn 1
        Move(  # 20
            player=PlayerColor.blue,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 21
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=4)),
        ),
        Move(  # 22
            player=PlayerColor.red,
            param=Stay(move=MoveType.stay),
        ),
        Move(  # 23
            player=PlayerColor.red,
            param=Fall(move=MoveType.fall, direction=FallDirection.column),
        ),
        Move(  # 24
            player=PlayerColor.green,
            param=Walk(move=MoveType.walk, direction=Direction.e),
        ),
        Move(  # 25
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=0)),
        ),
        Move(  # 26
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 27
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=2)),
        ),
        Move(  # 28
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 29
            player=PlayerColor.purple,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 30
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=4, y=0)),
        ),
        Move(  # 31
            player=PlayerColor.blue,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 32
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=5)),
        ),
        Move(  # 33
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=0, y=4)),
        ),
        Move(  # 34
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 35
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=3)),
        ),
        Move(  # 36
            player=PlayerColor.red,
            param=Drop(move=MoveType.drop, place=4),
        ),
        Move(  # 37
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=5)),
        ),
        Move(  # 38
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 3)),
        ),
        Move(  # 39
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(4, 4)),
        ),
        Move(  # 40
            player=PlayerColor.red,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 41
            player=PlayerColor.green,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 42
            player=PlayerColor.green,
            param=Fall(move=MoveType.fall, direction=FallDirection.column),
        ),
        Move(  # 43
            player=PlayerColor.purple,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 44
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 0)),
        ),
        Move(  # 45
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 46
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 2)),
        ),
        Move(  # 47
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(2, 1)),
        ),
        Move(  # 48
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 49
            player=PlayerColor.blue,
            param=Walk(move=MoveType.walk, direction=Direction.s),
        ),
        Move(  # 50
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(2, 5)),
        ),
        Move(  # 51
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 52
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(0, 5)),
        ),
        Move(  # 53
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.s),
        ),
        Move(  # 54
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(1, 0)),
        ),
        Move(  # 54
            player=PlayerColor.red,
            param=Walk(move=MoveType.walk, direction=Direction.e),
        ),
    ]

    # print(GameData(move_idx=0, move=None, resulting_game=game))

    fsm = TNGFSM()

    for idx, move in enumerate(moves):
        game = fsm.apply(
            game,
            move,
        )

        print(GameData(move_idx=idx, move=move, resulting_game=game))


if __name__ == '__main__':
    run_sample_match()
