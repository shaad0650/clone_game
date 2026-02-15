"""
progression_manager.py — XP and level progression for Mirror Clone Survival.
"""

from config import (
    BULLET_SPD_BONUS,
    MAX_LEVEL,
    SPEED_BONUS_PER_LVL,
    XP_BASE_THRESHOLD,
    XP_GROWTH_FACTOR,
    XP_PER_CLONE_KILL,
    XP_PER_SECOND,
    FPS,
)


class ProgressionManager:
    """Tracks XP, level, and stat bonuses."""

    def __init__(self) -> None:
        self.xp: int = 0
        self.level: int = 1
        self.xp_to_next: int = XP_BASE_THRESHOLD
        self._xp_acc_frames: int = 0   # accumulator for time-based XP

    # ── XP grants ───────────────────────────────────────────────────────

    def grant_kill_xp(self, count: int = 1) -> None:
        self.xp += XP_PER_CLONE_KILL * count
        self._check_level_up()

    def grant_survival_xp(self) -> None:
        """Call once per frame; awards XP_PER_SECOND every second."""
        self._xp_acc_frames += 1
        if self._xp_acc_frames >= FPS:
            self.xp += XP_PER_SECOND
            self._xp_acc_frames = 0
            self._check_level_up()

    # ── Level logic ─────────────────────────────────────────────────────

    def _check_level_up(self) -> None:
        while self.level < MAX_LEVEL and self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(XP_BASE_THRESHOLD * (XP_GROWTH_FACTOR ** (self.level - 1)))

    # ── Stat bonuses ────────────────────────────────────────────────────

    @property
    def speed_bonus(self) -> float:
        return SPEED_BONUS_PER_LVL * (self.level - 1)

    @property
    def bullet_speed_bonus(self) -> float:
        return BULLET_SPD_BONUS * (self.level - 1)

    @property
    def xp_ratio(self) -> float:
        """0.0–1.0 progress to next level."""
        if self.xp_to_next == 0:
            return 1.0
        return min(1.0, self.xp / self.xp_to_next)

    # ── Reset ───────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.xp = 0
        self.level = 1
        self.xp_to_next = XP_BASE_THRESHOLD
        self._xp_acc_frames = 0
