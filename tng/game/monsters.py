from .game import Cell, Board
from .types import Tile, Direction, is_monster, Position


class VisibleMonsters:
    def __init__(self, board: Board) -> None:
        self.board = board
        self.triggered_monsters: dict[Position, Cell] = {}
        self.visited_coords: set[Position] = set()

    def check(self, pos: Position) -> None:
        """
        pos is either the position from which a player move or to which it landed
        """

        starting_cell = self.board.at(pos)

        if starting_cell.tile is None:
            return

        queue: list[tuple[Position, Cell, Direction]] = [
            (pos, starting_cell, d) for d in starting_cell.open_directions()
        ]

        while queue:
            from_pos, from_cell, d = queue.pop()

            if from_cell.tile is None:
                continue

            if not self.board.is_connected(from_pos, d):
                continue

            to_pos = d.neighbor(from_pos, self.board.edge_length)

            if to_pos in self.visited_coords:
                continue

            self.visited_coords.add(to_pos)

            to_cell = self.board.at(to_pos)

            if to_cell.tile is None or to_cell.tile is Tile.pit:
                continue

            if is_monster[to_cell.tile]:
                self.triggered_monsters[to_pos] = to_cell

                queue.extend((to_pos, to_cell, next_d) for next_d in to_cell.open_directions())

                continue

            queue.append((to_pos, to_cell, d))
