#!/usr/bin/env python3
"""
Constants module for the "botwar ship" game.
"""

# Game constants
MAX_MOVES = 100
TOTAL_GOLD = 300
MAX_MISSILES = 6
MAX_MISSILES_EACH_TURN = 2
MAP_RADIUS = 10

# Item values
MIN_GOLD_VALUE = 1
MAX_GOLD_VALUE = 6

# Missile effects
MISSILE_DAMAGE_ONE = 0.20  # 20% gold lost when hit by 1 missile
MISSILE_DAMAGE_TWO = 0.30  # 30% gold lost when hit by 2+ missiles

# Treasure appearance
TREASURE_MIN_THRESHOLD = 0.6  # K*0.6 where K is max moves
TREASURE_MAX_THRESHOLD = 0.7  # K*0.7
TREASURE_MIN_VALUE = 10
TREASURE_VALUE_DIVISOR = 12  # max(d/12, 10) where d is total gold collected

# Gold distribution
GOLD_DISTRIBUTION_RADIUS = 2  # Manhattan distance for distributing lost gold
TIMEOUT = 2  # Timeout for agent execution in seconds
