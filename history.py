"""
history.py — Records and serves player movement, shooting, dash, and weapon history.
"""

from config import MAX_HISTORY_LENGTH


class FrameData:
    """Data recorded for a single frame."""

    __slots__ = ("x", "y", "shoot", "dir_x", "dir_y", "dashing", "weapon_id")

    def __init__(
        self,
        x: float,
        y: float,
        shoot: bool = False,
        dir_x: float = 0.0,
        dir_y: float = 0.0,
        dashing: bool = False,
        weapon_id: int = 0,
    ) -> None:
        self.x = x
        self.y = y
        self.shoot = shoot
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.dashing = dashing
        self.weapon_id = weapon_id


class HistoryManager:
    """Stores per-frame data and serves it to clones for deterministic replay."""

    def __init__(self) -> None:
        self._frames: list[FrameData | None] = []
        self._frame: int = 0
        # Pending events (set before add_position)
        self._pending_shoot: bool = False
        self._pending_dir_x: float = 0.0
        self._pending_dir_y: float = 0.0
        self._pending_dashing: bool = False
        self._pending_weapon_id: int = 0

    # ── Recording ───────────────────────────────────────────────────────

    def record_shoot_event(self, direction_x: float, direction_y: float) -> None:
        self._pending_shoot = True
        self._pending_dir_x = direction_x
        self._pending_dir_y = direction_y

    def record_dash(self, dashing: bool) -> None:
        self._pending_dashing = dashing

    def record_weapon(self, weapon_id: int) -> None:
        self._pending_weapon_id = weapon_id

    def add_position(self, x: float, y: float) -> None:
        """Append a frame with all pending event data."""
        self._frames.append(
            FrameData(
                x, y,
                shoot=self._pending_shoot,
                dir_x=self._pending_dir_x,
                dir_y=self._pending_dir_y,
                dashing=self._pending_dashing,
                weapon_id=self._pending_weapon_id,
            )
        )
        self._pending_shoot = False
        self._pending_dir_x = 0.0
        self._pending_dir_y = 0.0
        # dashing and weapon_id persist until changed
        self._frame += 1
        self.trim_history()

    # ── Querying ────────────────────────────────────────────────────────

    def get_position(self, frame_index: int) -> tuple[float, float] | None:
        fd = self.get_frame_data(frame_index)
        if fd is not None:
            return fd.x, fd.y
        return None

    def get_frame_data(self, frame_index: int) -> FrameData | None:
        if 0 <= frame_index < len(self._frames):
            return self._frames[frame_index]
        return None

    def get_current_frame(self) -> int:
        return self._frame

    # ── Memory management ───────────────────────────────────────────────

    def trim_history(self) -> None:
        overflow = len(self._frames) - MAX_HISTORY_LENGTH
        if overflow > 0:
            for i in range(overflow):
                self._frames[i] = None

    # ── Reset ───────────────────────────────────────────────────────────

    def reset(self) -> None:
        self._frames.clear()
        self._frame = 0
        self._pending_shoot = False
        self._pending_dir_x = 0.0
        self._pending_dir_y = 0.0
        self._pending_dashing = False
        self._pending_weapon_id = 0
