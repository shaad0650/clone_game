"""
time_echo.py — Time Echo system for Mirror Clone Survival.
"""

from clone import Clone
from config import (
    ECHO_COST,
    ECHO_DELAY_FRAMES,
    ECHO_MAX_ENERGY,
    ECHO_REGEN_PER_SECOND,
    FPS,
)
from history import HistoryManager


class TimeEchoManager:
    """Manages echo energy and spawns echo clones from player history."""

    def __init__(self) -> None:
        self.energy: float = ECHO_MAX_ENERGY
        self._regen_per_frame: float = ECHO_REGEN_PER_SECOND / FPS

    # ── Tick ─────────────────────────────────────────────────────────────

    def update(self) -> None:
        """Regenerate energy each frame."""
        self.energy = min(ECHO_MAX_ENERGY, self.energy + self._regen_per_frame)

    # ── Activation ───────────────────────────────────────────────────────

    def can_spawn(self) -> bool:
        return self.energy >= ECHO_COST

    def try_spawn(self, history: HistoryManager) -> Clone | None:
        """Attempt to spawn an echo clone. Returns the clone or None."""
        if not self.can_spawn():
            return None

        current = history.get_current_frame()
        start = current - ECHO_DELAY_FRAMES
        if start < 0:
            return None  # not enough history yet

        self.energy -= ECHO_COST

        echo = Clone(
            history, start,
            clone_type="normal",
            mutation_type="normal",
            is_echo=True,
        )
        return echo

    # ── Query ────────────────────────────────────────────────────────────

    @property
    def energy_ratio(self) -> float:
        return self.energy / ECHO_MAX_ENERGY

    # ── Reset ────────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.energy = ECHO_MAX_ENERGY
