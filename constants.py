# --- CONFIG BÁSICA ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

FPS = 60

TILE_SIZE = 32

SCROLL_THRESH = 150

PLAYER_SCALE = 2

# --- ANIMACIONES JUGADOR ---
ANIM_IDLE = 0
ANIM_RUN_UP = 1
ANIM_RUN_DOWN = 2
ANIM_RUN_LEFT = 3
ANIM_RUN_RIGHT = 4

# --- ANIMACIONES ENEMIGO ---
ENEMY_IDLE = 0
ENEMY_RUN_UP = 1
ENEMY_RUN_DOWN = 2
ENEMY_RUN_LEFT = 3
ENEMY_RUN_RIGHT = 4

# --- ENEMIGOS ---
ENEMY_SPEED = 80                     
ENEMY_VISION_RADIUS = 3 * TILE_SIZE  
PATROL_RADIUS_TILES = 3            
ANIM_COOLDOWN = 150    

DAMAGE_COOLDOWN = 1.2

# --- VIDA (CORAZONES) ---
HEART_SIZE = 32

HEART_COUNT = 3          # 3 corazones visibles
HEART_HP = 2             # 2 puntos por corazón (medio = 1)
MAX_HEALTH = HEART_COUNT * HEART_HP    # 6

 
# --- ENERGÍA ---

ENERGY_FRAMES = 9
MAX_ENERGY = ENERGY_FRAMES - 1 
ENERGY_SIZE = 48

# --- SPRINT
SPRINT_MULT = 1.8            # cuántas veces más rápido corre al sprintar
ENERGY_DRAIN_PER_SEC = 3.0   # cuánta energía se gasta por segundo sprintando
ENERGY_REGEN_PER_SEC = 0.9   # cuánta energía se regenera por segundo sin sprint

SPRINT_LOCK_TIME = 2.5