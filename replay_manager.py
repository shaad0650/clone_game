"""
replay_manager.py — Replay recording and playback for Mirror Clone Survival.
"""

import json
import os

from config import FPS, REPLAY_FILE


class ReplayManager:
    """Records per-frame game state and provides playback."""

    def __init__(self) -> None:
        self._path: str = os.path.join(os.path.dirname(__file__), REPLAY_FILE)
        self.frames: list[dict] = []
        self.recording: bool = True
        self.playing: bool = False
        self.playback_frame: int = 0
        self.playback_speed: float = 1.0
        self._speed_acc: float = 0.0
        self.playback_paused: bool = False

    # ── Recording ───────────────────────────────────────────────────────

    def record_frame(
        self,
        player_x: float,
        player_y: float,
        player_dashing: bool,
        clones: list[dict],
        shoot: bool,
        shoot_dir: tuple[float, float],
    ) -> None:
        if not self.recording:
            return
        self.frames.append({
            "px": round(player_x, 1),
            "py": round(player_y, 1),
            "dash": player_dashing,
            "clones": clones,            # [{x, y, type}]
            "shoot": shoot,
            "sdx": round(shoot_dir[0], 3),
            "sdy": round(shoot_dir[1], 3),
        })

    # ── Persistence ─────────────────────────────────────────────────────

    def save(self) -> None:
        try:
            with open(self._path, "w") as f:
                json.dump(self.frames, f)
        except IOError:
            pass

    def load(self) -> bool:
        if not os.path.exists(self._path):
            return False
        try:
            with open(self._path, "r") as f:
                self.frames = json.load(f)
            return len(self.frames) > 0
        except (json.JSONDecodeError, IOError):
            return False

    # ── Playback ────────────────────────────────────────────────────────

    def start_playback(self) -> bool:
        """Start replay playback. Returns False if no data."""
        if not self.frames:
            if not self.load():
                return False
        self.playing = True
        self.recording = False
        self.playback_frame = 0
        self.playback_speed = 1.0
        self._speed_acc = 0.0
        self.playback_paused = False
        return True

    def stop_playback(self) -> None:
        self.playing = False

    def advance(self) -> dict | None:
        """Advance playback and return current frame data, or None if done."""
        if not self.playing or self.playback_paused:
            return self.get_current()

        self._speed_acc += self.playback_speed
        steps = int(self._speed_acc)
        self._speed_acc -= steps

        self.playback_frame += steps
        if self.playback_frame >= len(self.frames):
            self.playback_frame = len(self.frames) - 1
            self.playing = False
            return None
        return self.frames[self.playback_frame]

    def get_current(self) -> dict | None:
        if 0 <= self.playback_frame < len(self.frames):
            return self.frames[self.playback_frame]
        return None

    @property
    def total_frames(self) -> int:
        return len(self.frames)

    @property
    def playback_time(self) -> float:
        return self.playback_frame / FPS

    @property
    def total_time(self) -> float:
        return len(self.frames) / FPS

    # ── Speed control ───────────────────────────────────────────────────

    def speed_up(self) -> None:
        self.playback_speed = min(4.0, self.playback_speed + 0.5)

    def speed_down(self) -> None:
        self.playback_speed = max(0.5, self.playback_speed - 0.5)

    def toggle_pause(self) -> None:
        self.playback_paused = not self.playback_paused

    # ── Reset ───────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.frames.clear()
        self.recording = True
        self.playing = False
        self.playback_frame = 0
        self.playback_speed = 1.0
        self._speed_acc = 0.0
        self.playback_paused = False
