"""
game.py — Core game logic for Mirror Clone Survival.
"""

import random

import pygame

from boss_clone import BossClone
from bullet_manager import BulletManager
from clone import Clone, pick_variant
from config import (
    BOSS_CLONE_FIRST_DELAY,
    BOSS_CLONE_INTERVAL,
    BULLET_COLOR_CLONE,
    BULLET_COLOR_PLAYER,
    CLONE_DELAYED_DELAY,
    CLONE_DELAY_FRAMES,
    CLONE_SPAWN_INTERVAL,
    DASH_COOLDOWN_FRAMES,
    ECHO_MAX_ENERGY,
    ECHO_REGEN_PER_SECOND,
    FPS,
    MIN_SPAWN_INTERVAL,
    MUZZLE_FLASH_FRAMES,
    PLAYER_SPEED,
    SPAWN_ACCELERATION,
)
from hazard import HazardManager
from history import HistoryManager
from instruction_screen import InstructionScreen
from leaderboard import Leaderboard
from player import Player
from powerup_manager import PowerupManager
from progression_manager import ProgressionManager
from renderer import Renderer
from replay_manager import ReplayManager
from time_echo import TimeEchoManager
from upgrade import UpgradeManager
from utils import check_collision
from weapon_manager import WeaponManager

# ── Game states ─────────────────────────────────────────────────────────────
STATE_INSTRUCTION = 0
STATE_PLAYING     = 1
STATE_GAME_OVER   = 2


