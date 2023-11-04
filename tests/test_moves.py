from tng.game.moves import PlaceTile, Move, MoveType
from tng.game.types import PlayerColor


def test_marshalling():
    assert (
        Move(
            player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, x=1, y=4)
        ).model_dump_json()
        == '{"player":"blue","param":{"move":"place_tile","x":1,"y":4}}'
    )


def test_unmarshalling():
    t = Move.model_validate_json('{"player":"blue","param":{"move":"place_tile","x":1,"y":4}}')

    assert t == Move(player=PlayerColor.blue, param=PlaceTile(move=MoveType.place_tile, x=1, y=4))
