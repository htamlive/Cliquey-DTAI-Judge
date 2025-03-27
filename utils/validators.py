#!/usr/bin/env python3
"""
Validators module for the "botwar ship" game.
"""


def validate_coordinate(q: int, r: int, s: int) -> bool:
    """
    Validate that a coordinate satisfies q + r + s = 0.
    
    Args:
        q: q-coordinate
        r: r-coordinate
        s: s-coordinate
        
    Returns:
        True if the coordinate is valid, False otherwise
    """
    return q + r + s == 0


def validate_coordinate_bounds(q: int, r: int, s: int, radius: int) -> bool:
    """
    Validate that a coordinate is within the map bounds.
    
    Args:
        q: q-coordinate
        r: r-coordinate
        s: s-coordinate
        radius: Maximum coordinate absolute value
        
    Returns:
        True if the coordinate is within bounds, False otherwise
    """
    return max(abs(q), abs(r), abs(s)) <= radius


def validate_team_constraints(team_id: int, q: int, r: int, s: int) -> bool:
    """
    Validate that a coordinate satisfies the team-specific constraints.

    Args:
        team_id: Team ID (1-3)
        q: q-coordinate
        r: r-coordinate
        s: s-coordinate

    Returns:
        True if the coordinate satisfies the constraints, False otherwise
    """
    if team_id == 1:
        return q > 0 > r
    elif team_id == 2:
        return r > 0 > s
    elif team_id == 3:
        return s > 0 > q
    else:
        return False
