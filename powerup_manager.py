"""
powerup_manager.py — Manages powerup spawning, collection, and effects.
"""

import random

from config import (
    POWERUP_MAX_ACTIVE,
    POWERUP_SPAWN_MAX_FRAMES,
    POWERUP_SPAWN_MIN_FRAMES,
    POWERUP_TYPES,
)
from powerup import Powerup
from utils import calculate_distance


class PowerupManager:
    """Spawns powerups, handles collection, and tracks active effects."""

    def __init__(self) -> None:
        self.powerups: list[Powerup] = []
        self.active_effects: dict[str, int] = {}  # type → remaining frames

        self._spawn_timer: int = 0
        self._next_spawn: int = self._random_interval()

    # ── Update ──────────────────────────────────────────────────────────

    def update(self, player) -> list[str]:
        """Update spawn timer, powerups, and active effects.

        Returns list of newly-collected powerup types this frame.
        """
        collected: list[str] = []

        # Spawn timer
        self._spawn_timer += 1
        if self._spawn_timer >= self._next_spawn and len(self.powerups) < POWERUP_MAX_ACTIVE:
            self.powerups.append(Powerup())
            self._spawn_timer = 0
            self._next_spawn = self._random_interval()

        # Update visuals
        for p in self.powerups:
            p.update()

        # Check collection
        for p in self.powerups:
            if not p.alive:
                continue
            dist = calculate_distance(player.x, player.y, p.x, p.y)
            if dist < (player.radius + p.radius):
                p.alive = False
                self.active_effects[p.type] = POWERUP_TYPES[p.type]["duration"]
                collected.append(p.type)

        # Remove collected
        self.powerups = [p for p in self.powerups if p.alive]

        # Tick active effects
        expired = []
        for ptype in list(self.active_effects):
            self.active_effects[ptype] -= 1
            if self.active_effects[ptype] <= 0:
                expired.append(ptype)
        for ptype in expired:
            del self.active_effects[ptype]

        return collected

    # ── Queries ─────────────────────────────────────────────────────────

    def is_active(self, powerup_type: str) -> bool:
        return powerup_type in self.active_effects

    def draw(self, screen) -> None:
        for p in self.powerups:
            p.draw(screen)

    # ── Helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _random_interval() -> int:
        return random.randint(POWERUP_SPAWN_MIN_FRAMES, POWERUP_SPAWN_MAX_FRAMES)

    def reset(self) -> None:
        self.powerups.clear()
        self.active_effects.clear()
        self._spawn_timer = 0
        self._next_spawn = self._random_interval()
