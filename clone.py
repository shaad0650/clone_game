"""
clone.py — Enemy clone with variants + mutations that replays recorded player actions.
"""

import random

import pygame

from config import (
    BULLET_COLOR_CLONE,
    CLONE_COLORS,
    CLONE_DELAYED_DELAY,
    CLONE_DELAY_FRAMES,
    CLONE_FAST_SPEED_MULT,
    CLONE_GLOW_COLORS,
    CLONE_MUTATION_TYPES,
    CLONE_MUTATION_WEIGHTS,
    CLONE_RADIUS,
    CLONE_VARIANT_WEIGHTS,
    ECHO_COLOR,
    ECHO_GLOW_COLOR,
    MUTATION_COLORS,
    TRAIL_COLOR,
    TRAIL_LENGTH,
    TRAIL_SPACING,
    UNSTABLE_JITTER,
    WINDOW_WIDTH,
)
from history import HistoryManager


def pick_variant() -> str:
    types = list(CLONE_VARIANT_WEIGHTS.keys())
    weights = list(CLONE_VARIANT_WEIGHTS.values())
    return random.choices(types, weights, k=1)[0]


def pick_mutation() -> str:
    return random.choices(CLONE_MUTATION_TYPES, CLONE_MUTATION_WEIGHTS, k=1)[0]


class Clone:
    """Replays player history with variant behaviour and mutation modifiers."""

    def __init__(
        self,
        history_manager: HistoryManager,
        start_frame: int,
        clone_type: str | None = None,
        mutation_type: str | None = None,
        is_echo: bool = False,
    ) -> None:
        self.history_manager = history_manager
        self.start_frame = start_frame
        self.current_frame = start_frame
        self.radius: int = CLONE_RADIUS
        self.alive: bool = True
        self.is_echo: bool = is_echo

        # Variant (normal/fast/delayed/shooter)
        self.clone_type: str = clone_type or pick_variant()
        self.color = CLONE_COLORS.get(self.clone_type, CLONE_COLORS["normal"])
        self.glow_color = CLONE_GLOW_COLORS.get(self.clone_type, CLONE_GLOW_COLORS["normal"])

        # Echo override — cyan visuals
        if self.is_echo:
            self.color = ECHO_COLOR
            self.glow_color = ECHO_GLOW_COLOR


        # Mutation (normal/fast/mirror/unstable)
        self.mutation_type: str = mutation_type or pick_mutation()
        self.mutation_color = MUTATION_COLORS.get(self.mutation_type, MUTATION_COLORS["normal"])

        # Shooting replay
        self.shoot_requested: bool = False
        self.shoot_dir_x: float = 0.0
        self.shoot_dir_y: float = 0.0
        self.shoot_weapon_id: int = 0
        self.bullet_color: tuple[int, int, int] = BULLET_COLOR_CLONE

        # Bootstrap position
        pos = history_manager.get_position(start_frame)
        if pos is not None:
            self.x, self.y = pos
        else:
            self.x, self.y = 400.0, 300.0

    # ── Update ──────────────────────────────────────────────────────────
    def update(self) -> None:
        if not self.alive:
            return

        self.shoot_requested = False

        # Steps per tick — fast variant or fast mutation
        steps = 1
        if self.clone_type == "fast":
            steps = CLONE_FAST_SPEED_MULT
        elif self.mutation_type == "fast":
            steps = 2

        for _ in range(steps):
            fd = self.history_manager.get_frame_data(self.current_frame)
            if fd is not None:
                raw_x, raw_y = fd.x, fd.y

                # Apply mutation
                if self.mutation_type == "mirror":
                    raw_x = WINDOW_WIDTH - raw_x
                elif self.mutation_type == "unstable":
                    raw_x += random.uniform(-UNSTABLE_JITTER, UNSTABLE_JITTER)
                    raw_y += random.uniform(-UNSTABLE_JITTER, UNSTABLE_JITTER)

                self.x, self.y = raw_x, raw_y

                if fd.shoot:
                    self.shoot_requested = True
                    dx = fd.dir_x
                    if self.mutation_type == "mirror":
                        dx = -dx  # mirror shoot direction too
                    self.shoot_dir_x = dx
                    self.shoot_dir_y = fd.dir_y
                    self.shoot_weapon_id = fd.weapon_id

                self.current_frame += 1
            else:
                break

        # Shooter clone fires extra if no recorded shot
        if self.clone_type == "shooter" and not self.shoot_requested:
            if random.random() < 0.03:
                self.shoot_requested = True
                self.shoot_dir_x = 1.0
                self.shoot_dir_y = 0.0
                self.shoot_weapon_id = 0

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        trail_color = self.color
        for i in range(1, TRAIL_LENGTH + 1):
            trail_frame = self.current_frame - i * TRAIL_SPACING
            trail_pos = self.history_manager.get_position(trail_frame)
            if trail_pos is not None:
                tx, ty = trail_pos
                if self.mutation_type == "mirror":
                    tx = WINDOW_WIDTH - tx
                alpha = max(20, 150 - i * 12)
                trail_surf = pygame.Surface(
                    (self.radius * 2, self.radius * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    trail_surf, (*trail_color, alpha),
                    (self.radius, self.radius), max(2, self.radius - i),
                )
                screen.blit(
                    trail_surf,
                    (int(tx) - self.radius, int(ty) - self.radius),
                )

        pos = (int(self.x), int(self.y))

        # Glow
        glow_surf = pygame.Surface(
            (self.radius * 4, self.radius * 4), pygame.SRCALPHA
        )
        pygame.draw.circle(
            glow_surf, (*self.glow_color, 40),
            (self.radius * 2, self.radius * 2), self.radius * 2,
        )
        screen.blit(glow_surf, (pos[0] - self.radius * 2, pos[1] - self.radius * 2))

        # Core
        pygame.draw.circle(screen, self.color, pos, self.radius)

        # Mutation ring
        if self.mutation_type != "normal":
            ring_surf = pygame.Surface(
                (self.radius * 2 + 8, self.radius * 2 + 8), pygame.SRCALPHA
            )
            r = self.radius + 4
            pygame.draw.circle(ring_surf, (*self.mutation_color, 90), (r, r), r, 2)
            screen.blit(ring_surf, (pos[0] - r, pos[1] - r))

        # Type letter
        font = pygame.font.SysFont("consolas", 10, bold=True)
        letter = self.clone_type[0].upper()
        txt = font.render(letter, True, (255, 255, 255))
        screen.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2))
