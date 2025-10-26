"""
This module implements the TNG game logic.

It:
1. validates a move
2. executes that move returning the resulting game state.
"""

from typing import override

from .game import Cell, Game, Phase, GameRuntimeError, Player, Decision
from .moves import (
    Move,
    PlaceTile,
    RotateTile,
    Stay,
    Crawl,
    OptionalMovement,
    Fall,
    Land,
    PassKey,
    Block,
    MoveAgain,
    DiscardTile,
    MoveType,
)
from .types import PlayerColor, Tile, Direction, is_monster, FallDirection, Position, is_crumbling
from .monsters import AttackingMonsters
from .exc import IllegalMove


# TODO: check that game has ended


class SubphaseComplete(Exception):
    def __init__(self, game: Game) -> None:
        super().__init__()

        self.game = game


class PhaseLogic:
    def place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def rotate_tile(self, game: Game, player: PlayerColor, move: RotateTile) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def stay(self, game: Game, player: PlayerColor, move: Stay) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def crawl(self, game: Game, player: PlayerColor, move: Crawl) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def optional_movement(self, game: Game, player: PlayerColor, move: OptionalMovement) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def fall(self, game: Game, player: PlayerColor, move: Fall) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def land(self, game: Game, player: PlayerColor, move: Land) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def pass_key(self, game: Game, player: PlayerColor, move: PassKey) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def discard_tile(self, game: Game, player: PlayerColor, move: DiscardTile) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def block(self, game: Game, player: PlayerColor, move: Block) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def move_again(self, game: Game, player: PlayerColor, move: MoveAgain) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def sub_phase_complete(self, game: Game, player: PlayerColor, move: Move) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')


class PlaceStart(PhaseLogic):
    @override
    def place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        g1 = apply_place_tile(game, player, move, Tile.start, replace_allowed=False)
        g2 = g1.move_player(g1.turn, move.pos)

        return g2.push_phase(Phase.rotate_placed)

    @override
    def sub_phase_complete(self, game: Game, player: PlayerColor, move: Move) -> Game:
        next_player = game.turn + 1

        if next_player == len(game.players):
            return game.set_turn(0).new_phase(Phase.move_player)

        return game.set_turn(next_player).new_phase(Phase.place_start)


class RotatePlaced(PhaseLogic):
    """
    Sub FSM started whenever a player lands on the board, either at the start or
    landing after a fall.
    """

    @override
    def rotate_tile(self, game: Game, player: PlayerColor, move: RotateTile) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        # apply

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        cell = game.board.at(player_status.pos)

        if cell.tile is None:
            raise GameRuntimeError('player\'s cell has no tile')

        g1 = game.place_tile(player_status.pos, cell.tile, move.direction)

        cells = g1.board.visible_cells_from(player_status.pos)

        if any(cell.tile is None for cell in cells):
            return g1.new_phase(Phase.discover_tiles)

        raise SubphaseComplete(g1)


class DiscoverTiles(PhaseLogic):
    @override
    def place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        if game.final_flickers():
            raise IllegalMove('final flickers')

        placed_tile = game.tile_holder[game.draw_index]

        g1 = apply_place_tile(game, player, move, placed_tile, replace_allowed=False)

        g2 = g1.draw_tile()

        if placed_tile == Tile.t_passage:
            return g2.new_phase(Phase.rotate_discovered_tile)

        start_pos = g2.players[g2.turn].pos

        if start_pos is None:
            raise GameRuntimeError('current player without pos')

        return next_from_discover_tiles(g2, start_pos)


class RotateDiscoveredTile(PhaseLogic):
    @override
    def rotate_tile(self, game: Game, player: PlayerColor, move: RotateTile) -> Game:
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

        return next_from_discover_tiles(new_game, player_status.pos)