class Game:
    """Owns all entities and drives state transitions."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.renderer = Renderer(screen)
        self.instruction_screen = InstructionScreen()

        # Entities
        self.player = Player()
        self.history = HistoryManager()
        self.clones: list[Clone] = []
        self.bosses: list[BossClone] = []
        self.bullet_manager = BulletManager()

        # Systems
        self.powerup_mgr = PowerupManager()
        self.progression = ProgressionManager()
        self.weapon_mgr = WeaponManager()
        self.leaderboard = Leaderboard()
        self.upgrade_mgr = UpgradeManager()
        self.hazard_mgr = HazardManager()
        self.replay_mgr = ReplayManager()
        self.echo_mgr = TimeEchoManager()

        # State
        self.state: int = STATE_INSTRUCTION
        self.game_over: bool = False
        self.frame_count: int = 0
        self.score: int = 0
        self._prev_level: int = 1

        # Clone spawning
        self.spawn_interval: float = CLONE_SPAWN_INTERVAL
        self.frames_since_last_spawn: int = 0

        # Boss spawning
        self._boss_timer: int = 0

        # Muzzle flash
        self._flash_timer: int = 0
        self._flash_x: float = 0.0
        self._flash_y: float = 0.0

        # Slow-motion
        self._slow_tick: bool = False

        # Upgrade dash CD override
        self._upgrade_dash_cd: int = DASH_COOLDOWN_FRAMES

        # Replay mode
        self.replay_mode: bool = False

    # ── Public API ──────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        # ── Instruction screen ──────────────────────────────────────────
        if self.state == STATE_INSTRUCTION:
            if self.instruction_screen.handle_event(event):
                self.state = STATE_PLAYING
            return

        # ── Replay playback ─────────────────────────────────────────────
        if self.replay_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.replay_mgr.toggle_pause()
                elif event.key == pygame.K_RIGHT:
                    self.replay_mgr.speed_up()
                elif event.key == pygame.K_LEFT:
                    self.replay_mgr.speed_down()
                elif event.key == pygame.K_ESCAPE:
                    self.replay_mgr.stop_playback()
                    self.replay_mode = False
            return

        # ── Upgrade selection ───────────────────────────────────────────
        if self.upgrade_mgr.paused:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                picked = self.upgrade_mgr.handle_event(event)
                if picked is not None:
                    self.upgrade_mgr.apply(picked, self)
            return

        # ── Game over ───────────────────────────────────────────────────
        if self.state == STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                if self.replay_mgr.start_playback():
                    self.replay_mode = True
            return

        # ── Normal play ─────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            weapon = self.weapon_mgr.current
            self.player.handle_shoot_input(
                mouse_pos=event.pos, fire_rate=weapon.fire_rate
            )

        # Time Echo — E key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            echo = self.echo_mgr.try_spawn(self.history)
            if echo is not None:
                self.clones.append(echo)

    def update(self) -> None:
        # ── Instruction state — no updates ──────────────────────────────
        if self.state == STATE_INSTRUCTION:
            return

        # ── Replay playback ─────────────────────────────────────────────
        if self.replay_mode:
            if self.replay_mgr.playing:
                self.replay_mgr.advance()
            else:
                self.replay_mode = False
            return

        # ── Game over — just particle/bullet wind-down ──────────────────
        if self.state == STATE_GAME_OVER:
            self.renderer.update_particles()
            self.bullet_manager.update(self.frame_count)
            return

        # ── Upgrade pause ───────────────────────────────────────────────
        if self.upgrade_mgr.tick():
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # SPACE shooting
        if keys[pygame.K_SPACE]:
            weapon = self.weapon_mgr.current
            self.player.handle_shoot_input(
                space_pressed=True, fire_rate=weapon.fire_rate
            )

        # Apply powerup effects
        self._apply_powerup_effects()

        # Dash CD override
        if not self.player.dash_available and self.player.dash_cooldown_timer > self._upgrade_dash_cd:
            self.player.dash_cooldown_timer = self._upgrade_dash_cd

        self.player.update()

        # ── Echo energy regen ───────────────────────────────────────────
        self.echo_mgr.update()
        self.player.echo_energy = self.echo_mgr.energy

        # ── Record into history ─────────────────────────────────────────
        if self.player.shoot_requested:
            self.history.record_shoot_event(
                self.player.shoot_dir_x, self.player.shoot_dir_y
            )
        self.history.record_dash(self.player.is_dashing)
        self.history.record_weapon(self.weapon_mgr.current_id)

        px, py = self.player.get_position()
        self.history.add_position(px, py)

        # ── Player bullets ──────────────────────────────────────────────
        if self.player.shoot_requested:
            weapon = self.weapon_mgr.current
            dirs = self.weapon_mgr.fire(
                self.player.shoot_dir_x, self.player.shoot_dir_y
            )
            bspeed = weapon.bullet_speed + self.progression.bullet_speed_bonus
            for dx, dy in dirs:
                self.bullet_manager.spawn_bullet(
                    px, py, dx, dy, "player", BULLET_COLOR_PLAYER,
                    bullet_speed=bspeed,
                    current_frame=self.frame_count,
                )
            self._flash_timer = MUZZLE_FLASH_FRAMES
            self._flash_x = px
            self._flash_y = py

        # ── Clone spawning ──────────────────────────────────────────────
        self.frames_since_last_spawn += 1
        if self.frames_since_last_spawn >= int(self.spawn_interval):
            self.spawn_clone()
            self.frames_since_last_spawn = 0
            self.spawn_interval = max(
                MIN_SPAWN_INTERVAL, self.spawn_interval * SPAWN_ACCELERATION
            )

        # ── Boss clone spawning ─────────────────────────────────────────
        self._boss_timer += 1
        if self.frame_count >= BOSS_CLONE_FIRST_DELAY and self._boss_timer >= BOSS_CLONE_INTERVAL:
            self._boss_timer = 0
            self.spawn_boss()

        # ── Update clones ───────────────────────────────────────────────
        slow_motion = self.powerup_mgr.is_active("slow_motion")
        if slow_motion:
            self._slow_tick = not self._slow_tick

        all_clones = self.clones + self.bosses
        for clone in all_clones:
            if slow_motion and self._slow_tick:
                pass
            else:
                clone.update()
            if clone.alive and clone.shoot_requested:
                w = WeaponManager.get_weapon(clone.shoot_weapon_id)
                dirs = WeaponManager.fire_with_weapon(
                    clone.shoot_weapon_id,
                    clone.shoot_dir_x, clone.shoot_dir_y,
                )
                for dx, dy in dirs:
                    self.bullet_manager.spawn_bullet(
                        clone.x, clone.y, dx, dy, "clone",
                        BULLET_COLOR_CLONE,
                        bullet_speed=w.bullet_speed,
                        current_frame=self.frame_count,
                    )

        # ── Update bullets ──────────────────────────────────────────────
        self.bullet_manager.update(self.frame_count)

        # ── Powerups ────────────────────────────────────────────────────
        self.powerup_mgr.update(self.player)

        # ── Hazards ─────────────────────────────────────────────────────
        self.hazard_mgr.update()

        # ── Collisions ──────────────────────────────────────────────────
        self.check_collisions()

        # ── Progression ─────────────────────────────────────────────────
        self.progression.grant_survival_xp()
        if self.progression.level != self._prev_level:
            self._prev_level = self.progression.level
            self.weapon_mgr.check_unlocks(self.progression.level)

        # ── Record replay ───────────────────────────────────────────────
        clone_snap = [{"x": c.x, "y": c.y, "t": c.clone_type}
                      for c in self.clones if c.alive]
        self.replay_mgr.record_frame(
            px, py, self.player.is_dashing, clone_snap,
            self.player.shoot_requested,
            (self.player.shoot_dir_x, self.player.shoot_dir_y),
        )

        # ── Muzzle flash ────────────────────────────────────────────────
        if self._flash_timer > 0:
            self._flash_timer -= 1

        self.frame_count += 1
        self.score += 1

    def render(self) -> None:
        # ── Instruction screen ──────────────────────────────────────────
        if self.state == STATE_INSTRUCTION:
            self.instruction_screen.draw(self.screen)
            return

        # ── Replay playback ─────────────────────────────────────────────
        if self.replay_mode:
            self.renderer.draw_background()
            frame = self.replay_mgr.get_current()
            if frame is not None:
                self.renderer.draw_replay_frame(frame)
            self.renderer.draw_replay_hud(
                self.replay_mgr.playback_time,
                self.replay_mgr.total_time,
                self.replay_mgr.playback_speed,
                self.replay_mgr.playback_paused,
            )
            return

        # ── Normal render ───────────────────────────────────────────────
        self.renderer.draw_background()

        self.hazard_mgr.draw(self.screen)
        self.powerup_mgr.draw(self.screen)

        self.renderer.draw_clones(self.clones)
        self.renderer.draw_clones(self.bosses)
        self.renderer.draw_player(self.player)

        if self._flash_timer > 0:
            self.renderer.draw_muzzle_flash(self._flash_x, self._flash_y)

        self.bullet_manager.draw(self.screen)
        self.renderer.draw_particles()

        survival = self.frame_count / FPS
        self.renderer.draw_hud(
            seconds=survival,
            score=self.score,
            clone_count=len(self.clones) + len(self.bosses),
            level=self.progression.level,
            xp_ratio=self.progression.xp_ratio,
            weapon_name=self.weapon_mgr.current.name,
            dash_available=self.player.dash_available,
            dash_cooldown_ratio=self._dash_cooldown_ratio(),
            active_effects=list(self.powerup_mgr.active_effects.keys()),
            echo_ratio=self.echo_mgr.energy_ratio,
        )

        if self.state == STATE_GAME_OVER:
            self.renderer.draw_game_over(
                survival, self.score, self.progression.level,
                self.leaderboard.get_top_scores(),
            )

        self.upgrade_mgr.draw(self.screen)

    # ── Clone management ────────────────────────────────────────────────

    def spawn_clone(self) -> None:
        current = self.history.get_current_frame()
        variant = pick_variant()
        delay = CLONE_DELAYED_DELAY if variant == "delayed" else CLONE_DELAY_FRAMES
        start_frame = max(0, current - delay)
        if current > delay:
            self.clones.append(Clone(self.history, start_frame, clone_type=variant))

    def spawn_boss(self) -> None:
        current = self.history.get_current_frame()
        start = max(0, current - CLONE_DELAY_FRAMES)
        if current > CLONE_DELAY_FRAMES:
            self.bosses.append(BossClone(self.history, start))

    # ── Collision ───────────────────────────────────────────────────────

    def check_collisions(self) -> None:
        # Player vs hazards
        if self.hazard_mgr.check_hits(self.player.x, self.player.y, self.player.radius):
            if not self.player.shield_active and not self.player.is_dashing:
                self._trigger_game_over()
                return

        # Clone vs hazards
        for clone in self.clones[:]:
            if clone.alive and self.hazard_mgr.check_hits(clone.x, clone.y, clone.radius):
                clone.alive = False
                self.renderer.emit_particles(clone.x, clone.y)
                self.score += 50

        # Body-to-body (regular clones)
        for clone in self.clones:
            if clone.alive and check_collision(self.player, clone):
                if self.player.shield_active or self.player.is_dashing:
                    clone.alive = False
                    self.renderer.emit_particles(clone.x, clone.y)
                    self.score += 100
                    self.progression.grant_kill_xp()
                else:
                    self._trigger_game_over()
                    return

        # Body-to-body (bosses)
        for boss in self.bosses:
            if boss.alive and check_collision(self.player, boss):
                if self.player.shield_active or self.player.is_dashing:
                    if boss.take_hit():
                        self.renderer.emit_particles(boss.x, boss.y)
                        self.score += 500
                        self.progression.grant_kill_xp(5)
                else:
                    self._trigger_game_over()
                    return

        # Bullet collisions — regular clones
        result = self.bullet_manager.check_collisions(self.player, self.clones)

        if result["player_hit"]:
            self._trigger_game_over()

        for idx in result["clones_hit"]:
            if 0 <= idx < len(self.clones):
                c = self.clones[idx]
                self.renderer.emit_particles(c.x, c.y)
                self.score += 100
                self.progression.grant_kill_xp()

        self.clones = [c for c in self.clones if c.alive]

        # Bullet collisions — bosses
        for b in self.bullet_manager.bullets:
            if not b.alive or b.owner_type != "player":
                continue
            for boss in self.bosses:
                if not boss.alive:
                    continue
                from utils import calculate_distance
                dist = calculate_distance(b.x, b.y, boss.x, boss.y)
                if dist < (b.radius + boss.radius):
                    b.destroy()
                    if boss.take_hit():
                        self.renderer.emit_particles(boss.x, boss.y)
                        self.score += 500
                        self.progression.grant_kill_xp(5)
                    break

        self.bosses = [b for b in self.bosses if b.alive]

    def _trigger_game_over(self) -> None:
        self.state = STATE_GAME_OVER
        self.game_over = True
        self.renderer.emit_particles(self.player.x, self.player.y)
        self.leaderboard.add_score(
            self.score, self.frame_count / FPS, self.progression.level,
        )
        self.replay_mgr.save()

    # ── Powerup effects ─────────────────────────────────────────────────

    def _apply_powerup_effects(self) -> None:
        if self.powerup_mgr.is_active("speed_boost"):
            self.player.speed = PLAYER_SPEED + self.progression.speed_bonus + 2.0
        else:
            self.player.speed = PLAYER_SPEED + self.progression.speed_bonus
        self.player.shield_active = self.powerup_mgr.is_active("shield")

    def _dash_cooldown_ratio(self) -> float:
        if self.player.dash_available:
            return 1.0
        return 1.0 - (self.player.dash_cooldown_timer / max(1, self._upgrade_dash_cd))

    # ── Reset ───────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.player.reset()
        self.history.reset()
        self.clones.clear()
        self.bosses.clear()
        self.bullet_manager.reset()
        self.powerup_mgr.reset()
        self.progression.reset()
        self.weapon_mgr.reset()
        self.upgrade_mgr.reset()
        self.hazard_mgr.reset()
        self.replay_mgr.reset()
        self.echo_mgr.reset()
        self.renderer.reset_particles()
        self.state = STATE_PLAYING
        self.game_over = False
        self.replay_mode = False
        self.frame_count = 0
        self.score = 0
        self._prev_level = 1
        self.spawn_interval = CLONE_SPAWN_INTERVAL
        self.frames_since_last_spawn = 0
        self._boss_timer = 0
        self._flash_timer = 0
        self._slow_tick = False
        self._upgrade_dash_cd = DASH_COOLDOWN_FRAMES
