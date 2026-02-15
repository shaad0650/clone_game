"""
renderer.py — Draws all visual elements for Mirror Clone Survival.
"""

import math
import random

import pygame

from config import (
    BACKGROUND_COLOR,
    CLONE_COLORS,
    DASH_COLOR,
    ECHO_BAR_BG,
    ECHO_BAR_COLOR,
    FONT_SIZE_GAME_OVER,
    FONT_SIZE_HUD,
    FONT_SIZE_SMALL,
    FONT_SIZE_SUB,
    GAME_OVER_COLOR,
    HUD_COLOR,
    LEVEL_COLOR,
    MUZZLE_FLASH_COLOR,
    PARTICLE_COLORS,
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_SPEED,
    PLAYER_COLOR,
    PLAYER_GLOW_COLOR,
    POWERUP_TYPES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    XP_BAR_BG_COLOR,
    XP_BAR_COLOR,
)


# ── Particle system ────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "radius")

    def __init__(self, x: float, y: float) -> None:
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, PARTICLE_SPEED)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = PARTICLE_LIFETIME
        self.max_life = PARTICLE_LIFETIME
        self.color = random.choice(PARTICLE_COLORS)
        self.radius = random.randint(2, 5)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= 1

    @property
    def alive(self) -> bool:
        return self.life > 0

    def draw(self, screen: pygame.Surface) -> None:
        alpha = int(255 * (self.life / self.max_life))
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(surf, (int(self.x) - self.radius, int(self.y) - self.radius))


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def emit(self, x: float, y: float, count: int = PARTICLE_COUNT) -> None:
        for _ in range(count):
            self.particles.append(Particle(x, y))

    def update(self) -> None:
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen: pygame.Surface) -> None:
        for p in self.particles:
            p.draw(screen)

    def reset(self) -> None:
        self.particles.clear()


# ── Renderer ────────────────────────────────────────────────────────────────

