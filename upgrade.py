"""
upgrade.py — Upgrade choice system for Mirror Clone Survival.
"""

import random

import pygame

from config import (
    UPGRADE_BG_COLOR,
    UPGRADE_CHOICES_COUNT,
    UPGRADE_DEFS,
    UPGRADE_HL_COLOR,
    UPGRADE_INTERVAL_FRAMES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class UpgradeManager:
    """Periodically offers the player a choice of upgrades."""

    def __init__(self) -> None:
        self._timer: int = 0
        self.paused: bool = False
        self.choices: list[str] = []
        self.selected: int = 0    # current hover / keyboard index
        self.applied: dict[str, int] = {}  # upgrade_key → count applied

    # ── Tick ─────────────────────────────────────────────────────────────

    def tick(self) -> bool:
        """Call every frame. Returns True if game should pause for selection."""
        if self.paused:
            return True
        self._timer += 1
        if self._timer >= UPGRADE_INTERVAL_FRAMES:
            self._timer = 0
            self._generate_choices()
            self.paused = True
            return True
        return False

    # ── Input ────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Process key/mouse during upgrade selection.

        Returns the selected upgrade key, or None.
        """
        if not self.paused:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(self.choices) >= 1:
                return self._pick(0)
            if event.key == pygame.K_2 and len(self.choices) >= 2:
                return self._pick(1)
            if event.key == pygame.K_3 and len(self.choices) >= 3:
                return self._pick(2)
            if event.key == pygame.K_UP:
                self.selected = max(0, self.selected - 1)
            if event.key == pygame.K_DOWN:
                self.selected = min(len(self.choices) - 1, self.selected + 1)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._pick(self.selected)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check which card was clicked
            for i in range(len(self.choices)):
                rect = self._card_rect(i)
                if rect.collidepoint(event.pos):
                    return self._pick(i)

        return None

    # ── Apply ────────────────────────────────────────────────────────────

    def apply(self, key: str, game) -> None:
        """Apply the upgrade to the live game state."""
        info = UPGRADE_DEFS.get(key)
        if info is None:
            return
        val = info["value"]
        self.applied[key] = self.applied.get(key, 0) + 1

        if key == "movement_speed_boost":
            game.player.speed += val
        elif key == "bullet_speed_boost":
            pass  # handled via progression bonus additive
        elif key == "dash_cooldown_reduction":
            from config import DASH_COOLDOWN_FRAMES
            current = getattr(game, "_upgrade_dash_cd", DASH_COOLDOWN_FRAMES)
            game._upgrade_dash_cd = max(30, int(current * (1 - val)))
        elif key == "clone_spawn_delay":
            game.spawn_interval += val

    # ── Draw ─────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        if not self.paused:
            return

        # Dim overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        font_title = pygame.font.SysFont("consolas", 32, bold=True)
        font_card = pygame.font.SysFont("consolas", 22)
        font_hint = pygame.font.SysFont("consolas", 16)

        title = font_title.render("CHOOSE UPGRADE", True, UPGRADE_HL_COLOR)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))

        for i, key in enumerate(self.choices):
            info = UPGRADE_DEFS[key]
            rect = self._card_rect(i)
            is_sel = (i == self.selected)

            # Card background
            color = UPGRADE_HL_COLOR if is_sel else UPGRADE_BG_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, (140, 140, 160) if is_sel else (60, 60, 70), rect, 2, border_radius=8)

            # Label
            txt_color = (20, 20, 30) if is_sel else (220, 220, 220)
            label = font_card.render(f"[{i+1}] {info['label']}", True, txt_color)
            screen.blit(label, (rect.x + 20, rect.y + rect.h // 2 - label.get_height() // 2))

        hint = font_hint.render("Press 1/2/3 or click to select", True, (160, 160, 170))
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 400))

    # ── Internals ────────────────────────────────────────────────────────

    def _generate_choices(self) -> None:
        keys = list(UPGRADE_DEFS.keys())
        self.choices = random.sample(keys, min(UPGRADE_CHOICES_COUNT, len(keys)))
        self.selected = 0

    def _pick(self, idx: int) -> str:
        key = self.choices[idx]
        self.paused = False
        self.choices.clear()
        return key

    def _card_rect(self, idx: int) -> pygame.Rect:
        card_w = 360
        card_h = 50
        gap = 16
        total_h = len(self.choices) * card_h + (len(self.choices) - 1) * gap
        start_y = 180
        x = WINDOW_WIDTH // 2 - card_w // 2
        y = start_y + idx * (card_h + gap)
        return pygame.Rect(x, y, card_w, card_h)

    def reset(self) -> None:
        self._timer = 0
        self.paused = False
        self.choices.clear()
        self.selected = 0
        self.applied.clear()
