"""
config.py — All game constants for Mirror Clone Survival.
"""

# ── Window ──────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE  = "Mirror Clone Survival"

# ── Performance ─────────────────────────────────────────────────────────────
FPS = 60

# ── Player ──────────────────────────────────────────────────────────────────
PLAYER_RADIUS     = 12
PLAYER_SPEED      = 4
PLAYER_SPEED_CAP  = 8

# ── Dash ────────────────────────────────────────────────────────────────────
DASH_SPEED            = 12
DASH_DURATION_FRAMES  = 12
DASH_COOLDOWN_FRAMES  = 120

# ── Clones ──────────────────────────────────────────────────────────────────
CLONE_RADIUS         = 12
CLONE_DELAY_FRAMES   = 300
CLONE_SPAWN_INTERVAL = 300
MIN_SPAWN_INTERVAL   = 90
SPAWN_ACCELERATION   = 0.97

# ── Clone variants ──────────────────────────────────────────────────────────
CLONE_FAST_SPEED_MULT   = 2
CLONE_DELAYED_DELAY     = 600
CLONE_VARIANT_WEIGHTS   = {
    "normal":  40,
    "fast":    25,
    "delayed": 20,
    "shooter": 15,
}

# ── Clone mutations ────────────────────────────────────────────────────────
CLONE_MUTATION_TYPES    = ["normal", "fast", "mirror", "unstable"]
CLONE_MUTATION_WEIGHTS  = [40, 25, 20, 15]
UNSTABLE_JITTER         = 3.0        # max random offset per axis

# ── Boss Clone ──────────────────────────────────────────────────────────────
BOSS_CLONE_INTERVAL         = 1800   # 30 s
BOSS_CLONE_FIRST_DELAY      = 3600   # first boss at 60 s
BOSS_CLONE_SIZE_MULTIPLIER  = 2.0
BOSS_CLONE_SPEED_MULT       = 1.5    # history replay speed
BOSS_CLONE_HP               = 5

# ── History ─────────────────────────────────────────────────────────────────
MAX_HISTORY_LENGTH = 10_000

# ── Clone trail ─────────────────────────────────────────────────────────────
TRAIL_LENGTH  = 12
TRAIL_SPACING = 4

# ── Particles ───────────────────────────────────────────────────────────────
PARTICLE_COUNT    = 40
PARTICLE_LIFETIME = 45
PARTICLE_SPEED    = 5.0

# ── Bullets ─────────────────────────────────────────────────────────────────
BULLET_SPEED          = 8
BULLET_RADIUS         = 4
MAX_BULLETS           = 500
SHOOT_COOLDOWN_FRAMES = 10
BULLET_TRAIL_LENGTH   = 5
MUZZLE_FLASH_FRAMES   = 4
BULLET_LIFETIME_FRAMES = 600        # 10 seconds — persistent bullets

# ── Weapons ─────────────────────────────────────────────────────────────────
WEAPON_DEFS = [
    {"id": 0, "name": "Basic Gun",  "fire_rate": 10, "bullet_speed": 8,  "bullet_count": 1, "spread": 0,  "unlock_level": 1},
    {"id": 1, "name": "Rapid Gun",  "fire_rate": 5,  "bullet_speed": 9,  "bullet_count": 1, "spread": 0,  "unlock_level": 3},
    {"id": 2, "name": "Spread Gun", "fire_rate": 12, "bullet_speed": 7,  "bullet_count": 3, "spread": 25, "unlock_level": 5},
    {"id": 3, "name": "Laser Gun",  "fire_rate": 3,  "bullet_speed": 14, "bullet_count": 1, "spread": 0,  "unlock_level": 8},
]

# ── Powerups ────────────────────────────────────────────────────────────────
POWERUP_RADIUS             = 10
POWERUP_SPAWN_MIN_FRAMES   = 600
POWERUP_SPAWN_MAX_FRAMES   = 1200
POWERUP_MAX_ACTIVE         = 3
POWERUP_TYPES = {
    "speed_boost":  {"duration": 360, "color": (100, 200, 255)},
    "shield":       {"duration": 300, "color": (100, 255, 100)},
    "slow_motion":  {"duration": 240, "color": (200, 100, 255)},
    "rapid_fire":   {"duration": 300, "color": (255, 255, 100)},
}