class Landing(PhaseLogic):
    """
    Landing phase: the player is falling and must land on a tile.
    See page 10 of the manual for details.
    """

    @override
    def land(self, game: Game, player: PlayerColor, move: Land) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if not player_status.falling:
            # this is actually a game runtime error because
            # we can be on landing phase only if the player is falling
            raise IllegalMove('non falling player')

        if player_status.fall_direction is None:
            raise GameRuntimeError('falling player without fall direction')

        if player_status.pos is None:
            raise GameRuntimeError('falling player without position')

        if move.place < 0 or move.place >= game.board.edge_length:
            raise IllegalMove('out of bounds')

        match player_status.fall_direction:
            case FallDirection.row:
                destination = Position(move.place, player_status.pos.y)
            case FallDirection.column:
                destination = Position(player_status.pos.x, move.place)

        cell = game.board.at(destination)

        if cell.tile is not None and (
            any(
                game.board.at(Position(ccrow, player_status.pos.y)).tile is None
                for ccrow in range(game.board.edge_length)
            )
            if player_status.fall_direction is FallDirection.column
            else any(
                game.board.at(Position(player_status.pos.x, cccol)).tile is None
                for cccol in range(game.board.edge_length)
            )
        ):
            raise IllegalMove('tile not empty')

        if cell.tile is not None:
            drawn_tile = cell.tile

            g1 = game.move_player(game.turn, destination)

        elif game.final_flickers():
            return game.new_phase(Phase.game_lost)

        else:
            drawn_tile = game.tile_holder[game.draw_index]

            g1 = (
                game.draw_tile()
                .place_tile(destination, drawn_tile)
                .move_player(game.turn, destination)
            )

        if is_monster[drawn_tile]:
            monsters = AttackingMonsters(g1.board)

            attacked_players_colors = monsters.trigger_monsters(destination)

            g2 = activate_monsters(g1, attacked_players_colors)

            g3 = g2.add_decision(Decision(player, MoveType.crawl))

            return g3

        if drawn_tile in (Tile.t_passage, Tile.straight_passage):
            # note: there is no constraint that forces the rotation
            # so that the straight is aligned to an already placed tile

            return g1.push_phase(Phase.rotate_discovered_tile)

        if any(cell.tile is None for cell in g1.board.visible_cells_from(destination)):
            return g1.push_phase(Phase.discover_tiles)

        return g1.new_phase(Phase.move_player)

    def sub_phase_complete(self, game: Game, player: PlayerColor, move: Move) -> Game:
        """
        TODO: either returning from discovery or from monster
        """