class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font_hud = pygame.font.SysFont("consolas", FONT_SIZE_HUD)
        self.font_game_over = pygame.font.SysFont("consolas", FONT_SIZE_GAME_OVER, bold=True)
        self.font_sub = pygame.font.SysFont("consolas", FONT_SIZE_SUB)
        self.font_small = pygame.font.SysFont("consolas", FONT_SIZE_SMALL)
        self.particles = ParticleSystem()

    # ── Background ──────────────────────────────────────────────────────
    def draw_background(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        grid_color = (35, 35, 35)
        for x in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(self.screen, grid_color, (0, y), (WINDOW_WIDTH, y))

    # ── Entities ────────────────────────────────────────────────────────
    def draw_player(self, player) -> None:
        player.draw(self.screen)

    def draw_clones(self, clones: list) -> None:
        for clone in clones:
            clone.draw(self.screen)

    # ── HUD ─────────────────────────────────────────────────────────────
    def draw_hud(
        self,
        seconds: float,
        score: int,
        clone_count: int,
        level: int,
        xp_ratio: float,
        weapon_name: str,
        dash_available: bool,
        dash_cooldown_ratio: float,
        active_effects: list[str],
        echo_ratio: float = 1.0,
    ) -> None:
        time_surf = self.font_hud.render(f"Time: {seconds:.1f}s", True, HUD_COLOR)
        score_surf = self.font_hud.render(f"Score: {score}", True, HUD_COLOR)
        self.screen.blit(time_surf, (15, 12))
        self.screen.blit(score_surf, (15, 38))

        clone_surf = self.font_hud.render(f"Clones: {clone_count}", True, HUD_COLOR)
        weap_surf = self.font_small.render(f"[{weapon_name}]", True, (255, 255, 150))
        self.screen.blit(clone_surf, (WINDOW_WIDTH - clone_surf.get_width() - 15, 12))
        self.screen.blit(weap_surf, (WINDOW_WIDTH - weap_surf.get_width() - 15, 38))

        lvl_surf = self.font_hud.render(f"LVL {level}", True, LEVEL_COLOR)
        self.screen.blit(lvl_surf, (15, 64))

        self._draw_xp_bar(xp_ratio)
        self._draw_echo_bar(echo_ratio)
        self._draw_dash_indicator(dash_available, dash_cooldown_ratio)
        self._draw_active_effects(active_effects)

    def _draw_xp_bar(self, ratio: float) -> None:
        bar_x, bar_y = 15, WINDOW_HEIGHT - 20
        bar_w, bar_h = WINDOW_WIDTH - 30, 8
        pygame.draw.rect(self.screen, XP_BAR_BG_COLOR, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(self.screen, XP_BAR_COLOR, (bar_x, bar_y, fill_w, bar_h), border_radius=4)

    def _draw_echo_bar(self, ratio: float) -> None:
        bar_x, bar_y = 15, WINDOW_HEIGHT - 34
        bar_w, bar_h = 140, 6
        # Label
        lbl = self.font_small.render("ECHO", True, ECHO_BAR_COLOR)
        self.screen.blit(lbl, (bar_x, bar_y - 16))
        # Background
        pygame.draw.rect(self.screen, ECHO_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(self.screen, ECHO_BAR_COLOR, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

    def _draw_dash_indicator(self, available: bool, ratio: float) -> None:
        cx, cy, r = WINDOW_WIDTH - 30, WINDOW_HEIGHT - 55, 10
        if available:
            pygame.draw.circle(self.screen, DASH_COLOR, (cx, cy), r)
            lbl = self.font_small.render("DASH", True, DASH_COLOR)
        else:
            pygame.draw.circle(self.screen, (60, 60, 70), (cx, cy), r)
            if ratio > 0:
                arc_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                end_angle = math.pi * 2 * ratio
                pygame.draw.arc(arc_surf, (*DASH_COLOR, 180),
                                (0, 0, r * 2, r * 2),
                                -math.pi / 2, -math.pi / 2 + end_angle, 3)
                self.screen.blit(arc_surf, (cx - r, cy - r))
            lbl = self.font_small.render("DASH", True, (80, 80, 90))
        self.screen.blit(lbl, (cx - lbl.get_width() - r - 4, cy - lbl.get_height() // 2))

    def _draw_active_effects(self, effects: list[str]) -> None:
        x, y = 170, WINDOW_HEIGHT - 48
        for etype in effects:
            info = POWERUP_TYPES.get(etype)
            if info is None:
                continue
            tag = self.font_small.render(etype.replace("_", " ").title(), True, info["color"])
            self.screen.blit(tag, (x, y))
            x += tag.get_width() + 12

    # ── Game Over ───────────────────────────────────────────────────────
    def draw_game_over(
        self, seconds: float, score: int, level: int, top_scores: list[dict],
    ) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        go_surf = self.font_game_over.render("GAME OVER", True, GAME_OVER_COLOR)
        self.screen.blit(go_surf, go_surf.get_rect(center=(WINDOW_WIDTH // 2, 120)))

        stat = f"Survived {seconds:.1f}s  |  Score {score}  |  Level {level}"
        stat_surf = self.font_sub.render(stat, True, HUD_COLOR)
        self.screen.blit(stat_surf, stat_surf.get_rect(center=(WINDOW_WIDTH // 2, 175)))

        lb_title = self.font_hud.render("— LEADERBOARD —", True, LEVEL_COLOR)
        self.screen.blit(lb_title, (WINDOW_WIDTH // 2 - lb_title.get_width() // 2, 215))

        y = 250
        for i, entry in enumerate(top_scores):
            line = f"#{i+1}  Score: {entry['score']}  Time: {entry['time']}s  Lvl {entry.get('level', 1)}"
            col = LEVEL_COLOR if i == 0 else HUD_COLOR
            surf = self.font_small.render(line, True, col)
            self.screen.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, y))
            y += 22

        r_hint = self.font_hud.render("R = Restart  |  P = Watch Replay", True, HUD_COLOR)
        self.screen.blit(r_hint, r_hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)))

    # ── Replay rendering ────────────────────────────────────────────────
    def draw_replay_frame(self, frame: dict) -> None:
        px, py = frame.get("px", 400), frame.get("py", 300)

        glow_surf = pygame.Surface((24 * 2, 24 * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*PLAYER_GLOW_COLOR, 40), (24, 24), 24)
        self.screen.blit(glow_surf, (int(px) - 24, int(py) - 24))
        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(px), int(py)), 12)

        if frame.get("dash"):
            pygame.draw.circle(self.screen, DASH_COLOR, (int(px), int(py)), 16, 2)

        if frame.get("shoot"):
            sdx, sdy = frame.get("sdx", 1), frame.get("sdy", 0)
            end_x = int(px + sdx * 30)
            end_y = int(py + sdy * 30)
            pygame.draw.line(self.screen, (255, 255, 100), (int(px), int(py)), (end_x, end_y), 2)

        for c in frame.get("clones", []):
            ct = c.get("t", "normal")
            color = CLONE_COLORS.get(ct, (200, 50, 50))
            pygame.draw.circle(self.screen, color, (int(c["x"]), int(c["y"])), 12)

    def draw_replay_hud(
        self, current_time: float, total_time: float,
        speed: float, paused: bool,
    ) -> None:
        bar_x, bar_y = 50, WINDOW_HEIGHT - 30
        bar_w, bar_h = WINDOW_WIDTH - 100, 6
        pygame.draw.rect(self.screen, (50, 50, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        ratio = current_time / max(0.1, total_time)
        fill = int(bar_w * ratio)
        pygame.draw.rect(self.screen, (80, 200, 255), (bar_x, bar_y, fill, bar_h), border_radius=3)

        status = "PAUSED" if paused else "PLAYING"
        info = f"REPLAY  {status}  {current_time:.1f}s / {total_time:.1f}s  [{speed:.1f}x]"
        surf = self.font_hud.render(info, True, (80, 200, 255))
        self.screen.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, 15))

        hint = self.font_small.render("SPACE=Pause  \u2190/\u2192=Speed  ESC=Exit", True, (140, 140, 150))
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, WINDOW_HEIGHT - 55))

    # ── Muzzle flash ────────────────────────────────────────────────────
    def draw_muzzle_flash(self, x: float, y: float) -> None:
        flash_radius = 18
        flash_surf = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            flash_surf, (*MUZZLE_FLASH_COLOR, 120),
            (flash_radius, flash_radius), flash_radius,
        )
        self.screen.blit(flash_surf, (int(x) - flash_radius, int(y) - flash_radius))

    # ── Particles ───────────────────────────────────────────────────────
    def update_particles(self) -> None:
        self.particles.update()

    def draw_particles(self) -> None:
        self.particles.draw(self.screen)

    def emit_particles(self, x: float, y: float) -> None:
        self.particles.emit(x, y)

    def reset_particles(self) -> None:
        self.particles.reset()
