from collections import defaultdict

from .game import Cell, Board
from .types import Tile, is_monster, Position, PlayerColor


class AttackingMonsters:
    def __init__(self, board: Board) -> None:
        self.board = board

        # self.triggered_monsters: dict[Position, Cell] = {}
        # self.visited_coords: set[Position] = set()

        # self.hitten_cells: dict[Position, list[Tile]] = {}

    def trigger_monsters(self, player_moved_from: Position) -> dict[PlayerColor, list[Cell]]:
        """
        Look for monsters in the cell the player moved from and in any direction from it.

        Two phases:
        1. find all monsters triggered by the player move
        2. look for chain reactions

        Returns, for each player a list of monters that hit them.
        """

        r: dict[PlayerColor, list[Cell]] = defaultdict(list)

        # phase 1

        monster_queue: list[Position] = []

        starting_cell = self.board.at(player_moved_from)

        if starting_cell.tile is not None and is_monster[starting_cell.tile]:
            monster_queue.append(player_moved_from)

        for d in starting_cell.open_directions():
            p = player_moved_from

            while True:
                p = d.neighbor(p, self.board.edge_length)

                if p == player_moved_from:
                    break

                cell = self.board.at(p)

                if cell.tile is None or cell.tile is Tile.pit:
                    break

                if is_monster[cell.tile]:
                    monster_queue.append(p)
                    break

        # phase 2

        examined_monsters: set[Position] = set()

        while monster_queue:
            pos = monster_queue.pop()

            if pos in examined_monsters:
                continue

            examined_monsters.add(pos)

            cell = self.board.at(pos)

            if cell.tile is None:
                continue

            for d in cell.open_directions():
                p = pos

                while True:
                    p = d.neighbor(p, self.board.edge_length)

                    if p == pos:
                        break

                    cell = self.board.at(p)

                    if cell.tile is None or cell.tile is Tile.pit:
                        break

                    if is_monster[cell.tile]:
                        monster_queue.append(p)

                    for player in cell.players:
                        r[player].append(cell)

        return r
