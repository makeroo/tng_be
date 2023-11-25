"""
This module implements the TNG game logic.

It:
1. validates a move
2. make that move returning the resulting game state.
"""

from .game import Game, Phase, GameRuntimeError
from .moves import Move, PlaceTile, RotateTile, Stay, Walk, Fall, Drop
from .types import PlayerColor, Tile, Direction, is_crumbling, is_monster, FallDirection, Position


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

    def move_player_stay(self, game: Game, player: PlayerColor, move: Stay) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.falling:
            raise IllegalMove('falling player')

        if not player_status.has_light and player_status.nerves == 0:
            raise IllegalMove('no nerves, forced to walk')

        # apply

        if game.draw_index < len(game.tile_holder):
            drawn_tile = game.tile_holder[game.draw_index]

            game = game.draw_tile()

            if is_monster[drawn_tile]:
                return game.new_phase(Phase.place_monster)

        else:
            # TODO: final flickers
            raise NotImplementedError('final flickers')

        if not player_status.has_light:
            game = game.change_nerves(game.turn, -1)

        elif player_status.nerves < 2:
            game = game.change_nerves(game.turn, +1)

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        player_cell = game.board.at(player_status.pos)

        if player_cell.tile is None:
            raise GameRuntimeError('player\'s cell has no tile')

        if is_crumbling[player_cell.tile]:
            game = (
                game.change_to_pit(player_status.pos)
                .player_falls(game.turn)
                .new_phase(Phase.fall_direction)
            )

            if is_monster[drawn_tile]:
                # TODO: trigger monster attacks
                raise NotImplementedError('trigger monster not implemented')

            return game

        game = game.set_turn(turn=(game.turn + 1) % len(game.players))

        return game

    def fall_direction_fall(self, game: Game, player: PlayerColor, move: Fall) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        # apply

        return (
            game.fall_direction(game.turn, move.direction)
            .set_turn(turn=(game.turn + 1) % len(game.players))
            .new_phase(Phase.move_player)
        )

    def move_player_walk(self, game: Game, player: PlayerColor, move: Walk) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.falling:
            raise IllegalMove('falling player')

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        player_cell = game.board.at(player_status.pos)

        if move.direction not in player_cell.open_directions():
            raise IllegalMove('illegal direction')

        dest_pos = game.board.dest_coords(player_status.pos, move.direction)

        dest_cell = game.board.at(dest_pos)

        if dest_cell.tile is None:
            raise GameRuntimeError('empty tile that shouldn\'t')

        if len(dest_cell.players) > 0 and dest_cell.tile is not Tile.gate:
            raise IllegalMove('dest tile already occupied')

        # apply

        new_game = game.move_player(game.turn, dest_pos)

        if player_cell.tile is None:
            raise GameRuntimeError('player\'s cell has no tile')

        if is_crumbling[player_cell.tile]:
            new_game = new_game.change_to_pit(player_status.pos)

        # TODO: trigger monster attacks

        new_player_status = new_game.players[new_game.turn]

        if new_player_status.falling:
            return new_game.new_phase(Phase.fall_direction)

        if new_player_status.has_light:
            new_game = new_game.relight_near_players(new_player_status)

        else:
            new_game = new_game.relight_me(new_player_status)

        if new_player_status.pos is None:
            raise GameRuntimeError('moved player lost pos')

        cells = game.board.visible_cells_from(new_player_status.pos)

        if any(cell.tile is None for cell in cells):
            return new_game.new_phase(Phase.discover_tiles)

        return new_game.set_turn((game.turn + 1) % len(game.players))

    def move_player_drop(self, game: Game, player: PlayerColor, move: Drop) -> 'Game':
        # validate

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if move.place < 0 or move.place >= game.board.edge_length:
            raise IllegalMove('out of bounds')

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        if player_status.fall_direction is FallDirection.column:
            pos = Position(player_status.pos.x, move.place)

        elif player_status.fall_direction is FallDirection.row:
            pos = Position(move.place, player_status.pos.y)

        else:
            raise GameRuntimeError(f'unknown player fall direction {player_status.fall_direction}')

        cell = game.board.at(pos)

        if cell.tile is not None and (
            (
                player_status.fall_direction is FallDirection.column
                and any(
                    game.board.at(Position(ccrow, player_status.pos.y)).tile is None
                    for ccrow in range(game.board.edge_length)
                )
                or any(
                    game.board.at(Position(player_status.pos.x, cccol)).tile is None
                    for cccol in range(game.board.edge_length)
                )
            )
        ):
            raise IllegalMove('tile not empty')

        if game.draw_index >= len(game.tile_holder):
            raise IllegalMove('game ended in loss')

        # apply

        if cell.tile is None:
            drawn_tile = game.tile_holder[game.draw_index]

            new_game = game.draw_tile().place_tile(pos, drawn_tile).move_player(game.turn, pos)

            if drawn_tile in (Tile.straight_passage, Tile.t_passage):
                return game.new_phase(Phase.drop_on_tile)

            if is_monster[drawn_tile]:
                # TODO monster attacks -> select an empty tile or draw a tile
                raise NotImplementedError('monster attacks')

            cells = new_game.board.visible_cells_from(pos)

            if any(cell.tile is None for cell in cells):
                return new_game.new_phase(Phase.discover_tiles)

            return new_game.new_phase(Phase.move_player).set_turn(
                (game.turn + 1) % len(game.players)
            )

        new_game = game.move_player(game.turn, pos)

        return new_game

    def discover_tiles_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        # validate

        player_status = game.players[game.turn]

        # checked in the _apply_place_tile
        # if player_status.color != player:
        #     raise IllegalMove('not player turn')

        if game.draw_index >= len(game.tile_holder):
            raise IllegalMove('final flickres')

        # apply

        placed_tile = game.tile_holder[game.draw_index]

        new_game = self._apply_place_tile(game, player, move, placed_tile).draw_tile()

        if placed_tile in (Tile.t_passage, Tile.straight_passage):
            return new_game.new_phase(Phase.rotate_discovered_tile)

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        cells = new_game.board.visible_cells_from(player_status.pos)

        if any(cell.tile is None for cell in cells):
            return new_game.new_phase(Phase.discover_tiles)

        return new_game.new_phase(Phase.move_player).set_turn((game.turn + 1) % len(game.players))

    def rotate_discovered_tile_rotate_tile(
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
            return new_game.new_phase(Phase.discover_tiles)

        return new_game.new_phase(Phase.move_player).set_turn(
            (new_game.turn + 1) % len(new_game.players)
        )

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
