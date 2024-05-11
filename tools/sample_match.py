from random import Random

from pydantic import BaseModel

from tng.game.factory import GameFactory
from tng.game.fsm import TNGFSM
from tng.game.types import PlayerColor, Direction, Position, FallDirection, Tile
from tng.game.moves import Move, PlaceTile, MoveType, RotateTile, Crawl, Stay, Fall, Land
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

    assert game.tile_holder == [
        Tile.t_passage,  # 0 rem 76
        Tile.straight_passage,  # 1 rem 75
        Tile.t_passage,  # 2 rem 74
        Tile.four_way_passage,  # 3 rem 73
        Tile.straight_passage,  # 4 rem 72
        Tile.t_passage,  # 5 rem 71
        Tile.four_way_passage,  # 6 rem 70
        Tile.t_passage,  # 7 rem 69
        Tile.t_passage,  # 8 rem 68
        Tile.t_passage,  # 9 rem 67
        Tile.wax_eater,  # 10 rem 66
        Tile.gate,  # 11 rem 65
        Tile.t_passage,  # 12 rem 64
        Tile.four_way_passage,  # 13 rem 63
        Tile.key,  # 14 rem 62
        Tile.key,  # 15 rem 61
        Tile.wax_eater,  # 16 rem 60
        Tile.straight_passage,  # 17 rem 59
        Tile.t_passage,  # 18 rem 58
        Tile.wax_eater,  # 19 rem 57
        Tile.t_passage,  # 20 rem 56
        Tile.t_passage,  # 21 rem 55
        Tile.t_passage,  # 22 rem 54
        Tile.wax_eater,  # 23 rem 53
        Tile.gate,  # 24 rem 52
        Tile.straight_passage,  # 25 rem 51
        Tile.key,  # 26 rem 50
        Tile.key,  # 27 rem 49
        Tile.four_way_passage,  # 28 rem 48
        Tile.four_way_passage,  # 29 rem 47
        Tile.straight_passage,  # 30 rem 46
        Tile.t_passage,  # 31 rem 45
        Tile.wax_eater,  # 32 rem 44
        Tile.t_passage,  # 33 rem 43
        Tile.t_passage,  # 34 rem 42
        Tile.t_passage,  # 35 rem 41
        Tile.gate,  # 36 rem 40
        Tile.wax_eater,  # 37 rem 39
        Tile.wax_eater,  # 38 rem 38
        Tile.t_passage,  # 39 rem 37
        Tile.t_passage,  # 40 rem 36
        Tile.four_way_passage,  # 41 rem 35
        Tile.four_way_passage,  # 42 rem 34
        Tile.t_passage,  # 43 rem 33
        Tile.t_passage,  # 44 rem 32
        Tile.four_way_passage,  # 45 rem 31
        Tile.wax_eater,  # 46 rem 30
        Tile.four_way_passage,  # 47 rem 29
        Tile.four_way_passage,  # 48 rem 28
        Tile.t_passage,  # 49 rem 27
        Tile.t_passage,  # 50 rem 26
        Tile.straight_passage,  # 51 rem 25
        Tile.t_passage,  # 52 rem 24
        Tile.straight_passage,  # 53 rem 23
        Tile.gate,  # 54 rem 22
        Tile.wax_eater,  # 55 rem 21
        Tile.t_passage,  # 56 rem 20
        Tile.wax_eater,  # 57 rem 19
        Tile.t_passage,  # 58 rem 18
        Tile.wax_eater,  # 59 rem 17
        Tile.t_passage,  # 60 rem 16
        Tile.t_passage,  # 61 rem 15
        Tile.key,  # 62 rem 14
        Tile.t_passage,  # 63 rem 13
        Tile.straight_passage,  # 64 rem 12
        Tile.t_passage,  # 65 rem 11
        Tile.t_passage,  # 66 rem 10
        Tile.t_passage,  # 67 rem 9
        Tile.four_way_passage,  # 68 rem 8
        Tile.four_way_passage,  # 69 rem 7
        Tile.key,  # 70 rem 6
        Tile.straight_passage,  # 71 rem 5
        Tile.wax_eater,  # 72 rem 4
        Tile.t_passage,  # 73 rem 3
        Tile.t_passage,  # 74 rem 2
        Tile.straight_passage,  # 75 rem 1
        # lights out!
    ]

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
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=5, y=1)),
        ),
        Move(  # 14
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 15
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=5, y=2)),
        ),
        Move(  # 16
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 17
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=4, y=1)),
        ),
        Move(  # 18
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.s),
        ),
        # in game macro phase, move turn 1
        Move(  # 19
            player=PlayerColor.blue,
            param=Crawl(move=MoveType.crawl, direction=Direction.w),
        ),
        Move(  # 20
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=4)),
        ),
        Move(  # 21
            player=PlayerColor.red,
            param=Stay(move=MoveType.stay),
        ),
        Move(  # 22
            player=PlayerColor.red,
            param=Fall(move=MoveType.fall, direction=FallDirection.column),
        ),
        Move(  # 23
            player=PlayerColor.green,
            param=Crawl(move=MoveType.crawl, direction=Direction.e),
        ),
        Move(  # 24
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=0)),
        ),
        Move(  # 25
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 26
            player=PlayerColor.green,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=2)),
        ),
        Move(  # 27
            player=PlayerColor.green,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 28
            player=PlayerColor.purple,
            param=Crawl(move=MoveType.crawl, direction=Direction.w),
        ),
        Move(  # 29
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=4, y=0)),
        ),
        Move(  # 30
            player=PlayerColor.blue,
            param=Crawl(move=MoveType.crawl, direction=Direction.w),
        ),
        Move(  # 31
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=5)),
        ),
        Move(  # 32
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=0, y=4)),
        ),
        Move(  # 33
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 34
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=3)),
        ),
        Move(  # 35
            player=PlayerColor.red,
            param=Land(move=MoveType.land, place=4),
        ),
        Move(  # 36
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=3, y=5)),
        ),
        Move(  # 37
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 3)),
        ),
        Move(  # 38
            player=PlayerColor.red,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(4, 4)),
        ),
        Move(  # 39
            player=PlayerColor.red,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 40
            player=PlayerColor.green,
            param=Crawl(move=MoveType.crawl, direction=Direction.w),
        ),
        Move(  # 41
            player=PlayerColor.green,
            param=Fall(move=MoveType.fall, direction=FallDirection.column),
        ),
        Move(  # 42
            player=PlayerColor.purple,
            param=Crawl(move=MoveType.crawl, direction=Direction.w),
        ),
        Move(  # 43
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 0)),
        ),
        Move(  # 44
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.n),
        ),
        Move(  # 45
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(3, 2)),
        ),
        Move(  # 46
            player=PlayerColor.purple,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 47
            player=PlayerColor.purple,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(2, 1)),
        ),
        Move(  # 48
            player=PlayerColor.blue,
            param=Crawl(move=MoveType.crawl, direction=Direction.s),
        ),
        Move(  # 49
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(2, 5)),
        ),
        Move(  # 50
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(0, 5)),
        ),
        Move(  # 51
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
        Move(  # 52
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(1, 0)),
        ),
        Move(  # 53
            player=PlayerColor.red,
            param=Crawl(move=MoveType.crawl, direction=Direction.e),
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
