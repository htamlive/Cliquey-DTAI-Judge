#!/usr/bin/env python3
"""
Move module for the "botwar ship" game.
"""
from typing import List, Optional

from models.direction import Direction
from models.coordinate import Coordinate


class Move:
    """
    Move class representing a player's move in the game.
    """

    def __init__(self, direction: Optional[Direction] = Direction.O, missile_targets: List[Coordinate] = None):
        """
        Initialize a move with direction and missile targets.
        
        Args:
            direction: Direction to move in, or None for no movement
            missile_targets: List of coordinates to fire missiles at
        """
        self.direction = direction
        self.missile_targets = missile_targets or []

    def validate(self, player, map_obj) -> bool:
        """
        Validate that this move is legal for the given player and map.
        
        Args:
            player: Player making the move
            map_obj: Current map state
            
        Returns:
            True if the move is valid, False otherwise
        """
        # Can't move if player is not alive
        if not player.alive:
            return False

        # Validate direction
        if self.direction is not None:
            # Calculate the new position after moving
            new_position = player.position.next(self.direction)

            # Check if the new position is within the map boundaries
            if new_position and not map_obj.is_valid_coordinate(new_position):
                return False

        # Validate missile targets
        if len(self.missile_targets) > player.missiles:
            return False

        for target in self.missile_targets:
            # Check if the target is valid
            if not target.validate() or not map_obj.is_valid_coordinate(target):
                return False

            # Check that the target is not the same as the player's position after moving
            if self.direction is not None:
                new_position = player.position.next(self.direction)
                if new_position and target == new_position:
                    return False

        return True
