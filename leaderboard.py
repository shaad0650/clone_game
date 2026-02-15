"""
leaderboard.py — Persistent leaderboard for Mirror Clone Survival.
"""

import json
import os

from config import LEADERBOARD_FILE, LEADERBOARD_SIZE


class Leaderboard:
    """Load/save top scores + survival times to a JSON file."""

    def __init__(self) -> None:
        self._path: str = os.path.join(os.path.dirname(__file__), LEADERBOARD_FILE)
        self.entries: list[dict] = []
        self.load()

    # ── Persistence ─────────────────────────────────────────────────────

    def load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    self.entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.entries = []
        else:
            self.entries = []

    def save(self) -> None:
        try:
            with open(self._path, "w") as f:
                json.dump(self.entries, f, indent=2)
        except IOError:
            pass

    # ── Mutators ────────────────────────────────────────────────────────

    def add_score(self, score: int, survival_time: float, level: int = 1) -> None:
        self.entries.append({
            "score": score,
            "time": round(survival_time, 1),
            "level": level,
        })
        # Sort descending by score
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        # Keep top N
        self.entries = self.entries[:LEADERBOARD_SIZE]
        self.save()

    # ── Queries ─────────────────────────────────────────────────────────

    def get_top_scores(self, n: int = 5) -> list[dict]:
        return self.entries[:n]
