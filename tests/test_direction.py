from tng.game.types import Direction


def test_rotate():
    assert Direction.n.rotate(Direction.n) is Direction.n

    assert Direction.w.rotate(Direction.s) is Direction.e


def test_neighbor():
    assert Direction.n.neighbor(0, 0, 6) == (0, 5)

    assert Direction.e.neighbor(3, 4, 6) == (4, 4)
