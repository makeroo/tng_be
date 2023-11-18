from tng.game.factory import GameFactory
from tng.game.fsm import TNGFSM
from tng.game.types import PlayerColor, Direction, Tile
from tng.game.moves import Move, PlaceTile, MoveType, RotateTile
from tng.game.game import Phase


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


def test_rotate_start_rotate_tile():
    factory = GameFactory()

    game = factory.new_game(
        PlayerColor.blue, PlayerColor.red, PlayerColor.green, PlayerColor.purple
    )

    fsm = TNGFSM()

    game2 = fsm.apply(
        game, Move(player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, x=3, y=4))
    )

    game3 = fsm.apply(
        game2,
        Move(
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
    )

    assert game3.board.at(3, 4).players == [PlayerColor.blue]
    assert game3.board.at(3, 4).direction == Direction.e
    assert game3.players[0].x == 3
    assert game3.players[0].y == 4
    assert game3.phase == Phase.discover_start_tiles


def test_rotate_discovered_start_tile_rotate_tile():
    factory = GameFactory()

    game = factory.new_game(
        PlayerColor.blue, PlayerColor.red, PlayerColor.green, PlayerColor.purple
    )

    fsm = TNGFSM()

    game2 = fsm.apply(
        game, Move(player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, x=3, y=4))
    )

    game3 = fsm.apply(
        game2,
        Move(
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.e),
        ),
    )

    # patch tile holder to simplify asserts after place_tile move
    game3.tile_holder[0] = Tile.straight_passage

    game4 = fsm.apply(
        game3,
        Move(
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, x=3, y=3),
        ),
    )

    assert game4.board.at(3, 4).players == [PlayerColor.blue]
    assert game4.players[0].x == 3
    assert game4.players[0].y == 4
    assert game4.last_placed_tile_x == 3
    assert game4.last_placed_tile_y == 3
    assert game4.draw_index == 1
    assert game4.phase == Phase.rotate_discovered_start_tile
    assert game4.board.at(3, 3).tile is Tile.straight_passage

    game5 = fsm.apply(
        game4,
        Move(
            player=PlayerColor.blue,
            param=RotateTile(move=MoveType.rotate_tile, direction=Direction.s),
        ),
    )

    assert game5.phase == Phase.discover_start_tiles
    assert game5.board.at(3, 3).direction == Direction.s
    assert game5.board.at(3, 4).players == [PlayerColor.blue]
    assert game5.players[0].x == 3
    assert game5.players[0].y == 4