class MovePlayer(PhaseLogic):
    def stay(self, game: Game, player: PlayerColor, move: Stay) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.falling:
            raise IllegalMove('falling player')

        if not player_status.has_light and player_status.nerves == 0:
            raise IllegalMove('no nerves, forced to crawl')

        # apply

        if not player_status.has_light:
            g1 = game.change_nerves(game.turn, -1)

        elif player_status.nerves < 2:
            g1 = game.change_nerves(game.turn, +1)

        else:
            g1 = game

        drawn_tile = g1.tile_holder[g1.draw_index]

        g2 = g1.draw_tile()

        if is_monster[drawn_tile]:
            return g2.push_phase(Phase.place_monster)

        g3, fallen = check_falling(game, player_status)

        if g3.final_flickers():
            if fallen:
                # TODO: detect game lost if both column and row have empty tiles
                return g3.push_phase(Phase.falling)

            else:
                return g3.new_phase(Phase.final_flickers)

        return g3.set_turn(turn=(game.turn + 1) % len(game.players))

    def crawl(self, game: Game, player: PlayerColor, move: Crawl) -> Game:
        # validate move

        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if player_status.falling:
            raise IllegalMove('falling player')

        if player_status.pos is None:
            raise GameRuntimeError('player without pos')

        player_cell = game.board.at(player_status.pos)

        if player_cell.tile is None:
            raise GameRuntimeError('player\'s cell has no tile')

        if move.direction not in player_cell.open_directions():
            raise IllegalMove('illegal direction')

        dest_pos = game.board.dest_coords(player_status.pos, move.direction)

        dest_cell = game.board.at(dest_pos)

        if dest_cell.tile is None:
            if player_status.has_light:
                raise GameRuntimeError('empty tile that shouldn\'t')

            if game.final_flickers():
                if any(
                    cell.tile is not None
                    for cell in game.board.visible_cells_from(player_status.pos)
                ):
                    raise IllegalMove('empty dest tile')

                return game.new_phase(Phase.game_lost)

        elif len(dest_cell.players) > 0 and dest_cell.tile is not Tile.gate:
            raise IllegalMove('dest tile already occupied')

        # apply

        g1 = game.move_player(game.turn, dest_pos)

        if is_crumbling[player_cell.tile]:
            g2 = g1.place_tile(player_status.pos, Tile.pit)
        else:
            g2 = g1

        if dest_cell.tile == Tile.pit:
            return g2.player_falls(game.turn).push_phase(Phase.falling)

        if dest_cell.tile is None:
            # lights out
            drawn_tile = g2.tile_holder[g2.draw_index]

            g3 = g2.draw_tile().place_tile(dest_pos, drawn_tile)

            if is_monster[drawn_tile]:
                # this is a move, not a decision, but from the
                # f/e pov both actions (nerves and moving) are to be taken
                # at once, therefore I use this mechanism on the b/e
                g3.add_decision(
                    Decision(player_status.color, MoveType.crawl),
                )

        else:
            drawn_tile = None

            g3 = g2

        # we calc visible monsters on the NEW table because if the player was in a crumbling tile
        # and moves the opposite way of a monster, that monster will be triggered but the
        # moving player will remain unaffected

        monsters = AttackingMonsters(g3.board)

        attacks = monsters.trigger_monsters(player_status.pos)

        g4 = activate_monsters(g3, attacks)

        if g4.decisions:
            return g4

        g5 = refresh_lighting(g4)

        if drawn_tile in [Tile.t_passage, Tile.straight_passage]:
            return g5.new_phase(Phase.rotate_discovered_tile)

        player_status5 = g5.players[g5.turn]

        if player_status5.pos is None:
            raise GameRuntimeError('player without pos')

        cells = g5.board.visible_cells_from(player_status5.pos)

        if any(cell.tile is None for cell in cells):
            return g5.push_phase(Phase.discover_tiles)

        if player_status5.nerves > 0:
            return g5.add_decision(Decision(player_status.color, MoveType.optional_movement))

        if g5.final_flickers():
            return g5.new_phase(Phase.final_flickers)

        return g5.set_turn((g5.turn + 1) % len(g5.players))

    def sub_phase_complete(self, game: Game, player: PlayerColor, move: Move) -> Game:
        """
        TODO return from discover tiles, falling or place_monster
        """


class PlaceMonster(PhaseLogic):
    @override
    def place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        # apply

        monster_tile = game.tile_holder[game.draw_index - 1]

        # TODO: if player is in lights out, the monster disappears soon. We can either:
        # 1. discard it
        # 2. place it and then remove it after activation check (if the player falls)
        # right now we do 2.

        g1 = apply_place_tile(game, player, move, monster_tile, replace_allowed=True)

        raise SubphaseComplete(g1)


class Falling(PhaseLogic):
    @override
    def fall(self, game: Game, player: PlayerColor, move: Fall) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if not player_status.falling:
            raise IllegalMove('non falling player')

        if player_status.fall_direction is not None:
            raise IllegalMove('already has fall direction')

        if player_status.pos is None:
            raise GameRuntimeError('falling player without position')

        if move.direction not in (FallDirection.row, FallDirection.column):
            raise IllegalMove('illegal fall direction')

        raise SubphaseComplete(
            game.fall_direction(game.turn, move.direction)
            # .set_turn(turn=(game.turn + 1) % len(game.players))
            # .new_phase(Phase.move_player)
        )


class FinalFlickers(PhaseLogic):
    @override
    def discard_tile(self, game: Game, player: PlayerColor, move: DiscardTile) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        if not game.final_flickers():
            raise IllegalMove('not in final flickers')

        if move.pos is not None:
            cell = game.board.at(move.pos)

            if cell.tile is None:
                raise IllegalMove('empty cell')

            if len(cell.players) > 0:
                raise IllegalMove('cell occupied')

        elif player_status.nerves == 0:
            raise IllegalMove('no nerves, must discard a tile')

        # apply

        if move.pos is not None:
            g1 = game.place_tile(move.pos, Tile.pit)
        else:
            g1 = game.change_nerves(game.turn, -1)

        return g1.set_turn((game.turn + 1) % len(game.players))


