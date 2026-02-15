"""
bullet_manager.py — Manages all bullets for Mirror Clone Survival.
"""

import math

import pygame

from bullet import Bullet
from config import BULLET_RADIUS, BULLET_SPEED, MAX_BULLETS
from utils import calculate_distance


class BulletManager:
    """Central store for every bullet in the game."""

    def __init__(self) -> None:
        self.bullets: list[Bullet] = []

    # ── Spawning ────────────────────────────────────────────────────────
    def spawn_bullet(
        self,
        x: float,
        y: float,
        direction_x: float,
        direction_y: float,
        owner_type: str,
        color: tuple[int, int, int],
        bullet_speed: float | None = None,
        current_frame: int = 0,
    ) -> None:
        if len(self.bullets) >= MAX_BULLETS:
            return

        speed = bullet_speed if bullet_speed is not None else BULLET_SPEED
        length = math.hypot(direction_x, direction_y)
        if length == 0:
            return
        vx = direction_x / length * speed
        vy = direction_y / length * speed

        self.bullets.append(
            Bullet(x, y, vx, vy, owner_type, color, spawn_frame=current_frame)
        )

    # ── Update ──────────────────────────────────────────────────────────
    def update(self, current_frame: int = 0) -> None:
        for b in self.bullets:
            b.update(current_frame)
        self.bullets = [b for b in self.bullets if b.alive]

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        for b in self.bullets:
            b.draw(screen)

    # ── Collision checks ────────────────────────────────────────────────
    def check_collisions(self, player, clones: list) -> dict:
        result: dict = {"player_hit": False, "clones_hit": []}

        for b in self.bullets:
            if not b.alive:
                continue

            if b.owner_type == "clone":
                dist = calculate_distance(b.x, b.y, player.x, player.y)
                if dist < (b.radius + player.radius):
                    if player.shield_active:
                        b.destroy()
                    else:
                        result["player_hit"] = True
                        b.destroy()
                    continue

            if b.owner_type == "player":
                for idx, clone in enumerate(clones):
                    if not clone.alive:
                        continue
                    dist = calculate_distance(b.x, b.y, clone.x, clone.y)
                    if dist < (b.radius + clone.radius):
                        clone.alive = False
                        b.destroy()
                        result["clones_hit"].append(idx)
                        break

        return result

    # ── Reset ───────────────────────────────────────────────────────────
    def reset(self) -> None:
        self.bullets.clear()
