#!/usr/bin/env python3
"""
Treasure item module for the "botwar ship" game.
"""
from items.item import Item


class Treasure(Item):
    """
    Treasure item with a special high value that appears at the center.
    """

    def __init__(self, value: int):
        """
        Initialize a treasure item with the specified value.
        
        Args:
            value: Value of the treasure
        """
        self.value = value

    def apply_effect(self, player, map_obj):
        """
        Apply the treasure's effect when a player moves onto it.
        
        Args:
            player: The player who moved onto the treasure
            map_obj: The current map state
        """
        if player.alive:
            player.collect_gold(self.value)
        return None