class GameWon(PhaseLogic):
    pass


class GameLost(PhaseLogic):
    pass


class TNGFSM:
    def __init__(self) -> None:
        self.phases = {
            Phase.place_start: PlaceStart(),
            Phase.rotate_placed: RotatePlaced(),
            Phase.discover_tiles: DiscoverTiles(),
            Phase.rotate_discovered_tile: RotateDiscoveredTile(),
            Phase.landing: Landing(),
            Phase.move_player: MovePlayer(),
            Phase.place_monster: PlaceMonster(),
            Phase.falling: Falling(),
            Phase.final_flickers: FinalFlickers(),
            Phase.game_lost: GameLost(),
            Phase.game_won: GameWon(),
        }

    def apply(self, game: Game, move: Move) -> Game:
        try:
            return self._apply(game, move)

        except SubphaseComplete as e:
            game = e.game

            return self._apply_sub_phase_complete(game, move)

    def _apply(self, game: Game, move: Move) -> Game:
        logic = self.phases[game.current_phase]

        handler = getattr(logic, move.param.move.value)

        return handler(game, move.player, move.param)

    def _apply_sub_phase_complete(self, game: Game, move: Move) -> Game:
        g1 = game.pop_phase()

        if not g1.phases:
            raise GameRuntimeError('no subphase running')

        logic = self.phases[g1.current_phase]

        return logic.sub_phase_complete(g1, move.player, move.param)

    # def discover_tiles_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
    #     # validate

    #     player_status = game.players[game.turn]

    #     # checked in the _apply_place_tile
    #     # if player_status.color != player:
    #     #     raise IllegalMove('not player turn')

    #     if game.final_flickers():
    #         # TODO: set game lost phase at the previous move
    #         raise IllegalMove('final flickres')

    #     # apply

    #     placed_tile = game.tile_holder[game.draw_index]

    #     new_game = self._apply_place_tile(
    #         game, player, move, placed_tile, replace_allowed=False
    #     ).draw_tile()

    #     if placed_tile in (Tile.t_passage, Tile.straight_passage):
    #         return new_game.new_phase(Phase.rotate_discovered_tile)

    #     if player_status.pos is None:
    #         raise GameRuntimeError('player without pos')

    #     cells = new_game.board.visible_cells_from(player_status.pos)

    #     if any(cell.tile is None for cell in cells):
    #         return new_game.new_phase(Phase.discover_tiles)

    #     return new_game.new_phase(Phase.move_player).set_turn((game.turn + 1) % len(game.players))

    # def rotate_discovered_tile_rotate_tile(
    #     self, game: Game, player: PlayerColor, move: RotateTile
    # ) -> Game:
    #     # validate move

    #     player_status = game.players[game.turn]

    #     if player_status.color != player:
    #         raise IllegalMove('not player turn')

    #     if player_status.pos is None:
    #         raise GameRuntimeError('player without pos')

    #     last_placed_cell = game.board.at(game.last_placed_tile_pos)

    #     if last_placed_cell.tile is None:
    #         raise GameRuntimeError('empty cell')

    #     new_game = game.place_tile(game.last_placed_tile_pos, last_placed_cell.tile, move.direction)

    #     if player_status.pos not in new_game.board.visible_cells_coords_from(
    #         new_game.last_placed_tile_pos
    #     ):
    #         raise IllegalMove('not_connected')

    #     # apply

    #     cells = new_game.board.visible_cells_from(player_status.pos)

    #     if any(cell.tile is None for cell in cells):
    #         return new_game.new_phase(Phase.discover_tiles)

    #     return new_game.new_phase(Phase.move_player).set_turn(
    #         (new_game.turn + 1) % len(new_game.players)
    #     )

    # def lights_out_rotate_rotate_tile(
    #     self, game: Game, player: PlayerColor, move: RotateTile
    # ) -> Game:
    #     # validate move

    #     player_status = game.players[game.turn]

    #     if player_status.color != player:
    #         raise IllegalMove('not player turn')

    #     if player_status.pos is None:
    #         raise GameRuntimeError('player without pos')

    #     last_placed_cell = game.board.at(game.last_placed_tile_pos)

    #     if last_placed_cell.tile is None:
    #         raise GameRuntimeError('empty cell')

    #     new_game = game.place_tile(game.last_placed_tile_pos, last_placed_cell.tile, move.direction)

    #     if player_status.pos not in new_game.board.visible_cells_coords_from(
    #         new_game.last_placed_tile_pos
    #     ):
    #         raise IllegalMove('not_connected')

    #     # apply

    #     new_game = new_game.relight_me(player_status)

    #     player_status = new_game.players[game.turn]

    #     monsters = VisibleMonsters(new_game.board)

    #     if player_status.pos is None:
    #         raise GameRuntimeError('player without pos')

    #     monsters.check(player_status.pos)

    #     new_game = activate_monsters(new_game, monsters)

    #     cells = new_game.board.visible_cells_from(player_status.pos)

    #     if any(cell.tile is None for cell in cells):
    #         return new_game.new_phase(Phase.discover_tiles)

    #     return new_game.new_phase(Phase.move_player).set_turn((game.turn + 1) % len(game.players))


