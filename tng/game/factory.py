from random import shuffle

from .types import Tile, PlayerColor, Direction, Position
from .game import Game, Board, Cell, Player, Phase


class GameFactory:
    standard_deck_up_to_four_players_opening = {
        Tile.t_passage: 4,
        Tile.four_way_passage: 2,
        Tile.straight_passage: 2,
    }

    standard_deck_five_players_opening = {
        Tile.t_passage: 5,
        Tile.four_way_passage: 3,
        Tile.straight_passage: 2,
    }

    standard_deck_up_to_four_players = {
        Tile.key: 6,
        Tile.wax_eater: 12,
        Tile.gate: 4,
        Tile.t_passage: 32 - standard_deck_up_to_four_players_opening[Tile.t_passage],
        Tile.four_way_passage: 12 - standard_deck_up_to_four_players_opening[Tile.four_way_passage],
        Tile.straight_passage: 10 - standard_deck_up_to_four_players_opening[Tile.straight_passage],
    }

    standard_deck_five_players = {
        Tile.key: 7,
        Tile.wax_eater: 10,
        Tile.gate: 4,
        Tile.t_passage: 32 - standard_deck_five_players_opening[Tile.t_passage],
        Tile.four_way_passage: 12 - standard_deck_five_players_opening[Tile.four_way_passage],
        Tile.straight_passage: 10 - standard_deck_up_to_four_players_opening[Tile.straight_passage],
    }

    def build_cards(self, specs: dict[Tile, int]) -> list[Tile]:
        return [v for t, x in specs.items() for v in [t] * x]

    def build_deck(self, initial: dict[Tile, int], remaining: dict[Tile, int]) -> list[Tile]:
        deck_initial = self.build_cards(initial)
        deck_remaining = self.build_cards(remaining)

        shuffle(deck_initial)
        shuffle(deck_remaining)

        return deck_initial + deck_remaining

    def new_game(self, *colors: PlayerColor) -> Game:
        if not colors:
            raise ValueError("no players")

        if len(colors) > 5:
            raise ValueError("too many players")

        if len(colors) != len(set(colors)):
            raise ValueError("duplicated colors")

        if len(colors) == 5:
            edge_length = 7
            initial = self.standard_deck_five_players_opening
            remaining = self.standard_deck_five_players

        else:
            edge_length = 6
            initial = self.standard_deck_up_to_four_players_opening
            remaining = self.standard_deck_up_to_four_players

        g = Game(
            board=Board(
                cells=[
                    Cell(tile=None, direction=Direction.n, players=[])
                    for _ in range(edge_length * edge_length)
                ],
                edge_length=edge_length,
            ),
            tile_holder=self.build_deck(initial, remaining),
            draw_index=0,
            players=[
                Player(
                    color=color,
                    has_key=False,
                    nerves=1,
                    has_light=True,
                    falling=False,
                    pos=None,
                )
                for color in colors
            ],
            turn=0,
            phase=Phase.place_start,
            last_placed_tile_pos=Position(0, 0),
        )

        return g
