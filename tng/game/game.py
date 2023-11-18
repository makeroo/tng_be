from typing import NamedTuple
from enum import Enum

from .types import Tile, Direction, PlayerColor


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
        return [d.rotate(self.direction) for d in self.tile.open_directions]


class Board(NamedTuple):
    cells: list[Cell]
    edge_length: int  # can be 6 (up to 4 players) or 7 (5 players)

    def at(self, x: int, y: int) -> Cell:
        return self.cells[y * self.edge_length + x]

    def place_tile(self, x: int, y: int, tile: Tile, direction: Direction = Direction.n) -> 'Game':
        new_cells = list(self.cells)

        pos = y * self.edge_length + x

        orig_cell = new_cells[pos]

        new_cell = orig_cell._replace(
            tile=tile,
            direction=direction,
        )

        new_cells[pos] = new_cell

        return self._replace(cells=new_cells)

    def move_player(
        self,
        player_color: PlayerColor,
        from_x: int | None,
        from_y: int | None,
        to_x: int,
        to_y: int,
    ) -> 'Board':
        new_cells = list(self.cells)

        if from_x is not None:
            old_pos = from_y * self.edge_length + from_x
            old_cell = self.cells[old_pos]

            new_cells[old_pos] = old_cell.remove_player(player_color)

        new_pos = to_y * self.edge_length + to_x
        new_cell = self.cells[new_pos]

        new_cells[new_pos] = new_cell.add_player(player_color)

        return self._replace(cells=new_cells)

    def visible_cells_from(self, x: int, y: int) -> list[Cell]:
        cell = self.at(x, y)
        directions = cell.open_directions()
        r = []

        for direction in directions:
            dx, dy = direction.neighbor(x, y, self.edge_length)

            dcell = self.at(dx, dy)

            if dcell.tile is None:
                r.append(dcell)

        return r


class Player(NamedTuple):
    color: PlayerColor

    has_key: bool
    nerves: int
    has_light: bool
    falling: bool

    # player position:
    # both None -> initial turn, not yet on map
    # both int -> on map
    # only one int -> falling
    x: int | None
    y: int | None


class Phase(Enum):
    place_start = 'place_start'
    rotate_start = 'rotate_start'
    discover_start_tiles = 'discover_start_tiles'
    rotate_discovered_start_tile = 'rotate_discovered_start_tile'
    move_player = 'move_player'


class Game(NamedTuple):
    board: Board
    tile_holder: list[Tile]
    draw_index: int  # index in the tile_holder deck

    players: list[Player]

    turn: int  # index in the players array

    phase: Phase

    last_placed_tile_x: int
    last_placed_tile_y: int

    def new_phase(self, phase: Phase) -> 'Game':
        """
        FSM check is up to TNGFSM, here we take the phase as it is.
        """

        return self._replace(phase=phase)

    def set_turn(self, turn: int) -> 'Game':
        return self._replace(turn=turn)

    def draw_tile(self):
        return self._replace(draw_index=self.draw_index + 1)

    def place_tile(self, x: int, y: int, tile: Tile, direction: Direction = Direction.n) -> 'Game':
        return self._replace(
            board=self.board.place_tile(x, y, tile, direction),
            last_placed_tile_x=x,
            last_placed_tile_y=y,
        )

    def move_player(self, player_idx: int, x: int, y: int) -> 'Game':
        player_status = self.players[player_idx]

        new_players = list(self.players)

        new_players[player_idx] = player_status._replace(x=x, y=y)

        return self._replace(
            players=new_players,
            board=self.board.move_player(
                player_status.color, player_status.x, player_status.y, x, y
            ),
        )

    def change_nerves(self, player_idx: int, delta: int) -> 'Game':
        player_status = self.players[player_idx]

        player_status = player_status._replace(nerves=player_status.nerves + delta)

        new_players = list(self.players)
        new_players[player_idx] = player_status

        return self._replace(players=new_players)


    def is_enlightened(self, x: int, y: int) -> bool:
        """
        A tile is enlightened if either a player is in it or
        there is a player (with a lit candle) in a directly
        connected tile.
        """
        cell = self.board.at(x, y)

        if cell.players:
            return True

        return any(
            p.has_light
            for c in self.board.visible_cells_from(x, y)
            for p in c.players
            if self.player_status(p).has_light
        )

    def player_status(self, player: PlayerColor) -> Player:
        for p in self.players:
            if p.color == player:
                return p

        raise ValueError('player not found')
