#!/usr/bin/env python3
"""
Direction module for the "botwar ship" game.
"""
from enum import Enum, auto


class Direction(Enum):
    """
    Direction enum representing the six possible movement directions in a hexagonal grid.
    """
    O = auto()  # Origin: (0, 0, 0)
    E = auto()  # East: (1, -1, 0)
    NE = auto()  # Northeast: (1, 0, -1)
    NW = auto()  # Northwest: (0, 1, -1)
    W = auto()  # West: (-1, 1, 0)
    SW = auto()  # Southwest: (-1, 0, 1)
    SE = auto()  # Southeast: (0, -1, 1)

    @staticmethod
    def all():
        """
        Get a list of all directions.

        Returns:
            List of all directions
        """
        return [Direction.O, Direction.E, Direction.NE, Direction.NW, Direction.W, Direction.SW, Direction.SE]

    @staticmethod
    def all_non_origin():
        """
        Get a list of all directions except the origin.

        Returns:
            List of all directions except the origin
        """
        return [Direction.E, Direction.NE, Direction.NW, Direction.W, Direction.SW, Direction.SE]

    def to_coordinate(self):
        """
        Convert the direction to a coordinate offset.

        Returns:
            Tuple of (q, r, s) coordinate offset
        """
        direction_to_coordinate = {
            Direction.O: (0, 0, 0),
            Direction.E: (1, -1, 0),
            Direction.NE: (1, 0, -1),
            Direction.NW: (0, 1, -1),
            Direction.W: (-1, 1, 0),
            Direction.SW: (-1, 0, 1),
            Direction.SE: (0, -1, 1),
        }
        return direction_to_coordinate[self]
