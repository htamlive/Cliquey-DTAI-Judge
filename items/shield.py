#!/usr/bin/env python3
"""
Shield item module for the "botwar ship" game.
"""
from items.item import Item


class Shield(Item):
    """
    Shield item that provides protection from danger cells.
    """

    def apply_effect(self, player, map_obj):
        """
        Apply the shield's effect when a player moves onto it.
        
        Args:
            player: The player who moved onto the shield
            map_obj: The current map state
        """
        if player.alive:
            player.equip_shield()
        return None
