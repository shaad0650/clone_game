"""
player.py — The player entity for Mirror Clone Survival.
"""

import math

import pygame

from config import (
    DASH_COOLDOWN_FRAMES,
    DASH_DURATION_FRAMES,
    DASH_SPEED,
    DASH_COLOR,
    ECHO_MAX_ENERGY,
    PLAYER_COLOR,
    PLAYER_GLOW_COLOR,
    PLAYER_RADIUS,
    PLAYER_SPEED,
    PLAYER_SPEED_CAP,
    SHIELD_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class Player:
    """Green circle controlled by the keyboard."""

    def __init__(self) -> None:
        self.x: float = WINDOW_WIDTH / 2
        self.y: float = WINDOW_HEIGHT / 2
        self.radius: int = PLAYER_RADIUS
        self.speed: float = PLAYER_SPEED
        self._dx: float = 0.0
        self._dy: float = 0.0

        # Shooting
        self.shoot_cooldown: int = 0
        self.shoot_requested: bool = False
        self.shoot_dir_x: float = 0.0
        self.shoot_dir_y: float = 0.0
        self.facing_x: float = 1.0
        self.facing_y: float = 0.0

        # Dash
        self.is_dashing: bool = False
        self.dash_timer: int = 0
        self.dash_cooldown_timer: int = 0
        self.dash_available: bool = True
        self._dash_dx: float = 0.0
        self._dash_dy: float = 0.0
        self._dash_trail: list[tuple[float, float]] = []

        # Powerup flags (set externally by Game)
        self.shield_active: bool = False

        # Echo energy
        self.echo_energy: float = ECHO_MAX_ENERGY

    # ── Input ───────────────────────────────────────────────────────────
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self._dx = 0.0
        self._dy = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._dx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._dy += 1.0

        length = (self._dx ** 2 + self._dy ** 2) ** 0.5
        effective_speed = min(self.speed, PLAYER_SPEED_CAP)
        if length > 0:
            self._dx = self._dx / length * effective_speed
            self._dy = self._dy / length * effective_speed
            self.facing_x = self._dx / effective_speed
            self.facing_y = self._dy / effective_speed

        # Dash input
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.start_dash()

    def handle_shoot_input(
        self,
        mouse_pos: tuple[int, int] | None = None,
        space_pressed: bool = False,
        fire_rate: int | None = None,
    ) -> None:
        self.shoot_requested = False
        cooldown = fire_rate if fire_rate is not None else 10

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return

        if mouse_pos is not None:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            length = math.hypot(dx, dy)
            if length > 0:
                self.shoot_dir_x = dx / length
                self.shoot_dir_y = dy / length
                self.shoot_requested = True
                self.shoot_cooldown = cooldown
        elif space_pressed:
            self.shoot_dir_x = self.facing_x
            self.shoot_dir_y = self.facing_y
            self.shoot_requested = True
            self.shoot_cooldown = cooldown

    # ── Dash ────────────────────────────────────────────────────────────
    def start_dash(self) -> None:
        if not self.dash_available or self.is_dashing:
            return
        length = math.hypot(self.facing_x, self.facing_y)
        if length == 0:
            return
        self.is_dashing = True
        self.dash_timer = DASH_DURATION_FRAMES
        self.dash_available = False
        self.dash_cooldown_timer = DASH_COOLDOWN_FRAMES
        self._dash_dx = self.facing_x / length * DASH_SPEED
        self._dash_dy = self.facing_y / length * DASH_SPEED

    def update_dash(self) -> None:
        if self.is_dashing:
            self.dash_timer -= 1
            self._dash_trail.append((self.x, self.y))
            if len(self._dash_trail) > 8:
                self._dash_trail.pop(0)
            if self.dash_timer <= 0:
                self.is_dashing = False
                self._dash_trail.clear()

        if not self.dash_available:
            self.dash_cooldown_timer -= 1
            if self.dash_cooldown_timer <= 0:
                self.dash_available = True

    # ── Update ──────────────────────────────────────────────────────────
    def update(self) -> None:
        self.update_dash()

        if self.is_dashing:
            self.x += self._dash_dx
            self.y += self._dash_dy
        else:
            self.x += self._dx
            self.y += self._dy

        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))

    # ── Query ───────────────────────────────────────────────────────────
    def get_position(self) -> tuple[float, float]:
        return self.x, self.y

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        pos = (int(self.x), int(self.y))

        # Dash trail
        for i, (tx, ty) in enumerate(self._dash_trail):
            alpha = int(40 + 20 * i)
            r = max(3, self.radius - (len(self._dash_trail) - i))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*DASH_COLOR, alpha), (r, r), r)
            screen.blit(surf, (int(tx) - r, int(ty) - r))

        # Shield ring
        if self.shield_active:
            shield_r = self.radius + 6
            shield_surf = pygame.Surface((shield_r * 2, shield_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*SHIELD_COLOR, 60), (shield_r, shield_r), shield_r)
            pygame.draw.circle(shield_surf, (*SHIELD_COLOR, 120), (shield_r, shield_r), shield_r, 2)
            screen.blit(shield_surf, (pos[0] - shield_r, pos[1] - shield_r))

        # Outer glow
        glow_color = DASH_COLOR if self.is_dashing else PLAYER_GLOW_COLOR
        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf, (*glow_color, 40),
            (self.radius * 2, self.radius * 2), self.radius * 2,
        )
        screen.blit(glow_surf, (pos[0] - self.radius * 2, pos[1] - self.radius * 2))

        # Core
        core_color = DASH_COLOR if self.is_dashing else PLAYER_COLOR
        pygame.draw.circle(screen, core_color, pos, self.radius)

    # ── Reset ───────────────────────────────────────────────────────────
    def reset(self) -> None:
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT / 2
        self.speed = PLAYER_SPEED
        self._dx = 0.0
        self._dy = 0.0
        self.shoot_cooldown = 0
        self.shoot_requested = False
        self.shoot_dir_x = 0.0
        self.shoot_dir_y = 0.0
        self.facing_x = 1.0
        self.facing_y = 0.0
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dash_available = True
        self._dash_trail.clear()
        self.shield_active = False
        self.echo_energy = ECHO_MAX_ENERGY
