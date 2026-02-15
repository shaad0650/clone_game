"""
utils.py — Geometry helpers for Mirror Clone Survival.
"""

import math


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Return the Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def check_collision(player, clone) -> bool:
    """Return True if the player and clone circles overlap."""
    dist = calculate_distance(player.x, player.y, clone.x, clone.y)
    return dist < (player.radius + clone.radius)
