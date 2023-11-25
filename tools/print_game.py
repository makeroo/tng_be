from tng.game.types import Direction, Tile, FallDirection
from tng.game.game import Board, Cell, Game, Player
from tng.game.moves import Move, MoveType


cell_character: dict[tuple[Tile | None, Direction], str] = {
    (None, Direction.n): '•',
    (None, Direction.e): '•',
    (None, Direction.s): '•',
    (None, Direction.w): '•',
    (Tile.start, Direction.n): '╗',
    (Tile.start, Direction.e): '╝',
    (Tile.start, Direction.s): '╚',
    (Tile.start, Direction.w): '╔',
    (Tile.key, Direction.n): 'ໃ',
    (Tile.key, Direction.e): 'ໃ',
    (Tile.key, Direction.s): 'ໃ',
    (Tile.key, Direction.w): 'ໃ',
    (Tile.gate, Direction.n): '⌘',
    (Tile.gate, Direction.e): '⌘',
    (Tile.gate, Direction.s): '⌘',
    (Tile.gate, Direction.w): '⌘',
    (Tile.wax_eater, Direction.n): '⍨',
    (Tile.wax_eater, Direction.e): '⍨',
    (Tile.wax_eater, Direction.s): '⍨',
    (Tile.wax_eater, Direction.w): '⍨',
    (Tile.straight_passage, Direction.n): '║',
    (Tile.straight_passage, Direction.e): '═',
    (Tile.straight_passage, Direction.s): '║',
    (Tile.straight_passage, Direction.w): '═',
    (Tile.t_passage, Direction.n): '╦',
    (Tile.t_passage, Direction.e): '╣',
    (Tile.t_passage, Direction.s): '╩',
    (Tile.t_passage, Direction.w): '╠',
    (Tile.four_way_passage, Direction.n): '╬',
    (Tile.four_way_passage, Direction.e): '╬',
    (Tile.four_way_passage, Direction.s): '╬',
    (Tile.four_way_passage, Direction.w): '╬',
    (Tile.pit, Direction.n): '⌾',
    (Tile.pit, Direction.e): '⌾',
    (Tile.pit, Direction.s): '⌾',
    (Tile.pit, Direction.w): '⌾',
}


class Colors:
    """ANSI color codes"""

    red = "\033[1;31m"
    yellow = "\033[1;33m"
    green = "\033[1;32m"
    blue = "\033[1;34m"
    purple = "\033[1;35m"

    # gate & keys
    gate_and_keys = "\033[1;37m"

    # wax
    wax_monster = "\033[0;37m"

    # passages
    passages = "\033[1;30m"

    empty = "\033[2m"

    end = "\033[0m"


def print_cell(cell: Cell) -> str:
    p = len(cell.players)

    if p == 1:
        color = getattr(Colors, cell.players[0].value)

    elif p > 1:
        color = Colors.gate_and_keys

    elif cell.tile is None:
        color = Colors.empty

    elif cell.tile in (Tile.gate, Tile.key):
        color = Colors.gate_and_keys

    elif cell.tile is Tile.wax_eater:
        color = Colors.wax_monster

    else:
        color = Colors.passages

    if p <= 1:
        return color + cell_character[(cell.tile, cell.direction)] + Colors.end

    return str(len(cell.players))


def print_board(board: Board) -> str:
    matrix = [
        ''.join(print_cell(cell) for cell in board.cells[i : i + board.edge_length])
        for i in range(0, len(board.cells), board.edge_length)
    ]

    return '\n'.join(matrix)


def print_player(p: Player) -> str:
    r = []

    if p.falling:
        if p.pos is None:
            raise Exception('falling player without pos')

        if p.fall_direction is None:
            r.append(f'falling from {p.pos.x},{p.pos.y}')

        elif p.fall_direction is FallDirection.column:
            r.append(f'falling on column {p.pos.x}')

        elif p.fall_direction is FallDirection.row:
            r.append(f'falling on row {p.pos.y}')

        else:
            raise Exception(f'unknown fall direction {p.fall_direction}')

    if p.has_key:
        r.append('key')

    if p.has_light:
        r.append('has light')

    r.append(f'nerves: {p.nerves}')

    return getattr(Colors, p.color.value) + ' '.join(r) + Colors.end


def print_game(game: Game) -> str:
    board = print_board(game.board)

    p = game.players[game.turn]

    turn = f'\nturn: {getattr(Colors, p.color.value)}{p.color.value}{Colors.end}, phase: {game.phase.value}'

    return board + '\n\n' + '\n'.join(print_player(ps) for ps in game.players) + turn


def print_move(m: Move) -> str:
    color = getattr(Colors, m.player.value)

    if m.param.move == MoveType.place_tile:
        place_tile = m.param

        t = f'place at {place_tile.pos.x},{place_tile.pos.y}'

    elif m.param.move == MoveType.rotate_tile:
        rotate_tile = m.param
        t = f'rotate {rotate_tile.direction.value}'

    elif m.param.move == MoveType.stay:
        t = 'stay'

    elif m.param.move == MoveType.walk:
        walk = m.param
        t = f'walk {walk.direction.value}'

    elif m.param.move == MoveType.fall:
        fall = m.param
        t = f'fall {fall.direction.value}'

    elif m.param.move == MoveType.drop:
        drop = m.param
        t = f'drop on {drop.place}'

    else:
        raise ValueError

    return color + t + Colors.end
