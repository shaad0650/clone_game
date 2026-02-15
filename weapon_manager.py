"""
weapon_manager.py — Manages weapon unlocks and switching.
"""

from weapon import ALL_WEAPONS, WEAPON_BY_ID, Weapon


class WeaponManager:
    """Tracks unlocked weapons and the currently selected weapon."""

    def __init__(self) -> None:
        self.unlocked_ids: set[int] = {0}   # basic_gun always unlocked
        self.current_id: int = 0

    @property
    def current(self) -> Weapon:
        return WEAPON_BY_ID[self.current_id]

    # ── Level-up check ──────────────────────────────────────────────────

    def check_unlocks(self, level: int) -> Weapon | None:
        """Unlock any weapon whose unlock_level <= *level*.

        Returns the newly-equipped weapon if one was just unlocked, else None.
        """
        newly = None
        for w in ALL_WEAPONS:
            if w.id not in self.unlocked_ids and w.unlock_level <= level:
                self.unlocked_ids.add(w.id)
                newly = w
        # Auto-equip the best unlocked weapon
        if newly is not None:
            self.current_id = max(self.unlocked_ids)
        return newly

    # ── Fire helper ─────────────────────────────────────────────────────

    def fire(self, base_dx: float, base_dy: float) -> list[tuple[float, float]]:
        """Return list of (dx, dy) directions for the current weapon."""
        return self.current.get_fire_directions(base_dx, base_dy)

    # ── Weapon by id (for clone replay) ─────────────────────────────────

    @staticmethod
    def fire_with_weapon(weapon_id: int, base_dx: float, base_dy: float) -> list[tuple[float, float]]:
        w = WEAPON_BY_ID.get(weapon_id)
        if w is None:
            return [(base_dx, base_dy)]
        return w.get_fire_directions(base_dx, base_dy)

    @staticmethod
    def get_weapon(weapon_id: int) -> Weapon:
        return WEAPON_BY_ID.get(weapon_id, WEAPON_BY_ID[0])

    # ── Reset ───────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.unlocked_ids = {0}
        self.current_id = 0
