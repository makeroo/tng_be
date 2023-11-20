from tng.game.types import Tile, Direction, open_directions


def test_open_directions():
    assert open_directions[Tile.start] == [Direction.s, Direction.w]
