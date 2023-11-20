from tng.game.types import Direction, Position


def test_rotate():
    assert Direction.n.rotate(Direction.n) is Direction.n

    assert Direction.w.rotate(Direction.s) is Direction.e


def test_neighbor():
    assert Direction.n.neighbor(Position(0, 0), 6) == Position(0, 5)

    assert Direction.e.neighbor(Position(3, 4), 6) == Position(4, 4)
