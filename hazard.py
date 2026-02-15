"""
hazard.py — Environmental hazards for Mirror Clone Survival.
"""

import math
import random

import pygame

from config import (
    HAZARD_LASER_COLOR,
    HAZARD_LASER_SPEED,
    HAZARD_LIFETIME_FRAMES,
    HAZARD_MAX_ACTIVE,
    HAZARD_SPAWN_MAX_FRAMES,
    HAZARD_SPAWN_MIN_FRAMES,
    HAZARD_WALL_COLOR,
    HAZARD_WALL_SPEED,
    HAZARD_ZONE_COLOR,
    HAZARD_ZONE_RADIUS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from utils import calculate_distance


# ── Hazard base ─────────────────────────────────────────────────────────────

class Hazard:
    """Base class for arena hazards."""

    def __init__(self, hazard_type: str) -> None:
        self.hazard_type = hazard_type
        self.alive: bool = True
        self.life: int = HAZARD_LIFETIME_FRAMES

    def update(self) -> None:
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def hits_entity(self, ex: float, ey: float, er: int) -> bool:
        return False

    def draw(self, screen: pygame.Surface) -> None:
        pass


# ── Moving wall ─────────────────────────────────────────────────────────────

class MovingWall(Hazard):
    """Horizontal bar that sweeps across the screen."""

    def __init__(self) -> None:
        super().__init__("moving_wall")
        self.thickness = 8
        # Start from a random edge
        self.horizontal = random.choice([True, False])
        if self.horizontal:
            self.pos: float = 0.0
            self.speed = HAZARD_WALL_SPEED * random.choice([-1, 1])
        else:
            self.pos = 0.0
            self.speed = HAZARD_WALL_SPEED * random.choice([-1, 1])

    def update(self) -> None:
        super().update()
        self.pos += self.speed
        limit = WINDOW_WIDTH if not self.horizontal else WINDOW_HEIGHT
        if self.pos < 0 or self.pos > limit:
            self.speed = -self.speed

    def hits_entity(self, ex: float, ey: float, er: int) -> bool:
        if self.horizontal:
            return abs(ey - self.pos) < (self.thickness / 2 + er)
        else:
            return abs(ex - self.pos) < (self.thickness / 2 + er)

    def draw(self, screen: pygame.Surface) -> None:
        alpha = min(200, int(200 * (self.life / HAZARD_LIFETIME_FRAMES)))
        if self.horizontal:
            surf = pygame.Surface((WINDOW_WIDTH, self.thickness), pygame.SRCALPHA)
            surf.fill((*HAZARD_WALL_COLOR, alpha))
            screen.blit(surf, (0, int(self.pos) - self.thickness // 2))
        else:
            surf = pygame.Surface((self.thickness, WINDOW_HEIGHT), pygame.SRCALPHA)
            surf.fill((*HAZARD_WALL_COLOR, alpha))
            screen.blit(surf, (int(self.pos) - self.thickness // 2, 0))


# ── Rotating laser ──────────────────────────────────────────────────────────

class RotatingLaser(Hazard):
    """Line that rotates around a fixed point."""

    def __init__(self) -> None:
        super().__init__("rotating_laser")
        self.cx = random.uniform(150, WINDOW_WIDTH - 150)
        self.cy = random.uniform(150, WINDOW_HEIGHT - 150)
        self.angle: float = random.uniform(0, math.tau)
        self.length = 200
        self.width = 3

    def update(self) -> None:
        super().update()
        self.angle += HAZARD_LASER_SPEED

    def hits_entity(self, ex: float, ey: float, er: int) -> bool:
        # Point-to-segment distance
        dx = math.cos(self.angle) * self.length
        dy = math.sin(self.angle) * self.length
        x1, y1 = self.cx, self.cy
        x2, y2 = self.cx + dx, self.cy + dy

        # Project point onto line
        lsq = dx * dx + dy * dy
        if lsq == 0:
            return False
        t = max(0, min(1, ((ex - x1) * dx + (ey - y1) * dy) / lsq))
        px = x1 + t * dx
        py = y1 + t * dy
        dist = math.hypot(ex - px, ey - py)
        return dist < (self.width + er)

    def draw(self, screen: pygame.Surface) -> None:
        alpha = min(200, int(200 * (self.life / HAZARD_LIFETIME_FRAMES)))
        dx = math.cos(self.angle) * self.length
        dy = math.sin(self.angle) * self.length
        end = (int(self.cx + dx), int(self.cy + dy))
        start = (int(self.cx), int(self.cy))

        # Glow
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(surf, (*HAZARD_LASER_COLOR, alpha), start, end, self.width + 4)
        screen.blit(surf, (0, 0))
        pygame.draw.line(screen, HAZARD_LASER_COLOR, start, end, self.width)

        # Center dot
        pygame.draw.circle(screen, HAZARD_LASER_COLOR, start, 5)


# ── Danger zone ─────────────────────────────────────────────────────────────

class DangerZone(Hazard):
    """Pulsing circular area of damage."""

    def __init__(self) -> None:
        super().__init__("danger_zone")
        margin = HAZARD_ZONE_RADIUS + 20
        self.cx = random.uniform(margin, WINDOW_WIDTH - margin)
        self.cy = random.uniform(margin, WINDOW_HEIGHT - margin)
        self.radius = HAZARD_ZONE_RADIUS
        self._pulse: float = 0.0

    def update(self) -> None:
        super().update()
        self._pulse += 0.1

    def hits_entity(self, ex: float, ey: float, er: int) -> bool:
        return calculate_distance(ex, ey, self.cx, self.cy) < (self.radius + er)

    def draw(self, screen: pygame.Surface) -> None:
        pulse = 0.6 + 0.4 * math.sin(self._pulse)
        alpha = int(80 * pulse * min(1.0, self.life / HAZARD_LIFETIME_FRAMES))
        r = int(self.radius + 5 * pulse)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*HAZARD_ZONE_COLOR, alpha), (r, r), r)
        screen.blit(surf, (int(self.cx) - r, int(self.cy) - r))
        pygame.draw.circle(screen, (*HAZARD_ZONE_COLOR, min(150, alpha + 40)),
                           (int(self.cx), int(self.cy)), self.radius, 2)


# ── Hazard Manager ──────────────────────────────────────────────────────────

_HAZARD_BUILDERS = [MovingWall, RotatingLaser, DangerZone]


class HazardManager:
    """Spawns and manages environmental hazards."""

    def __init__(self) -> None:
        self.hazards: list[Hazard] = []
        self._timer: int = 0
        self._next: int = self._interval()

    def update(self) -> None:
        self._timer += 1
        if self._timer >= self._next and len(self.hazards) < HAZARD_MAX_ACTIVE:
            cls = random.choice(_HAZARD_BUILDERS)
            self.hazards.append(cls())
            self._timer = 0
            self._next = self._interval()

        for h in self.hazards:
            h.update()
        self.hazards = [h for h in self.hazards if h.alive]

    def check_hits(self, ex: float, ey: float, er: int) -> bool:
        """Return True if any hazard hits the entity circle."""
        for h in self.hazards:
            if h.hits_entity(ex, ey, er):
                return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        for h in self.hazards:
            h.draw(screen)

    @staticmethod
    def _interval() -> int:
        return random.randint(HAZARD_SPAWN_MIN_FRAMES, HAZARD_SPAWN_MAX_FRAMES)

    def reset(self) -> None:
        self.hazards.clear()
        self._timer = 0
        self._next = self._interval()
