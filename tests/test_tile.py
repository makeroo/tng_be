from tng.game.types import Tile, Direction


def test_open_directions():
    assert Tile.start.open_directions == [Direction.s, Direction.w]