def apply_place_tile(
    game: Game, player: PlayerColor, move: PlaceTile, tile: Tile, *, replace_allowed: bool
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

    if not replace_allowed and cell.tile is not None:
        raise IllegalMove('tile not empty')

    # apply

    if player_status.pos is not None and tile == Tile.straight_passage:
        # force correct direction
        open_dirs = game.board.at(player_status.pos).open_directions()

        if Direction.n in open_dirs or Direction.s in open_dirs:
            dir = Direction.n
        else:
            dir = Direction.e

    else:
        dir = Direction.n

    return game.place_tile(move.pos, tile, dir)


def next_from_discover_tiles(game: Game, start_pos: Position) -> Game:
    cells = game.board.visible_cells_from(start_pos)

    if any(cell.tile is None for cell in cells):
        return game.new_phase(Phase.discover_tiles)

    raise SubphaseComplete(game)


def check_falling(game: Game, player_status: Player) -> tuple[Game, bool]:
    if player_status.pos is None:
        raise GameRuntimeError('player without pos')

    player_cell = game.board.at(player_status.pos)

    if player_cell.tile is None:
        raise GameRuntimeError('player\'s cell has no tile')

    if is_crumbling[player_cell.tile]:
        return (game.place_tile(player_status.pos, Tile.pit).player_falls(game.turn)), True

    return game, False


def activate_monsters(game: Game, attacks: dict[PlayerColor, list[Cell]]) -> Game:
    if not attacks:
        return game

    for p in game.players:
        hitting_monsters = attacks.get(p.color)

        if not hitting_monsters:
            continue

        for monster in hitting_monsters:
            monster_tile = monster.tile

            if monster_tile is None:
                raise GameRuntimeError('monster cell without tile')

            game = monster_attack(game, monster_tile, p)

    return game


def monster_attack(game: Game, monster: Tile, player_status: Player) -> Game:
    if monster == Tile.wax_eater:
        if player_status.nerves > 0:
            return game.add_decision(
                Decision(player_status.color, MoveType.block),
            )

        else:
            return game.draw_tiles(3).light_out(player_status)

    else:
        raise GameRuntimeError(f'unknown monster {monster}')


def enlighted_cells(game: Game) -> set[Position]:
    visible_cells: set[Position] = set()

    for player_status in game.players:
        if player_status.pos is None:
            continue

        visible_cells.add(player_status.pos)

        if not player_status.has_light:
            continue

        visible_cells.update(game.board.visible_cells_coords_from(player_status.pos))

    return visible_cells


def refresh_lighting(game: Game) -> Game:
    cells = enlighted_cells(game)

    return game.drop_tiles(
        Position(x, y)
        for x in range(game.board.edge_length)
        for y in range(game.board.edge_length)
        if Position(x, y) not in cells
    )
