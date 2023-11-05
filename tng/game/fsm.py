from .game import Game, Phase
from .moves import Move, PlaceTile
from .types import PlayerColor, Tile, Direction


class TNGFSM:
    def apply(self, game: Game, move: Move) -> Game:
        handler = getattr(f'{game.phase}_{move.param.move}')

        return handler(game, move.player, move.param)