# ── XP / Levels ─────────────────────────────────────────────────────────────
XP_PER_CLONE_KILL   = 10
XP_PER_SECOND       = 1
XP_BASE_THRESHOLD   = 50
XP_GROWTH_FACTOR    = 1.4
SPEED_BONUS_PER_LVL = 0.15
BULLET_SPD_BONUS    = 0.3
MAX_LEVEL           = 15

# ── Leaderboard ─────────────────────────────────────────────────────────────
LEADERBOARD_FILE = "leaderboard.json"
LEADERBOARD_SIZE = 10

# ── Upgrades ────────────────────────────────────────────────────────────────
UPGRADE_INTERVAL_FRAMES = 1800      # every 30 s
UPGRADE_CHOICES_COUNT   = 3
UPGRADE_DEFS = {
    "movement_speed_boost":   {"label": "Speed +15%",      "value": 0.6},
    "bullet_speed_boost":     {"label": "Bullet Speed +1",  "value": 1.0},
    "dash_cooldown_reduction":{"label": "Dash CD −20%",     "value": 0.2},
    "clone_spawn_delay":      {"label": "Clone Delay +1s",  "value": 60},
}

# ── Hazards ─────────────────────────────────────────────────────────────────
HAZARD_SPAWN_MIN_FRAMES = 1200      # 20 s
HAZARD_SPAWN_MAX_FRAMES = 2400      # 40 s
HAZARD_MAX_ACTIVE       = 3
HAZARD_LIFETIME_FRAMES  = 600       # 10 s per hazard
HAZARD_WALL_SPEED       = 2.0
HAZARD_LASER_SPEED      = 0.02      # radians/frame
HAZARD_ZONE_RADIUS      = 50

# ── Replay ──────────────────────────────────────────────────────────────────
REPLAY_FILE = "replay.json"

# ── Time Echo ───────────────────────────────────────────────────────────────
ECHO_MAX_ENERGY      = 100
ECHO_COST            = 25
ECHO_REGEN_PER_SECOND = 10
ECHO_DELAY_FRAMES    = 300      # 5 seconds

# ── Colours (R, G, B) ──────────────────────────────────────────────────────
BACKGROUND_COLOR   = (20, 20, 20)
PLAYER_COLOR       = (50, 200, 50)
PLAYER_GLOW_COLOR  = (80, 255, 80)

CLONE_COLORS = {
    "normal":  (200, 50, 50),
    "fast":    (255, 160, 50),
    "delayed": (160, 80, 220),
    "shooter": (255, 100, 180),
}
CLONE_GLOW_COLORS = {
    "normal":  (255, 80, 80),
    "fast":    (255, 200, 80),
    "delayed": (200, 120, 255),
    "shooter": (255, 150, 220),
}
TRAIL_COLOR        = (200, 50, 50)
HUD_COLOR          = (220, 220, 220)
GAME_OVER_COLOR    = (255, 60, 60)
PARTICLE_COLORS    = [
    (255, 100, 100),
    (255, 160, 60),
    (255, 220, 80),
    (255, 255, 180),
]
BULLET_COLOR_PLAYER = (255, 255, 100)
BULLET_COLOR_CLONE  = (255, 100, 100)
MUZZLE_FLASH_COLOR  = (255, 255, 200)

DASH_COLOR         = (80, 160, 255)
XP_BAR_COLOR       = (80, 200, 255)
XP_BAR_BG_COLOR    = (50, 50, 60)
LEVEL_COLOR        = (255, 220, 80)
SHIELD_COLOR       = (100, 255, 100)

BOSS_COLOR         = (255, 80, 40)
BOSS_GLOW_COLOR    = (255, 200, 60)

HAZARD_WALL_COLOR  = (255, 80, 80)
HAZARD_LASER_COLOR = (255, 50, 50)
HAZARD_ZONE_COLOR  = (255, 160, 0)

UPGRADE_BG_COLOR   = (30, 30, 40)
UPGRADE_HL_COLOR   = (80, 200, 255)

MUTATION_COLORS = {
    "normal":   (200, 50, 50),
    "fast":     (255, 160, 50),
    "mirror":   (50, 200, 200),
    "unstable": (200, 200, 50),
}

ECHO_COLOR      = (0, 220, 255)
ECHO_GLOW_COLOR = (60, 240, 255)
ECHO_BAR_COLOR  = (0, 200, 240)
ECHO_BAR_BG     = (40, 50, 60)

# ── Fonts ───────────────────────────────────────────────────────────────────
FONT_SIZE_HUD       = 24
FONT_SIZE_GAME_OVER = 64
FONT_SIZE_SUB       = 28
FONT_SIZE_SMALL     = 18
