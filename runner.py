#!/usr/bin/env python3
"""
Runner module for orchestrating the "botwar ship" game.
"""
import os
import subprocess
import logging
from typing import List, Dict, Any
import json
import time

from judger.judger import Judger
from utils.constants import TIMEOUT


class Runner:
    """
    Runner class that orchestrates the game flow, manages the judger,
    and handles communication with agent executables.
    """

    def __init__(self, agent_paths: List[str]):
        """
        Initialize the Runner with paths to agent executables.
        
        Args:
            agent_paths: List of paths to the three agent executables
        """
        self.judger = None
        self.agent_paths = agent_paths
        self.log_path = None
        self.turn = 0
        self.logger = logging.getLogger("Runner")
        self.game_history = []

    def initialize_game(self, map_path: str, log_path: str = "./data/logs/final_results.json"):
        """
        Initialize the game with the specified map.
        
        Args:
            map_path: Path to the map JSON file
            log_path: Path for logging game data
        """
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # Initialize the judger
        self.judger = Judger.initialize(map_path)

        self.logger.info(f"Game initialized with map: {map_path}")

    def run_game(self):
        """
        Run the game until completion (all ships sink or max moves reached).
        """
        # Phase 0: Get starting positions from agents
        start_positions = []
        agent_inputs = self.judger.generate_agent_inputs()
        for i, agent_path in enumerate(self.agent_paths):
            agent_input = agent_inputs[i]
            position_str = self.execute_agent(agent_path, agent_input)
            # Parse the position from the agent's output
            # Format should be "q r s"
            try:
                q, r, s = map(int, position_str.strip().split())
            except Exception as e:
                self.logger.error(
                    f"Error parsing starting position for agent {i + 1}: {str(e)}. The output was: '{position_str}'")
                q, r, s = 0, 0, 0
            start_positions.append({"q": q, "r": r, "s": s})

        # Validate and set starting positions
        self.judger.validate_start_positions(start_positions)

        # Log the game state
        self.game_history.append(self._get_current_game_state())

        # Phase 1 onwards: Move phase
        while not self.check_game_end():
            self.turn += 1  # TODO: check
            self.logger.info(f"Turn {self.turn}")

            # Generate inputs for all agents
            agent_inputs = self.judger.generate_agent_inputs()

            # Get moves from all agents
            moves = []
            for i, agent_path in enumerate(self.agent_paths):
                if self.judger.game_state.players[i].alive:
                    move_str = self.execute_agent(agent_path, agent_inputs[i])
                    moves.append(move_str)
                else:
                    moves.append("")  # Empty move for inactive agents

            # Process the turn with the moves
            self.judger.process_turn(moves)

            # Log the game state
            self.game_history.append(self._get_current_game_state())

    def execute_agent(self, agent_path: str, input_data: str) -> str:
        """
        Execute an agent program and get its response.
        
        Args:
            agent_path: Path to the agent executable
            input_data: Input data to send to the agent
            
        Returns:
            The agent's response as a string
        """
        try:
            # Create a temporary file for the input
            input_file = "MAP.INP"
            # get agent directory path
            agent_path = os.path.abspath(agent_path)
            agent_dir = os.path.dirname(agent_path)

            with open(os.path.join(agent_dir, input_file), "w") as f:
                f.write(input_data)

            # Execute the agent with the input file
            result = subprocess.run(
                [agent_path, input_file],
                cwd=agent_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            if result.returncode != 0:
                self.logger.error(f"Agent execution failed: {result.stderr}")
                return ""

            output_file = "ACT.OUT"
            with open(os.path.join(agent_dir, output_file), "r") as f:
                return f.read()

        except subprocess.TimeoutExpired:
            self.logger.error(f"Agent execution timed out: {agent_path}")
            return ""
        except Exception as e:
            self.logger.error(f"Error executing agent: {str(e)}")
            return ""

    def check_game_end(self) -> bool:
        """
        Check if the game has ended (all ships sunk or max moves reached).
        
        Returns:
            True if the game has ended, False otherwise
        """
        return self.judger.check_game_end()

    def report_results(self):
        """
        Report the final results of the game.
        """
        # Save results to file
        with open(self.log_path, "w") as f:
            json.dump(self.game_history, f)

    def _get_current_game_state(self):
        """
        Log the current game state to a file.
        """
        return self.judger.export_game_state()
