import pygame
import random
import math

from world import *
from constants import *


class Enemy:
    def __init__(self, x_tile, y_tile, animation_frames, world):
        # posición en píxeles
        self.px = x_tile * TILE_SIZE
        self.py = y_tile * TILE_SIZE

        self.animation_list = animation_frames   # lista de listas
        self.action = ENEMY_IDLE
        self.frame_index = 0
        self.last_anim_update = pygame.time.get_ticks()
        self.image = self.animation_list[self.action][self.frame_index]

        # hitbox
        self.rect = pygame.Rect(self.px, self.py, TILE_SIZE, TILE_SIZE)

        # movimiento
        self.vx = 0.0
        self.vy = 0.0
        self.speed = ENEMY_SPEED

        # movimiento aleatorio cuando no tiene buena patrulla
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.last_dir_change = pygame.time.get_ticks()

        # IA
        self.state = "patrol"  # "patrol", "chase", "return"
        self.patrol_points = self._generar_puntos_patrulla(x_tile, y_tile, world)
        self.patrol_index = 0

    # ---------- SET ACTION ----------
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.frame_index = 0
            self.last_anim_update = pygame.time.get_ticks()
            self.image = self.animation_list[self.action][self.frame_index]

    # ---------- GENERAR RUTA DE PATRULLA ALEATORIA ----------
    def _generar_puntos_patrulla(self, x_tile, y_tile, world):
        puntos = []

        # siempre incluimos el punto de spawn como patrulla
        puntos.append((x_tile, y_tile))

        intentos = 0
        max_intentos = 60
        max_puntos = 4  # además del de spawn

        while len(puntos) < max_puntos + 1 and intentos < max_intentos:
            intentos += 1

            dx = random.randint(-PATROL_RADIUS_TILES, PATROL_RADIUS_TILES)
            dy = random.randint(-PATROL_RADIUS_TILES, PATROL_RADIUS_TILES)
            nx = x_tile + dx
            ny = y_tile + dy

            if not world.inside(nx, ny):
                continue

            tile = world.tiles[ny][nx]
            # solo usamos tiles donde el enemigo pueda pasar
            if not tile.puede_pasar_enemigo():
                continue

            if (nx, ny) not in puntos:
                puntos.append((nx, ny))

        return puntos

    # ---------- SET VELOCITY HACIA UN PUNTO ----------
    def _set_velocity_towards(self, tx, ty, speed_factor=1.0):
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist_sq = dx * dx + dy * dy

        if dist_sq == 0:
            self.vx = 0
            self.vy = 0
            return

        dist = math.sqrt(dist_sq)
        nx = dx / dist
        ny = dy / dist

        self.vx = nx * self.speed * speed_factor
        self.vy = ny * self.speed * speed_factor

    # ---------- ELEGIR PUNTO DE PATRULLA MÁS CERCANO ----------
    def _seleccionar_punto_patrulla_mas_cercano(self):
        if not self.patrol_points:
            self.patrol_index = 0
            return

        cx, cy = self.rect.centerx, self.rect.centery
        mejor_i = 0
        mejor_d2 = float("inf")

        for i, (tx, ty) in enumerate(self.patrol_points):
            px = tx * TILE_SIZE + TILE_SIZE // 2
            py = ty * TILE_SIZE + TILE_SIZE // 2
            dx = px - cx
            dy = py - cy
            d2 = dx*dx + dy*dy
            if d2 < mejor_d2:
                mejor_d2 = d2
                mejor_i = i

        self.patrol_index = mejor_i

    # ---------- THINK: DECIDIR ESTADO Y TARGET ----------
    def _think(self, player):
        # Distancia al jugador
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist_sq = dx * dx + dy * dy

        # Si el jugador está dentro de visión -> CHASE
        if dist_sq <= ENEMY_VISION_RADIUS ** 2:
            self.state = "chase"
            self._set_velocity_towards(player.rect.centerx, player.rect.centery, speed_factor=1.2)
            return

        # Jugador fuera de visión
        if self.state == "chase":
            # Antes estaba persiguiendo y lo perdió -> RETURN
            self.state = "return"
            self._seleccionar_punto_patrulla_mas_cercano()

        # Si tiene MUY POCA patrulla (0 o 1 punto), usar modo wander
        if len(self.patrol_points) <= 1:
            now = pygame.time.get_ticks()
            if now - self.last_dir_change > 800:
                self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                self.last_dir_change = now

            self.vx = self.dir[0] * self.speed * 0.6
            self.vy = self.dir[1] * self.speed * 0.6
            return

        # RETURN / PATROL normales con varios puntos
        tx_tile, ty_tile = self.patrol_points[self.patrol_index]
        tx = tx_tile * TILE_SIZE + TILE_SIZE // 2
        ty = ty_tile * TILE_SIZE + TILE_SIZE // 2

        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist_sq = dx * dx + dy * dy

        # Si ya está suficientemente cerca del punto -> pasar al siguiente
        if dist_sq < (4 ** 2):  # 4 píxeles
            if self.state == "return":
                self.state = "patrol"

            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
            self.vx = 0
            self.vy = 0
            return

        # sino, moverse hacia el punto de patrulla
        self._set_velocity_towards(tx, ty, speed_factor=0.7)

    # ---------- MOVIMIENTO CON COLISIÓN ----------
    def _move_axis(self, dt, world, axis):
        if axis == "x":
            if self.vx == 0:
                return
            new_px = self.px + self.vx * dt
            new_rect = self.rect.copy()
            new_rect.x = int(new_px)

            if world.can_enemy_rect_move(new_rect):
                self.px = new_px
                self.rect.x = int(self.px)
        else:  # "y"
            if self.vy == 0:
                return
            new_py = self.py + self.vy * dt
            new_rect = self.rect.copy()
            new_rect.y = int(new_py)

            if world.can_enemy_rect_move(new_rect):
                self.py = new_py
                self.rect.y = int(self.py)

    # ---------- ANIMACIÓN ----------
    def _update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > ANIM_COOLDOWN:
            self.frame_index = (self.frame_index + 1) % len(self.animation_list[self.action])
            self.last_anim_update = now
            self.image = self.animation_list[self.action][self.frame_index]

    # ---------- UPDATE GENERAL ----------
    def update(self, dt, world, player):
        self._think(player)
        self._move_axis(dt, world, "x")
        self._move_axis(dt, world, "y")

        # elegir animación según velocidad
        if self.vx == 0 and self.vy == 0:
            self.set_action(ENEMY_IDLE)
        elif abs(self.vy) >= abs(self.vx):
            if self.vy < 0:
                self.set_action(ENEMY_RUN_UP)
            else:
                self.set_action(ENEMY_RUN_DOWN)
        else:
            if self.vx < 0:
                self.set_action(ENEMY_RUN_LEFT)
            else:
                self.set_action(ENEMY_RUN_RIGHT)

        self._update_animation()

    # ---------- DIBUJO ----------
    def draw(self, surface):
        img_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, img_rect.topleft)
