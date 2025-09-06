"""
This module implements the TNG game logic.

It:
1. validates a move
2. executes that move returning the resulting game state.
"""

from typing import override

from .game import Game, Phase, GameRuntimeError, Player, Decision
from .moves import (
    Move,
    PlaceTile,
    RotateTile,
    Stay,
    Crawl,
    Fall,
    Land,
    PassKey,
    Charge,
    Block,
    SpendNerve,
    DiscardTile,
    MoveType,
)
from .types import PlayerColor, Tile, Direction, is_monster, FallDirection, Position, is_crumbling
from .monsters import AttackingMonsters


# TODO: check that game has ended

# TODO: move again (spend 1 nerve to move again)


class IllegalMove(ValueError):
    pass


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

    def fall(self, game: Game, player: PlayerColor, move: Fall) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def land(self, game: Game, player: PlayerColor, move: Land) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def pass_key(self, game: Game, player: PlayerColor, move: PassKey) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def block(self, game: Game, player: PlayerColor, move: Block) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def charge(self, game: Game, player: PlayerColor, move: Charge) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def spend_nerve(self, game: Game, player: PlayerColor, move: SpendNerve) -> Game:
        raise IllegalMove(f'illegal move {move} in phase {game.current_phase}')

    def discard_tile(self, game: Game, player: PlayerColor, move: DiscardTile) -> Game:
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

        # this is the start macro phase, there is no need
        # to check for bounds: there are surely tiles to draw
        placed_tile = game.tile_holder[game.draw_index]

        g1 = apply_place_tile(game, player, move, placed_tile, replace_allowed=False)

        g2 = g1.draw_tile()

        # FIXME: if there is one only available rotation force that and skip rotate_discovered_start_title phase

        if placed_tile in (Tile.t_passage, Tile.straight_passage):
            return g2.new_phase(Phase.rotate_discovered_tile)
        if placed_tile == Tile.straight_passage:
            # TODO: calc correct direction and place it accordingly
            pass

        start_pos = g2.players[g2.turn].pos

        if start_pos is None:
            raise GameRuntimeError('current player without pos')

        return next_from_discover_tiles(game, start_pos)


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

        else:
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

        drawn_tile = g1.tile_holder[game.draw_index]

        g2 = g1.draw_tile()

        if is_monster[drawn_tile]:
            return g2.push_phase(Phase.place_monster)

        g3, fallen = check_falling(game, player_status)

        if g3.final_flickers():
            if fallen:
                # TODO: detect game lost if both column and row have empty tiles
                return g3.new_phase(Phase.falling)

            else:
                return g3.new_phase(Phase.final_flickers)

        return g3.set_turn(turn=(game.turn + 1) % len(game.players))

    def crawl(self, game: Game, player: PlayerColor, move: Crawl) -> Game:
        # TODO: sono fermo qua
        # ho capito la VisibleMonster ma questo metodo va tutto ripensato

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
            if player_status.has_light:
                raise GameRuntimeError('empty tile that shouldn\'t')

            if game.final_flickers():
                raise IllegalMove('empty dest tile')

        elif len(dest_cell.players) > 0 and dest_cell.tile is not Tile.gate:
            raise IllegalMove('dest tile already occupied')

        # apply

        new_game = game.move_player(game.turn, dest_pos)

        if dest_cell.tile is None:
            # lights out
            drawn_tile = new_game.tile_holder[new_game.draw_index]

            new_game = new_game.draw_tile().place_tile(dest_pos, drawn_tile)

            if is_monster[drawn_tile]:
                new_game.add_decision(
                    Phase.monster_attack, Decision(player_status.color, MoveType.crawl, 2)
                )

        else:
            drawn_tile = None

        # we calc visible monsters on the NEW table because if the player was in a crumbling tile
        # and moves the opposite way of a monster, that monster will be triggered but the
        # moving player will remain unaffected

        monsters = VisibleMonsters(new_game.board)

        monsters.check(player_status.pos)
        monsters.check(dest_pos)

        new_game = self._activate_monsters(new_game, monsters)

        # if player_cell.tile is None:
        #     raise GameRuntimeError('player\'s cell has no tile')

        if drawn_tile in [Tile.t_passage, Tile.straight_passage]:
            return game.new_phase(Phase.lights_out_rotate)

        new_player_status = game.players[game.turn]

        if new_player_status.falling:
            game = game.new_phase(Phase.fall_direction)

            game = self._activate_monsters(game, monsters)

            return game

        if new_player_status.has_light:
            game = game.relight_near_players(new_player_status)

        else:
            game = game.relight_me(new_player_status)

            new_player_status = game.players[game.turn]

        if new_player_status.pos is None:
            raise GameRuntimeError('moved player lost pos')

        # monsters.check(new_player_status.pos)

        game = self._activate_monsters(game, monsters)

        cells = game.board.visible_cells_from(new_player_status.pos)

        if any(cell.tile is None for cell in cells):
            return game.new_phase(Phase.discover_tiles)

        return game.set_turn((game.turn + 1) % len(game.players))


