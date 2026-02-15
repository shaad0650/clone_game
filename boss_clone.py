"""
boss_clone.py — Boss clone enemy for Mirror Clone Survival.
"""

import pygame

from clone import Clone
from config import (
    BOSS_CLONE_HP,
    BOSS_CLONE_SIZE_MULTIPLIER,
    BOSS_CLONE_SPEED_MULT,
    BOSS_COLOR,
    BOSS_GLOW_COLOR,
    CLONE_RADIUS,
    TRAIL_LENGTH,
    TRAIL_SPACING,
)
from history import HistoryManager


class BossClone(Clone):
    """Large, fast, multi-hit boss that replays player history."""

    def __init__(self, history_manager: HistoryManager, start_frame: int) -> None:
        super().__init__(
            history_manager, start_frame,
            clone_type="normal", mutation_type="normal",
        )
        self.radius = int(CLONE_RADIUS * BOSS_CLONE_SIZE_MULTIPLIER)
        self.hp: int = BOSS_CLONE_HP
        self.color = BOSS_COLOR
        self.glow_color = BOSS_GLOW_COLOR
        self.is_boss: bool = True
        self._replay_speed = BOSS_CLONE_SPEED_MULT  # 1.5×

        # Accumulator for fractional replay speed
        self._step_acc: float = 0.0

    # ── Update ──────────────────────────────────────────────────────────
    def update(self) -> None:
        if not self.alive:
            return

        self.shoot_requested = False

        # Fractional speed: accumulate and step whole frames
        self._step_acc += self._replay_speed
        steps = int(self._step_acc)
        self._step_acc -= steps

        for _ in range(steps):
            fd = self.history_manager.get_frame_data(self.current_frame)
            if fd is not None:
                self.x, self.y = fd.x, fd.y
                if fd.shoot:
                    self.shoot_requested = True
                    self.shoot_dir_x = fd.dir_x
                    self.shoot_dir_y = fd.dir_y
                    self.shoot_weapon_id = fd.weapon_id
                self.current_frame += 1
            else:
                break

    # ── Take hit (requires multiple hits to kill) ───────────────────────
    def take_hit(self) -> bool:
        """Reduce HP. Returns True when boss dies."""
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    # ── Render ──────────────────────────────────────────────────────────
    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return

        # Trail
        for i in range(1, TRAIL_LENGTH + 1):
            trail_frame = self.current_frame - i * TRAIL_SPACING
            tpos = self.history_manager.get_position(trail_frame)
            if tpos is not None:
                alpha = max(20, 150 - i * 10)
                r = max(3, self.radius - i * 2)
                surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*self.color, alpha), (r, r), r)
                screen.blit(surf, (int(tpos[0]) - r, int(tpos[1]) - r))

        pos = (int(self.x), int(self.y))

        # Glow
        gr = self.radius + 10
        glow_surf = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color, 50), (gr, gr), gr)
        screen.blit(glow_surf, (pos[0] - gr, pos[1] - gr))

        # Core
        pygame.draw.circle(screen, self.color, pos, self.radius)

        # HP bar
        bar_w = self.radius * 2
        bar_h = 4
        bx = pos[0] - bar_w // 2
        by = pos[1] - self.radius - 8
        pygame.draw.rect(screen, (60, 60, 60), (bx, by, bar_w, bar_h))
        fill = int(bar_w * (self.hp / BOSS_CLONE_HP))
        pygame.draw.rect(screen, BOSS_GLOW_COLOR, (bx, by, fill, bar_h))

        # BOSS label
        font = pygame.font.SysFont("consolas", 12, bold=True)
        txt = font.render("BOSS", True, (255, 255, 255))
        screen.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2))
