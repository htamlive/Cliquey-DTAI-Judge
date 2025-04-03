#!/usr/bin/env python3
"""
Judger module for the "botwar ship" game.
"""
import json
import math
import random
from typing import List, Dict, Any, Optional, Tuple

from models.coordinate import Coordinate
from models.map import Map
from models.player import Player
from models.move import Move
from judger.game_state import GameState
from judger.file_handler import FileHandler
from items.gold import Gold
from items.shield import Shield
from items.danger import Danger
from items.treasure import Treasure
from utils.constants import MAX_MISSILES, TREASURE_MIN_THRESHOLD, TREASURE_MAX_THRESHOLD, MAX_MISSILES_EACH_TURN
from utils.constants import TREASURE_MIN_VALUE, TREASURE_VALUE_DIVISOR, GOLD_DISTRIBUTION_RADIUS
from utils.validators import validate_team_constraints


class Judger:
    """
    Judger class that implements the game rules, validates moves, 
    and updates the game state.
    """

    def __init__(self, file_handler: FileHandler, game_state: GameState, treasure_appearance_turn: int):
        """
        Initialize the Judger with the provided file handler and game state.

        Args:
            file_handler: FileHandler instance for reading and writing files
            game_state: GameState instance representing the current game state
            treasure_appearance_turn: Turn number when the treasure appears
        """
        self.file_handler = file_handler
        self.game_state = game_state
        self.treasure_appearance_turn = treasure_appearance_turn

    @staticmethod
    def initialize(map_path: str) -> 'Judger':
        """
        Initialize the game with the specified map.
        
        Args:
            map_path: Path to the map JSON file

        Returns:
            Judger instance initialized with the map
        """
        file_handler = FileHandler()

        map_data = file_handler.read_json(map_path)

        # Validate required parameters
        if "max_moves" not in map_data:
            raise ValueError("Required parameter 'max_moves' not found in map file")
        max_moves = map_data["max_moves"]

        if "map_radius" not in map_data:
            raise ValueError("Required parameter 'map_radius' not found in map file")
        map_radius = map_data["map_radius"]

        # Create a new game state
        game_state = GameState(radius=map_radius, moves_left=max_moves)

        # Initialize the Judger
        judger = Judger(file_handler, game_state, treasure_appearance_turn=0)

        # Initialize the map
        judger._initialize_map(map_data)

        # Initialize players
        judger._initialize_players()

        # Initialize the treasure appearance turn
        judger._initialize_treasure_appearance_turn(max_moves)

        return judger

    def validate_start_positions(self, positions: List[Dict[str, int]]):
        """
        Validate the starting positions chosen by the agents.
        
        Args:
            positions: List of position dictionaries with q, r, s coordinates
            
        Returns:
            True if the positions are valid, False otherwise
        """
        # Check if the number of positions matches the number of players
        if len(positions) != len(self.game_state.players):
            raise ValueError("Number of positions does not match the number of players")

        for i, position in enumerate(positions):
            player = self.game_state.players[i]
            coord = Coordinate(position["q"], position["r"], position["s"])

            valid_position = True

            # Check if the coordinate is within the map boundaries
            if not self.game_state.map.is_valid_coordinate(coord):
                valid_position = False

            # Check team-specific constraints
            if not validate_team_constraints(i + 1, coord.q, coord.r, coord.s):
                valid_position = False

            # Check if the cell is empty
            cell = self.game_state.map.get_cell(coord)
            if not cell.is_empty():
                valid_position = False

            # Set the player's position
            if not valid_position:
                # randomize the position
                coord = self.get_random_start_position(team_id=i + 1)
            player.position = coord

        self.game_state.started = True

        return True

    def get_random_start_position(self, team_id: int) -> Coordinate:
        """
        Get a random starting position for the specified team.

        Args:
            team_id: The team ID

        Returns:
            Random starting position for the team
        """
        # Get the list of empty cells
        empty_cells = []
        for q in range(-self.game_state.map.radius, self.game_state.map.radius + 1):
            for r in range(max(-self.game_state.map.radius, -q - self.game_state.map.radius),
                           min(self.game_state.map.radius + 1, -q + self.game_state.map.radius + 1)):
                s = -q - r
                coord = Coordinate(q, r, s)
                if self.game_state.map.is_valid_coordinate(coord):
                    cell = self.game_state.map.get_cell(coord)
                    if cell.is_empty():
                        empty_cells.append(coord)

        valid_cells = []
        for coord in empty_cells:
            q, r, s = coord.q, coord.r, coord.s
            if validate_team_constraints(team_id, q, r, s):
                valid_cells.append(coord)

        # Randomly select a valid cell
        return random.choice(valid_cells)

    def process_turn(self, moves: List[str]) -> GameState:
        """
        Process a turn with the provided moves.

        Args:
            moves: List of move strings from the agents

        Returns:
            Updated game state
        """
        # Parse the moves
        parsed_moves = []
        for i, move_str in enumerate(moves):
            if self.game_state.players[i].alive and move_str:
                move = self.file_handler.parse_agent_input(move_str)
                parsed_moves.append(move)
            else:
                parsed_moves.append(Move())

        # Decrement the number of moves left
        self.game_state.moves_left -= 1

        # 1. Move all players
        self.game_state.update(parsed_moves)

        # 2. Check for collisions
        self.check_collisions()

        # 3. Check for treasure appearance
        self._check_treasure_appearance()

        # 4. Apply item effects (collect gold, shields, etc.)
        self.apply_item_effects()

        # 5. Handle missiles
        self.handle_missiles(parsed_moves)

        # 6. Apply item effects after missiles
        self.apply_item_effects()

        return self.game_state

    def generate_agent_inputs(self) -> List[str]:
        """
        Generate input strings for all agents based on the current game state.
        
        Returns:
            List of input strings for the agents
        """
        inputs = []
        for i, player in enumerate(self.game_state.players):
            input_str = self.file_handler.format_agent_output(self.game_state, i)
            inputs.append(input_str)
        return inputs

    def export_game_state(self) -> dict[str, Any]:
        """
        Export the current game state to a JSON string.
        
        Returns:
            JSON string representation of the game state
        """
        return self.game_state.to_dict()

    def check_collisions(self):
        """
        Check for and handle ship collisions, including both:
        - Ships ending up at the same position
        - Ships swapping positions (crossing paths)
        """
        # Store previous positions for detecting swaps
        previous_positions = {
            i: self.game_state.players[i].previous_position
            for i in range(len(self.game_state.players))
            if self.game_state.players[i].previous_position
        }

        # Store current positions for detecting overlaps
        current_positions = {
            i: self.game_state.players[i].position
            for i in range(len(self.game_state.players))
        }

        for idx, player in enumerate(self.game_state.players):
            if not player.alive:
                continue
            position = player.position
            prev_position = player.previous_position

            # First pass: check for ships at the same position
            for other_idx, other_position in current_positions.items():
                if idx != other_idx and position == other_position:
                    player.alive = False

            # Second pass: check for ships swapping positions
            for other_idx, other_prev_position in previous_positions.items():
                other_position = current_positions[other_idx]
                if idx != other_idx and position == other_prev_position and prev_position == other_position:
                    player.alive = False

    def validate_missile(self, player: Player, targets: List[Coordinate]) -> bool:
        """
        Check if a missile target is valid for a player.

        Args:
            player: The player firing the missile
            targets: List of missile
        Returns:
            True if the missile targets are valid, False otherwise
        """
        # Can't fire missiles if player is not alive
        if not player.alive:
            return False
        # Limit missile targets to 2
        if len(targets) == 0 or len(targets) > MAX_MISSILES_EACH_TURN:
            return False
        # Check if player has enough missiles
        if player.missiles < len(targets):
            return False
        # Check if missile targets are valid
        for target in targets:
            if not self.game_state.map.is_valid_coordinate(target) or \
                    target == player.position:
                return False
        return True

    def handle_missiles(self, moves: List[Optional[Move]]):
        """
        Handle missile firing and their effects.
        
        Args:
            moves: List of parsed moves from agents
        """
        # Record missile targets for each player
        missile_targets = {}

        for player in self.game_state.players:
            player.missiles_fired = []

        for i, move in enumerate(moves):
            player = self.game_state.players[i]
            targets = move.missile_targets

            if not self.validate_missile(player, targets):
                continue

            # Record valid targets
            for target in move.missile_targets:
                # Add target to the list
                if target not in missile_targets:
                    missile_targets[target] = 0
                missile_targets[target] += 1

                # Update player's missiles fired
                player.missiles_fired.append(target)
            player.missiles -= len(move.missile_targets)

        # Apply missile effects to players
        for i, player in enumerate(self.game_state.players):
            pos = player.position
            if pos in missile_targets:
                # Player hit by missiles
                hit_count = missile_targets[pos]
                if hit_count > 0:
                    # Calculate gold lost
                    gold_lost = player.hit_by_missile(hit_count)

                    # Distribute lost gold to nearby cells
                    if gold_lost > 0:
                        self._distribute_lost_gold(pos, gold_lost)

    def apply_item_effects(self):
        """
        Apply the effects of items at player positions.
        """
        for player in self.game_state.players:
            if not player.alive:
                continue

            cell = self.game_state.map.get_cell(player.position)
            if not cell.is_empty():
                item = cell.get_item()
                if isinstance(item, Treasure):
                    self.game_state.treasure_remaining = False
                item = item.apply_effect(player, self.game_state.map)
                cell.set_item(item)

    def check_game_end(self) -> bool:
        """
        Check if the game has ended (all ships sunk or max moves reached).
        
        Returns:
            True if the game has ended, False otherwise
        """
        # Check if there are no moves left
        if self.game_state.moves_left <= 0:
            return True

        # Check if all ships have sunk
        all_sunk = True
        for player in self.game_state.players:
            if player.alive:
                all_sunk = False
                break

        return all_sunk

    def _initialize_map(self, map_data: Dict[str, Any]):
        """
        Initialize the map from the provided map data.
        
        Args:
            map_data: Map data from the JSON file
        """
        self.game_state.map = Map(radius=map_data["map_radius"])

        # Add cells to the map
        for cell_data in map_data.get("cells", []):
            q = cell_data.get("q", 0)
            r = cell_data.get("r", 0)
            s = cell_data.get("s", 0)
            value = cell_data.get("value", 0)

            coord = Coordinate(q, r, s)

            # Create the appropriate item based on the value
            if isinstance(value, int) and value > 0:
                self.game_state.map.add_item(coord, Gold(value))
            elif value == "S":
                self.game_state.map.add_item(coord, Shield())
            elif value == "D":
                self.game_state.map.add_item(coord, Danger())

    def _initialize_players(self):
        """
        Initialize the players for the game.
        """
        self.game_state.players = [
            Player(team_id=1, missiles=MAX_MISSILES),
            Player(team_id=2, missiles=MAX_MISSILES),
            Player(team_id=3, missiles=MAX_MISSILES)
        ]

    def _initialize_treasure_appearance_turn(self, max_moves):
        # Calculate the threshold for treasure appearance
        min_threshold = math.ceil(max_moves * TREASURE_MIN_THRESHOLD)
        max_threshold = math.floor(max_moves * TREASURE_MAX_THRESHOLD)

        # Random treasure appearance turn
        self.treasure_appearance_turn = random.randint(min_threshold, max_threshold)

    def _check_treasure_appearance(self):
        """
        Check if the treasure should appear at the center of the map.
        """
        # Skip if treasure has already appeared
        if self.game_state.treasure_appeared:
            return

        if self.game_state.turn == self.treasure_appearance_turn:
            # Calculate treasure value based on total gold collected
            total_gold = sum(player.gold for player in self.game_state.players)
            treasure_value = max(total_gold // TREASURE_VALUE_DIVISOR, TREASURE_MIN_VALUE)

            # Place treasure at the center coordinate (0, 0, 0)
            center = Coordinate(0, 0, 0)
            cell = self.game_state.map.get_cell(center)

            if isinstance(cell.get_item(), Gold):
                treasure_value += cell.get_item().value
            if not cell.is_empty():
                cell.clear_item()
            self.game_state.map.add_item(center, Treasure(treasure_value))

            self.game_state.treasure_appeared = True
            self.game_state.treasure_remaining = True

    def _distribute_lost_gold(self, position: Coordinate, gold_amount: int):
        """
        Distribute lost gold to nearby empty cells.
        
        Args:
            position: The position from which gold is lost
            gold_amount: Amount of gold to distribute
        """
        # Find valid cells in Manhattan distance <= 2
        valid_cells = []
        for q_offset in range(-GOLD_DISTRIBUTION_RADIUS, GOLD_DISTRIBUTION_RADIUS + 1):
            for r_offset in range(max(-GOLD_DISTRIBUTION_RADIUS, -q_offset - GOLD_DISTRIBUTION_RADIUS),
                                  min(GOLD_DISTRIBUTION_RADIUS + 1, -q_offset + GOLD_DISTRIBUTION_RADIUS + 1)):
                s_offset = -q_offset - r_offset

                # Skip the center cell
                if q_offset == 0 and r_offset == 0:
                    continue

                # Calculate new coordinate
                new_coord = Coordinate(
                    position.q + q_offset,
                    position.r + r_offset,
                    position.s + s_offset
                )

                # Skip invalid coordinates
                if not self.game_state.map.is_valid_coordinate(new_coord):
                    continue

                # Check if it's valid and empty
                cell = self.game_state.map.get_cell(new_coord)
                if cell.is_empty() or isinstance(cell.get_item(), Gold) or isinstance(cell.get_item(), Treasure):
                    valid_cells.append(new_coord)

        # If no valid cells, return
        if not valid_cells:
            return

        # Distribute gold to valid cells
        for coord in random.choices(valid_cells, k=gold_amount):
            cell = self.game_state.map.get_cell(coord)
            if isinstance(cell.get_item(), Gold):
                gold_value = cell.get_item().value + 1
                cell.clear_item()
                self.game_state.map.add_item(coord, Gold(gold_value))
            elif isinstance(cell.get_item(), Treasure):
                gold_value = cell.get_item().value + 1
                cell.clear_item()
                self.game_state.map.add_item(coord, Treasure(gold_value))
            else:
                self.game_state.map.add_item(coord, Gold(1))
