"""
This module contains all TNG game data manipulation.

Every method parameter is assumed to be correct, ie. already "validated"
by the caller (eg. FSM).

Assuming also that each state is "consistent" ie. produced by FSM
while processing a valid sequence of moves, then every exception risen
denote a bug.

The game state classes are meant to be immutable. Even if
we use lists or other mutable structures, we never change them,
instead we recursively shallow clone them.

The resulting state is coherent from that class POV.
Example:
* Board.move_player removes the player from the starting cell
  and adds to the destination cell.
  But Board doesn't know about player state so if the dest cell
  is a pit, it's a Game concern to change they state to falling.

Note: an exception to this principle are the turn/phase flags.
They are managed by FSM which uses several Game calls.
"""

from typing import NamedTuple, Iterable, Iterator
from enum import Enum

from .types import Tile, Direction, PlayerColor, Position, open_directions, FallDirection


class GameRuntimeError(Exception):
    pass


class Cell(NamedTuple):
    tile: Tile | None
    direction: Direction
    players: list[PlayerColor]

    def remove_player(self, player_color: PlayerColor) -> 'Cell':
        new_players = [player for player in self.players if player != player_color]

        return self._replace(players=new_players)

    def add_player(self, player_color: PlayerColor) -> 'Cell':
        new_players = list(self.players)

        new_players.append(player_color)

        return self._replace(players=new_players)

    def open_directions(self) -> list[Direction]:
        if self.tile is None:
            raise GameRuntimeError('no tile')

        return [d.rotate(self.direction) for d in open_directions[self.tile]]


class Board(NamedTuple):
    cells: list[Cell]
    edge_length: int  # can be 6 (up to 4 players) or 7 (5 players)

    def at(self, pos: Position) -> Cell:
        return self.cells[pos.idx(self.edge_length)]

    def place_tile(self, pos: Position, tile: Tile, direction: Direction = Direction.n) -> 'Board':
        new_cells = list(self.cells)

        idx = pos.idx(self.edge_length)

        orig_cell = new_cells[idx]

        new_cell = orig_cell._replace(
            tile=tile,
            direction=direction,
        )

        new_cells[idx] = new_cell

        return self._replace(cells=new_cells)

    def move_player(
        self,
        player_color: PlayerColor,
        from_pos: Position | None,
        to_pos: Position | None,
    ) -> 'Board':
        new_cells = list(self.cells)

        if from_pos is not None:
            old_idx = from_pos.idx(self.edge_length)
            old_cell = self.cells[old_idx]

            new_cells[old_idx] = old_cell.remove_player(player_color)

        if to_pos is not None:
            new_idx = to_pos.idx(self.edge_length)
            new_cell = self.cells[new_idx]

            new_cells[new_idx] = new_cell.add_player(player_color)

        return self._replace(cells=new_cells)

    def visible_cells_from(self, pos: Position) -> list[Cell]:
        return [self.at(pos) for pos in self.visible_cells_coords_from(pos)]

    def visible_cells_coords_from(self, pos: Position) -> list[Position]:
        cell = self.at(pos)
        directions = cell.open_directions()
        r = []

        for direction in directions:
            dx, dy = direction.neighbor(pos, self.edge_length)

            r.append(Position(dx, dy))

        return r

    def is_connected(self, from_pos: Position, d: Direction) -> bool:
        cell = self.at(from_pos)

        if cell.tile is None:
            return False

        for od in cell.open_directions():
            if od is d:
                return True

        return False

    def drop_tiles(self, dropped_tiles: Iterable[tuple[int, int]]) -> 'Board':
        new_cells = list(self.cells)

        for x, y in dropped_tiles:
            pos = y * self.edge_length + x

            cell = new_cells[pos]
            new_cells[pos] = cell._replace(tile=None)

        return self._replace(cells=new_cells)

    def dest_coords(self, pos: Position, direction: Direction) -> Position:
        return direction.neighbor(pos, self.edge_length)


class Player(NamedTuple):
    color: PlayerColor

    has_key: bool
    nerves: int
    has_light: bool
    falling: bool

    # player state:
    # falling False, pos None: start, fall_direction: None, the player has to place the start tile yet
    # falling False, pos not None, fall_direction: None, player on board
    # falling True, pos not None, fall_direction: None, player falling, they have to decide if row or column
    # falling True, pos not None, fall_direction: not None, player falling, they decided if row or column
    pos: Position | None

    fall_direction: FallDirection | None


class Phase(Enum):
    place_start = 'place_start'
    rotate_start = 'rotate_start'
    discover_start_tiles = 'discover_start_tiles'
    rotate_discovered_start_tile = 'rotate_discovered_start_tile'
    move_player = 'move_player'
    place_monster = 'place_monster'
    discover_tiles = 'discover_tiles'
    rotate_discovered_tile = 'rotate_discovered_tile'
    fall_direction = 'fall_direction'
    drop_on_tile = 'drop_on_tile'


