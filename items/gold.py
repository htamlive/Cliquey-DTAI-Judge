#!/usr/bin/env python3
"""
Gold item module for the "botwar ship" game.
"""
from items.item import Item
from utils.constants import MIN_GOLD_VALUE, MAX_GOLD_VALUE


class Gold(Item):
    """
    Gold item that can be collected by players.
    """

    def __init__(self, value: int):
        """
        Initialize a gold item with the specified value.
        
        Args:
            value: Value of the gold
        """
        self.value = value

    def apply_effect(self, player, map_obj):
        """
        Apply the gold's effect when a player moves onto it.
        
        Args:
            player: The player who moved onto the gold
            map_obj: The current map state
        """
        if player.alive:
            player.collect_gold(self.value)
        return None
