"""
instruction_screen.py — Professional instruction screen for Mirror Clone Survival.
"""

import math

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH


class InstructionScreen:
    """Renders a full-screen instruction overlay before gameplay begins."""

    def __init__(self) -> None:
        self.font_title = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_section = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 17)
        self.font_hint = pygame.font.SysFont("consolas", 20, bold=True)
        self._pulse: float = 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True when SPACE is pressed to start."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        self._pulse += 0.05
        screen.fill((12, 12, 18))

        cx = WINDOW_WIDTH // 2
        y = 40

        # ── Title ───────────────────────────────────────────────────────
        title = self.font_title.render("MIRROR CLONE SURVIVAL", True, (80, 200, 255))
        screen.blit(title, (cx - title.get_width() // 2, y))
        y += 60

        # Subtitle
        sub = self.font_body.render(
            "Your past actions become future enemies.", True, (160, 160, 180)
        )
        screen.blit(sub, (cx - sub.get_width() // 2, y))
        y += 45

        # ── Controls ────────────────────────────────────────────────────
        controls_title = self.font_section.render("— CONTROLS —", True, (255, 220, 80))
        screen.blit(controls_title, (cx - controls_title.get_width() // 2, y))
        y += 32

        controls = [
            ("WASD / Arrows", "Move"),
            ("Mouse Click", "Shoot toward cursor"),
            ("SPACE", "Shoot in facing direction"),
            ("SHIFT", "Dash (invulnerable)"),
            ("E", "Spawn Time Echo Clone (costs energy)"),
            ("R", "Restart (game over)"),
            ("P", "Watch Replay (game over)"),
        ]
        for key, desc in controls:
            line = self.font_body.render(f"{key:>16}   {desc}", True, (200, 200, 210))
            screen.blit(line, (cx - line.get_width() // 2, y))
            y += 23
        y += 15

        # ── Objective ───────────────────────────────────────────────────
        obj_title = self.font_section.render("— OBJECTIVE —", True, (255, 220, 80))
        screen.blit(obj_title, (cx - obj_title.get_width() // 2, y))
        y += 30

        objectives = [
            "Survive as long as possible.",
            "Avoid clones, bullets, and hazards.",
            "Every 5 seconds a clone replays your past.",
            "Level up to unlock new weapons.",
        ]
        for line in objectives:
            surf = self.font_body.render(line, True, (180, 180, 195))
            screen.blit(surf, (cx - surf.get_width() // 2, y))
            y += 22
        y += 15

        # ── Tip ─────────────────────────────────────────────────────────
        tip_title = self.font_section.render("— TIP —", True, (100, 255, 200))
        screen.blit(tip_title, (cx - tip_title.get_width() // 2, y))
        y += 28
        tip = self.font_body.render(
            "Use Time Echo strategically to create allies", True, (100, 255, 200)
        )
        screen.blit(tip, (cx - tip.get_width() // 2, y))
        y += 22
        tip2 = self.font_body.render(
            "from your past timeline.", True, (100, 255, 200)
        )
        screen.blit(tip2, (cx - tip2.get_width() // 2, y))

        # ── Start prompt (pulsing) ──────────────────────────────────────
        alpha = int(140 + 115 * math.sin(self._pulse))
        prompt = self.font_hint.render("Press  SPACE  to Start", True, (80, 200, 255))
        prompt_surf = pygame.Surface(
            (prompt.get_width(), prompt.get_height()), pygame.SRCALPHA
        )
        prompt_surf.blit(prompt, (0, 0))
        prompt_surf.set_alpha(alpha)
        screen.blit(prompt_surf, (cx - prompt.get_width() // 2, WINDOW_HEIGHT - 55))
