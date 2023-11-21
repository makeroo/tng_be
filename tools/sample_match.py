from random import Random

from pydantic import BaseModel

from tng.game.factory import GameFactory
from tng.game.fsm import TNGFSM
from tng.game.types import PlayerColor, Direction, Position
from tng.game.moves import Move, PlaceTile, MoveType, RotateTile, Walk
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
        # in game macro phase
        Move(  # 20
            player=PlayerColor.blue,
            param=Walk(move=MoveType.walk, direction=Direction.w),
        ),
        Move(  # 21
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=4)),
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
