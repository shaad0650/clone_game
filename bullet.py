"""
bullet.py — Persistent projectile entity for Mirror Clone Survival.
"""

import pygame

from config import (
    BULLET_LIFETIME_FRAMES,
    BULLET_RADIUS,
    BULLET_TRAIL_LENGTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class Bullet:
    """A projectile that bounces off walls and persists for a set lifetime."""

    __slots__ = (
        "x", "y", "vx", "vy", "radius", "alive",
        "owner_type", "color", "trail",
        "spawn_frame", "lifetime",
    )

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        owner_type: str,
        color: tuple[int, int, int],
        spawn_frame: int = 0,
        lifetime: int = BULLET_LIFETIME_FRAMES,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius: int = BULLET_RADIUS
        self.alive: bool = True
        self.owner_type = owner_type   # "player" or "clone"
        self.color = color
        self.trail: list[tuple[float, float]] = []
        self.spawn_frame = spawn_frame
        self.lifetime = lifetime

    # ── Update ──────────────────────────────────────────────────────────
    def update(self, current_frame: int) -> None:
        if not self.alive:
            return

        # Lifetime expiry
        if current_frame - self.spawn_frame >= self.lifetime:
            self.destroy()
            return

        # Record trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > BULLET_TRAIL_LENGTH:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius >= WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
            self.vx = -abs(self.vx)

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius
            self.vy = -abs(self.vy)

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(40 + 40 * (i / max(1, len(self.trail))))
            r = max(1, self.radius - (BULLET_TRAIL_LENGTH - i))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (r, r), r)
            screen.blit(surf, (int(tx) - r, int(ty) - r))

        pygame.draw.circle(
            screen, self.color, (int(self.x), int(self.y)), self.radius
        )

    # ── Destroy ─────────────────────────────────────────────────────────
    def destroy(self) -> None:
        self.alive = False
