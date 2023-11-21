"""
This module implements the TNG game logic.

It:
1. validates a move
2. make that move returning the resulting game state.
"""

from .game import Game, Phase, GameRuntimeError
from .moves import Move, PlaceTile, RotateTile
from .types import PlayerColor, Tile, Direction, connected_to, is_crumbling, is_monster


class IllegalMove(ValueError):
    pass


class TNGFSM:
    def apply(self, game: Game, move: Move) -> Game:
        handler = getattr(self, f'{game.phase.value}_{move.param.move}')

        return handler(game, move.player, move.param)

    def place_start_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        return (
            self._apply_place_tile(game, player, move, Tile.start)
            .new_phase(Phase.rotate_start)
            .move_player(game.turn, move.pos)
        )

    def rotate_start_rotate_tile(self, game: Game, player: PlayerColor, move: RotateTile) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        # apply

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        game = game.place_tile(player_status.pos, Tile.start, move.direction)

        cells = game.board.visible_cells_from(player_status.pos)

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

    def rotate_discovered_start_tile_rotate_tile(
        self, game: Game, player: PlayerColor, move: RotateTile
    ) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        last_placed_cell = game.board.at(game.last_placed_tile_pos)

        if last_placed_cell.tile is None:
            raise GameRuntimeError('empty cell')

        new_game = game.place_tile(game.last_placed_tile_pos, last_placed_cell.tile, move.direction)

        if player_status.pos not in new_game.board.visible_cells_coords_from(
            new_game.last_placed_tile_pos
        ):
            raise IllegalMove('not_connected')

        # apply

        cells = new_game.board.visible_cells_from(player_status.pos)

        if any(cell.tile is None for cell in cells):
            return new_game.new_phase(Phase.discover_start_tiles)

        elif new_game.turn + 1 == len(new_game.players):
            return new_game.new_phase(Phase.move_player).set_turn(0)

        else:
            return new_game.new_phase(Phase.place_start).set_turn(game.turn + 1)


        else:
            return game.new_phase(Phase.place_start).set_turn(game.turn + 1)

    def _apply_place_tile(
        self, game: Game, player: PlayerColor, move: PlaceTile, tile: Tile
    ) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.pos is None:
            # assuming placing start

            x = move.pos.x
            y = move.pos.y
            edge_length = game.board.edge_length

            if x < 0 or x >= edge_length:
                raise IllegalMove('x out of board')

            if y < 0 or y >= edge_length:
                raise IllegalMove('y out of board')

        elif move.pos not in game.board.visible_cells_coords_from(player_status.pos):
            raise IllegalMove('not connected')

        cell = game.board.at(move.pos)

        if cell.tile is not None:
            raise IllegalMove('tile not empty')

        # apply

        return game.place_tile(move.pos, tile, Direction.n)
