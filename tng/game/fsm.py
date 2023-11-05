from .game import Game, Phase
from .moves import Move, PlaceTile
from .types import PlayerColor, Tile, Direction


class TNGFSM:
    def apply(self, game: Game, move: Move) -> Game:
        handler = getattr(self, f'{game.phase.value}_{move.param.move}')

        return handler(game, move.player, move.param)

    def place_start_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        # validate move

        x = move.x
        y = move.y
        edge_length = game.board.edge_length

        if x < 0 or x >= edge_length:
            raise ValueError('x out of board')

        if y < 0 or y >= edge_length:
            raise ValueError('y out of board')

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise ValueError('not player turn')

        cell = game.board.at(move.x, move.y)

        if cell.tile is not None:
            raise ValueError('tile not empty')

        # apply

        return (
            game.new_phase(Phase.rotate_start)
            .place_tile(move.x, move.y, Tile.start, Direction.n)
            .move_player(game.turn, move.x, move.y)
        )
