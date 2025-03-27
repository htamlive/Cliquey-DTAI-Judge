#!/usr/bin/env python3
"""
Item base class module for the "botwar ship" game.
"""
from abc import ABC, abstractmethod


class Item(ABC):
    """
    Abstract base class for all items in the game.
    """

    @abstractmethod
    def apply_effect(self, player, map_obj) -> 'Item':
        """
        Apply the item's effect when a player moves onto it.
        
        Args:
            player: The player who moved onto the item
            map_obj: The current map state
        """
        return self
