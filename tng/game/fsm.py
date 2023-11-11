from .game import Game, Phase
from .moves import Move, PlaceTile, RotateTile
from .types import PlayerColor, Tile, Direction


class TNGFSM:
    def apply(self, game: Game, move: Move) -> Game:
        handler = getattr(self, f'{game.phase.value}_{move.param.move}')

        return handler(game, move.player, move.param)

    def place_start_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        return self._apply_place_tile(game, player, move, Tile.start).new_phase(Phase.rotate_start)

    def rotate_start_rotate_tile(self, game: Game, player: PlayerColor, move: RotateTile) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise ValueError('not player turn')

        # apply

        cells = game.board.visible_cells_from(player_status.x, player_status.y)

        if any(cell.tile is None for cell in cells):
            return game.new_phase(Phase.discover_start_tiles)

        elif game.turn + 1 == len(game.players):
            return game.new_phase(Phase.move_player).set_turn(0)

        else:
            return game.new_phase(Phase.place_start).set_turn(game.turn + 1)

    def discover_start_tiles_place_tile(
        self, game: Game, player: PlayerColor, move: PlaceTile
    ) -> Game:
        # this is the start macro phase, there is no need
        # to check for bounds: there are surely tiles to draw
        placed_tile = game.tile_holder[game.draw_index]

        return (
            self._apply_place_tile(game, player, move, placed_tile)
            .new_phase(Phase.rotate_discovered_start_tile)
            .draw_tile()
        )

    def _apply_place_tile(
        self, game: Game, player: PlayerColor, move: PlaceTile, tile: Tile
    ) -> Game:
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

        return game.place_tile(move.x, move.y, tile, Direction.n).move_player(
            game.turn, move.x, move.y
        )