class PlaceMonster(PhaseLogic):
    pass


class PitsForm(PhaseLogic):
    pass


class Falling(PhaseLogic):
    pass


class TriggerMonsters(PhaseLogic):
    pass


class HitByMonsters(PhaseLogic):
    pass


class LightAndDarkness(PhaseLogic):
    pass


class HurryUp(PhaseLogic):
    pass


class FinalFlickers(PhaseLogic):
    pass


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
            Phase.pits_form: PitsForm(),
            Phase.falling: Falling(),
            Phase.trigger_monsters: TriggerMonsters(),
            Phase.hit_by_monsters: HitByMonsters(),
            Phase.light_and_darkness: LightAndDarkness(),
            Phase.hurry_up: HurryUp(),
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

    def place_monster_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        player_status = game.players[game.turn]

        if player_status.color != player:
            raise IllegalMove('not player turn')

        # apply

        monster_tile = game.tile_holder[game.draw_index - 1]

        new_game = self._apply_place_tile(game, player, move, monster_tile, replace_allowed=True)

        return self._check_falling(new_game, player_status)

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

    def _activate_monsters(self, game: Game, monsters: VisibleMonsters) -> Game:
        if not monsters.triggered_monsters:
            return game

        monsters.cover_cells()

        for p in game.players:
            if p.falling or p.pos is None:
                continue

            hitting_monsters = monsters.hitting(p.pos)

            for monster in hitting_monsters:
                game = self._monster_attack(game, monster, p)

        return game

    def _monster_attack(self, game: Game, monster: Tile, player_status: Player) -> Game:
        if monster == Tile.wax_eater:
            return game.draw_tiles(3).light_out(player_status)

        else:
            raise GameRuntimeError(f'unknown monster {monster}')

    def move_player_land(self, game: Game, player: PlayerColor, move: Land) -> 'Game':
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

        if game.final_flickers():
            # TODO: calc at the end of the previous move
            raise IllegalMove('game ended in loss')

        # apply

        if cell.tile is None:
            drawn_tile = game.tile_holder[game.draw_index]

            new_game = game.draw_tile().place_tile(pos, drawn_tile).move_player(game.turn, pos)

            if drawn_tile in (Tile.straight_passage, Tile.t_passage):
                return game.new_phase(Phase.drop_on_tile)

            if is_monster[drawn_tile]:
                monsters = VisibleMonsters(new_game.board)

                monsters.add_monster(pos)

                monsters.check(pos)

                new_game = self._activate_monsters(new_game, monsters)

                # TODO: new phase: force dropped player to crawl away

                return new_game

            cells = new_game.board.visible_cells_from(pos)

            if any(cell.tile is None for cell in cells):
                return new_game.new_phase(Phase.discover_tiles)

            return new_game.new_phase(Phase.move_player).set_turn(
                (game.turn + 1) % len(game.players)
            )

        new_game = game.move_player(game.turn, pos)

        monsters = VisibleMonsters(new_game.board)

        new_game = self._activate_monsters(new_game, monsters)

        return new_game

    def discover_tiles_place_tile(self, game: Game, player: PlayerColor, move: PlaceTile) -> Game:
        # validate

        player_status = game.players[game.turn]

        # checked in the _apply_place_tile
        # if player_status.color != player:
        #     raise IllegalMove('not player turn')

        if game.final_flickers():
            # TODO: set game lost phase at the previous move
            raise IllegalMove('final flickres')

        # apply

        placed_tile = game.tile_holder[game.draw_index]

        new_game = self._apply_place_tile(
            game, player, move, placed_tile, replace_allowed=False
        ).draw_tile()

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

    return game.place_tile(move.pos, tile, Direction.n)


def next_from_discover_tiles(game: Game, start_pos: Position) -> Game:
    cells = game.board.visible_cells_from(start_pos)

    if any(cell.tile is None for cell in cells):
        return game.new_phase(Phase.discover_tiles)

    raise SubphaseComplete(game)
    # next_player = game.turn + 1

    # if next_player == len(game.players):
    #     g1 = game.set_turn(0)
    #     return g1.new_phase(Phase.move_player)

    # g1 = game.set_turn(next_player)

    # return g1.new_phase(Phase.place_start)


def check_falling(game: Game, player_status: Player) -> tuple[Game, bool]:
    if player_status.pos is None:
        raise GameRuntimeError('player without pos')

    player_cell = game.board.at(player_status.pos)

    if player_cell.tile is None:
        raise GameRuntimeError('player\'s cell has no tile')

    if is_crumbling[player_cell.tile]:
        return (
            game.place_tile(player_status.pos, Tile.pit)
            .player_falls(game.turn)
            .new_phase(Phase.falling)
        ), True

    return game, False  # .set_turn(turn=(game.turn + 1) % len(game.players))
