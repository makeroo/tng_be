from tng.game.factory import GameFactory
from tng.game.fsm import TNGFSM
from tng.game.types import PlayerColor
from tng.game.moves import Move, PlaceTile, MoveType


def test_place_start_place_tile():
    factory = GameFactory()

    game = factory.new_game(
        PlayerColor.blue, PlayerColor.red, PlayerColor.green, PlayerColor.purple
    )

    fsm = TNGFSM()

    game2 = fsm.apply(
        game, Move(player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, x=3, y=4))
    )

    assert game2.board.at(3, 4).players == [PlayerColor.blue]
    assert game2.players[0].x == 3
    assert game2.players[0].y == 4

    assert game.board.at(3, 4).players == []
    assert game.players[0].x is None
    assert game.players[0].y is None
