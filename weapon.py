"""
weapon.py — Weapon definitions for Mirror Clone Survival.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from config import WEAPON_DEFS


@dataclass(frozen=True)
class Weapon:
    """Immutable weapon definition."""
    id: int
    name: str
    fire_rate: int        # frames between shots
    bullet_speed: float
    bullet_count: int     # 1 for single, 3+ for spread
    spread: float         # total spread angle in degrees (0 = straight)
    unlock_level: int

    def get_fire_directions(
        self, base_dx: float, base_dy: float
    ) -> list[tuple[float, float]]:
        """Return a list of normalised (dx, dy) pairs for each bullet.

        For bullet_count == 1, returns the base direction.
        For bullet_count > 1, fans them evenly across ``spread`` degrees.
        """
        if self.bullet_count <= 1 or self.spread == 0:
            return [(base_dx, base_dy)]

        base_angle = math.atan2(base_dy, base_dx)
        half = math.radians(self.spread) / 2
        step = math.radians(self.spread) / (self.bullet_count - 1)

        dirs: list[tuple[float, float]] = []
        for i in range(self.bullet_count):
            a = base_angle - half + step * i
            dirs.append((math.cos(a), math.sin(a)))
        return dirs


# Build registry from config
ALL_WEAPONS: list[Weapon] = [
    Weapon(
        id=d["id"],
        name=d["name"],
        fire_rate=d["fire_rate"],
        bullet_speed=d["bullet_speed"],
        bullet_count=d["bullet_count"],
        spread=d["spread"],
        unlock_level=d["unlock_level"],
    )
    for d in WEAPON_DEFS
]

WEAPON_BY_ID: dict[int, Weapon] = {w.id: w for w in ALL_WEAPONS}
