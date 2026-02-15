"""
powerup.py — Powerup entity for Mirror Clone Survival.
"""

import math
import random

import pygame

from config import POWERUP_RADIUS, POWERUP_TYPES, WINDOW_HEIGHT, WINDOW_WIDTH


class Powerup:
    """A collectible powerup that floats in the arena."""

    def __init__(self, powerup_type: str | None = None) -> None:
        if powerup_type is None:
            powerup_type = random.choice(list(POWERUP_TYPES.keys()))
        self.type: str = powerup_type
        self.radius: int = POWERUP_RADIUS
        self.alive: bool = True

        info = POWERUP_TYPES[self.type]
        self.duration: int = info["duration"]
        self.color: tuple[int, int, int] = info["color"]

        # Random position (away from edges)
        margin = 40
        self.x: float = random.uniform(margin, WINDOW_WIDTH - margin)
        self.y: float = random.uniform(margin, WINDOW_HEIGHT - margin)

        self._pulse_phase: float = random.uniform(0, math.tau)

    # ── Update ──────────────────────────────────────────────────────────
    def update(self) -> None:
        self._pulse_phase += 0.08

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)
        glow_r = int(self.radius * 2 + 6 * pulse)

        # Outer glow
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        alpha = int(40 + 30 * pulse)
        pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_r, glow_r), glow_r)
        screen.blit(glow_surf, (int(self.x) - glow_r, int(self.y) - glow_r))

        # Core
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Type indicator letter
        font = pygame.font.SysFont("consolas", 12, bold=True)
        letter = self.type[0].upper()
        txt = font.render(letter, True, (20, 20, 20))
        screen.blit(txt, (int(self.x) - txt.get_width() // 2,
                          int(self.y) - txt.get_height() // 2))