class Game(NamedTuple):
    board: Board
    tile_holder: list[Tile]
    draw_index: int  # index in the tile_holder deck

    players: list[Player]

    turn: int  # index in the players array

    phase: Phase

    last_placed_tile_pos: Position

    def new_phase(self, phase: Phase) -> 'Game':
        """
        FSM check is up to TNGFSM, here we take the phase as it is.
        """

        return self._replace(phase=phase)

    def set_turn(self, turn: int) -> 'Game':
        return self._replace(turn=turn)

    def draw_tile(self):
        return self._replace(draw_index=self.draw_index + 1)

    def place_tile(self, pos: Position, tile: Tile, direction: Direction = Direction.n) -> 'Game':
        return self._replace(
            board=self.board.place_tile(pos, tile, direction),
            last_placed_tile_pos=pos,
        )

    def move_player(self, player_idx: int, pos: Position) -> 'Game':
        player_status = self.players[player_idx]

        new_player_status = player_status._replace(pos=pos, falling=False, fall_direction=None)

        dest_cell = self.board.at(pos)

        if dest_cell.tile is Tile.key and not new_player_status.has_key:
            new_player_status = new_player_status._replace(has_key=True)

        if dest_cell.tile is Tile.pit:
            new_player_status = new_player_status._replace(falling=True)
            board_pos = None

        else:
            board_pos = new_player_status.pos

        new_players = list(self.players)

        new_players[player_idx] = new_player_status

        new_game = self._replace(
            players=new_players,
            board=self.board.move_player(player_status.color, player_status.pos, board_pos),
        )

        if player_status.pos is None:
            return new_game

        return new_game._drop_tiles(player_status.pos, player_status.has_light)

    def change_nerves(self, player_idx: int, delta: int) -> 'Game':
        player_status = self.players[player_idx]

        player_status = player_status._replace(nerves=player_status.nerves + delta)

        new_players = list(self.players)
        new_players[player_idx] = player_status

        return self._replace(players=new_players)

    def change_to_pit(self, pos: Position) -> 'Game':
        return self._replace(board=self.board.place_tile(pos, Tile.pit))

    def player_falls(self, player_idx: int) -> 'Game':
        player_status = self.players[player_idx]

        new_player_status = player_status._replace(falling=True)

        new_players = list(self.players)
        new_players[player_idx] = new_player_status

        new_board = self.board.move_player(player_status.color, player_status.pos, None)

        new_game = self._replace(
            board=new_board,
            players=new_players,
        )

        if player_status.pos is None:
            raise GameRuntimeError('player not placed')

        return new_game._drop_tiles(player_status.pos, player_status.has_light)

    def relight_near_players(self, player_status: Player) -> 'Game':
        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        player_updates: dict[PlayerColor, Player] = {}

        for p in filter(lambda p: not p.has_light, self.near_players(player_status.pos)):
            player_updates[p.color] = p._replace(has_light=True)

        if not player_updates:
            return self

        new_players = [player_updates.get(p.color, p) for p in self.players]

        return self._replace(players=new_players)

    def relight_me(self, player_status: Player) -> 'Game':
        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        if all(not p.has_light for p in self.near_players(player_status.pos)):
            return self

        new_player_status = player_status._replace(has_light=True)

        new_players = [
            p if p.color != new_player_status.color else new_player_status for p in self.players
        ]

        return self._replace(players=new_players)

    def near_players(self, pos: Position) -> Iterator[Player]:
        for cell in self.board.visible_cells_from(pos):
            yield from map(self.player_status, cell.players)

    def _drop_tiles(self, pos: Position, has_light: bool) -> 'Game':
        enlighten_cells = [pos]

        if has_light:
            enlighten_cells.extend(self.board.visible_cells_coords_from(pos))

        # not on the first and term in the lambda: a connected tile may be empty
        # when falling because the crumbled tile may have few open directions
        # then a pit (that has all the four of them)

        dropped_tiles = filter(
            lambda cell_coords: self.board.at(cell_coords).tile is not None
            and not self.is_enlightened(cell_coords),
            enlighten_cells,
        )

        new_board = self.board.drop_tiles(dropped_tiles)

        return self._replace(board=new_board)

    def is_enlightened(self, pos: Position) -> bool:
        """
        A tile is enlightened if either a player is in it or
        there is a player (with a lit candle) in a directly
        connected tile.
        """
        cell = self.board.at(pos)

        if cell.players:
            return True

        return any(
            self.player_status(p).has_light
            for c in self.board.visible_cells_from(pos)
            for p in c.players
        )

    def player_status(self, player: PlayerColor) -> Player:
        for p in self.players:
            if p.color == player:
                return p

        raise GameRuntimeError('player not found')

    def fall_direction(self, player_idx: int, direction: FallDirection) -> 'Game':
        player_status = self.players[player_idx]

        new_player_status = player_status._replace(fall_direction=direction)

        new_players = list(self.players)

        new_players[player_idx] = new_player_status

        return self._replace(players=new_players)
