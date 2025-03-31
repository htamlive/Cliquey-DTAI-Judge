#!/usr/bin/env python3
"""
Game state module for the "botwar ship" game.
"""
import json
from typing import List, Dict, Any, Optional

from models.map import Map
from models.move import Move


class GameState:
    """
    GameState class representing the current state of the game.
    """

    def __init__(self, radius: int, moves_left: int):
        """
        Initialize a new game state.
        """
        self.started = False
        self.turn = 0
        self.map = Map(radius=radius)
        self.players = []
        self.moves_left = moves_left
        self.treasure_appeared = False
        self.treasure_remaining = False

    def update(self, moves: List[Optional[Move]]):
        """
        Update the game state based on the provided moves.

        Args:
            moves: List of moves for each player
        """
        self.turn += 1
        for i, player in enumerate(self.players):
            if player.alive and moves[i]:
                direction = moves[i].direction
                if direction:
                    player.move(direction, self.map)

    def to_json(self) -> str:
        """
        Convert the game state to a JSON string.

        Returns:
            JSON string representation of the game state
        """
        state_dict = self.to_dict()
        return json.dumps(state_dict, indent=2)

    # def from_json(self, json_str: str) -> 'GameState':
    #     """
    #     Load the game state from a JSON string.
    #
    #     Args:
    #         json_str: JSON string representation of the game state
    #
    #     Returns:
    #         The updated game state
    #     """
    #     state_dict = json.loads(json_str)
    #     return self.from_dict(state_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the game state to a dictionary.

        Returns:
            Dictionary representation of the game state
        """
        return {
            "players": [
                {
                    "q": player.position.q if player.position else 0,
                    "r": player.position.r if player.position else 0,
                    "s": player.position.s if player.position else 0,
                    "points": player.gold,
                    "shield": player.shield,
                    "alive": player.alive,
                    "missiles": player.missiles,
                    "missiles_fired": [
                        {"q": target.q, "r": target.r, "s": target.s}
                        for target in player.missiles_fired
                    ]
                }
                for i, player in enumerate(self.players)
            ],
            "map": {
                "moveleft": self.moves_left,
                "radius": self.map.radius,
                "treasure_remaining": self.treasure_remaining,
                "cells": self.map.to_dict_list()
            }
        }
