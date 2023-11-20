from tng.game.moves import PlaceTile, Move, MoveType
from tng.game.types import PlayerColor, Position


def test_marshalling():
    assert (
        Move(
            player=PlayerColor.blue,
            param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=4)),
        ).model_dump_json()
        == '{"player":"blue","param":{"move":"place_tile","pos":[1,4]}}'
    )


def test_unmarshalling():
    t = Move.model_validate_json('{"player":"blue","param":{"move":"place_tile","pos":[1,4]}}')

    assert t == Move(
        player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, pos=Position(x=1, y=4))
    )
