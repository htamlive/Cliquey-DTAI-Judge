#!/usr/bin/env python3
"""
Danger item module for the "botwar ship" game.
"""
from items.item import Item


class Danger(Item):
    """
    Danger item that causes ships to sink if they don't have a shield.
    """

    def apply_effect(self, player, map_obj):
        """
        Apply the danger's effect when a player moves onto it.
        
        Args:
            player: The player who moved onto the danger
            map_obj: The current map state
        """
        if player.alive:
            if not player.shield:
                # Player hit danger without a shield, ship sinks
                player.alive = False
        return self
