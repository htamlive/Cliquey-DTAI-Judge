#!/usr/bin/env python3
"""
Cell module for the "botwar ship" game.
"""
from typing import Optional, Any


class Cell:
    """
    Cell class representing a single cell in the hexagonal grid.
    """

    def __init__(self):
        """
        Initialize an empty cell.
        """
        self.item = None

    def is_empty(self) -> bool:
        """
        Check if the cell is empty (contains no item).
        
        Returns:
            True if the cell is empty, False otherwise
        """
        return self.item is None

    def get_item(self) -> Optional[Any]:
        """
        Get the item in the cell.
        
        Returns:
            The item in the cell, or None if the cell is empty
        """
        return self.item

    def set_item(self, item: Any):
        """
        Set the item in the cell.
        
        Args:
            item: The item to set
        """
        self.item = item

    def clear_item(self):
        """
        Remove any item from the cell.
        """
        self.item = None
