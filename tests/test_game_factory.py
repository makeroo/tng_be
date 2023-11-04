from tng.game.factory import GameFactory
from tng.game.types import PlayerColor


def test_new_game():
    factory = GameFactory()

    game = factory.new_game(
        PlayerColor.red,
        PlayerColor.blue,
        PlayerColor.green,
        PlayerColor.purple,
    )

    assert game.board.edge_length == 6
    assert len(game.board.cells) == 36
    assert len(game.players) == 4
    assert all(c.tile is None for c in game.board.cells)
    assert all(len(c.players) == 0 for c in game.board.cells)

    assert [p.color for p in game.players] == [
        PlayerColor.red,
        PlayerColor.blue,
        PlayerColor.green,
        PlayerColor.purple,
    ]
    assert all(not p.has_key for p in game.players)
    assert all(p.has_light for p in game.players)
    assert all(p.nerves == 1 for p in game.players)

    assert len(game.tile_holder) == 76
