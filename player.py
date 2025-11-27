import pygame
from math import atan2, degrees

from constants import *


class Player:
    def __init__(self, x_tile, y_tile, animation_list, speed=120):
        self.animation_list = animation_list
        self.action = ANIM_RUN_DOWN          # por defecto mirar hacia abajo
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.action][self.frame_index]

        # ---------- CAJA VERDE: COLISIÓN (UN TILE ENTERO) ----------
        cx = x_tile * TILE_SIZE
        cy = y_tile * TILE_SIZE
        self.collision_rect = pygame.Rect(cx, cy, TILE_SIZE, TILE_SIZE)

        # posición flotante para movimiento suave
        self.px = float(self.collision_rect.x)
        self.py = float(self.collision_rect.y)

        # ---------- CAJA ROJA: HITBOX (MÁS PEQUEÑA ADENTRO) ----------
        shrink = int(TILE_SIZE * 0.3)  # reduce ancho/alto
        self.hitbox_rect = self.collision_rect.inflate(-shrink, -shrink)

        # movimiento
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = speed    # velocidad normal
        self.speed = speed         # velocidad actual (se modifica si hace sprint)
        self.want_sprint = False   # si el jugador está intentando sprintar

        # STATS
        self.hp = MAX_HEALTH        # 0..6 (3 corazones, medio por golpe)
        self.energy = MAX_ENERGY    # 0..8 (niveles de energía)
        self.invuln_timer = 0.0     # tiempo de invulnerabilidad tras golpe (segundos)

        # dirección de mirada (arriba/abajo/izq/der)
        self.facing_action = ANIM_RUN_DOWN

        self.base_speed = speed
        self.speed = speed
        self.want_sprint = False

        # ...
        self.invuln_timer = 0.0

        # cooldown de sprint cuando vacías la energía
        self.sprint_lock_timer = 0.0

    # ---------- ANIMACIONES ----------
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.image = self.animation_list[self.action][self.frame_index]

    def _update_animation(self):
        animation_cooldown = 100  # ms

        # si está quieto → no animamos, solo mostramos frame 0 mirando en self.facing_action
        if self.vx == 0 and self.vy == 0:
            # acción = la dirección de mirada
            if self.action != self.facing_action:
                self.action = self.facing_action
                self.frame_index = 0
            self.image = self.animation_list[self.action][0]
            return

        # si se está moviendo → animación normal
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time

            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

            self.image = self.animation_list[self.action][self.frame_index]

    # ---------- INPUT ----------
    def handle_input(self, keys, mouse_pos=None, scale_x=1.0, scale_y=1.0):
        vx = 0
        vy = 0

        # --- MOVIMIENTO POR TECLAS ---
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy = 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx = 1

        self.vx = vx * self.speed
        self.vy = vy * self.speed
        self.want_sprint = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # 1) SI SE MUEVE → dirección según movimiento
        if vx != 0 or vy != 0:
            # decide si domina X o Y
            if abs(vx) > abs(vy):
                if vx > 0:
                    move_action = ANIM_RUN_RIGHT
                else:
                    move_action = ANIM_RUN_LEFT
            else:
                if vy > 0:
                    move_action = ANIM_RUN_DOWN
                else:
                    move_action = ANIM_RUN_UP

            self.facing_action = move_action
            self.set_action(move_action)
            return

        # 2) SI ESTÁ QUIETO → mirar hacia el mouse (sin caminar)
        if mouse_pos is None:
            # si no tenemos mouse, se queda mirando como esté
            return

        mx_screen, my_screen = mouse_pos

        # convertir mouse (pantalla) a coords del render_surface
        mx = mx_screen / scale_x
        my = my_screen / scale_y

        px = self.collision_rect.centerx
        py = self.collision_rect.centery

        dx = mx - px
        dy = my - py

        if dx == 0 and dy == 0:
            return

        # ángulo en grados: 0 = derecha, 90 = arriba, -90 = abajo
        angle = degrees(atan2(-dy, dx))

        # mapping de ángulos a direcciones
        if -45 <= angle <= 45:
            self.facing_action = ANIM_RUN_RIGHT
        elif 45 < angle <= 135:
            self.facing_action = ANIM_RUN_UP
        elif -135 <= angle < -45:
            self.facing_action = ANIM_RUN_DOWN
        else:
            self.facing_action = ANIM_RUN_LEFT

        # no usamos anim de correr; la animación se congelará en frame 0 en _update_animation
        self.set_action(self.facing_action)

    # ---------- MOVIMIENTO CON COLISIÓN ----------
    def _move_axis(self, dt, world, axis):
        if axis == "x":
            if self.vx == 0:
                return
            new_px = self.px + self.vx * dt
            new_rect = self.collision_rect.copy()
            new_rect.x = int(new_px)

            if world.can_player_rect_move(new_rect):
                self.px = new_px
                self.collision_rect.x = int(self.px)
        else:
            if self.vy == 0:
                return
            new_py = self.py + self.vy * dt
            new_rect = self.collision_rect.copy()
            new_rect.y = int(new_py)

            if world.can_player_rect_move(new_rect):
                self.py = new_py
                self.collision_rect.y = int(self.py)

        # hitbox roja sigue a la verde
        self.hitbox_rect.center = self.collision_rect.center

    def move(self, dt, world):
        # ---------- TIMERS ----------
        # cooldown de sprint
        if self.sprint_lock_timer > 0:
            self.sprint_lock_timer -= dt
            if self.sprint_lock_timer < 0:
                self.sprint_lock_timer = 0

        # invulnerabilidad de daño
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            if self.invuln_timer < 0:
                self.invuln_timer = 0

        # ---------- SPRINT Y ENERGÍA ----------
        moving = (self.vx != 0 or self.vy != 0)
        can_sprint = (self.sprint_lock_timer == 0 and self.energy > 0)

        if self.want_sprint and moving and can_sprint:
            # activar sprint
            self.speed = self.base_speed * SPRINT_MULT
            self.energy -= ENERGY_DRAIN_PER_SEC * dt

            # si la vaciamos, bloqueamos el sprint
            if self.energy <= 0:
                self.energy = 0
                self.sprint_lock_timer = SPRINT_LOCK_TIME
        else:
            # sin sprint -> velocidad normal
            self.speed = self.base_speed
            # regenerar energía si no está llena
            if self.energy < MAX_ENERGY:
                self.energy += ENERGY_REGEN_PER_SEC * dt
                if self.energy > MAX_ENERGY:
                    self.energy = MAX_ENERGY

        # ---------- MOVIMIENTO ----------
        self._move_axis(dt, world, "x")
        self._move_axis(dt, world, "y")
        self._update_animation()


    # ---------- VIDA / ENERGÍA ----------
    def take_damage(self, amount):
        # si está invulnerable, ignorar
        if self.invuln_timer > 0:
            return

        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

        # activar cooldown de daño
        self.invuln_timer = DAMAGE_COOLDOWN


    def is_dead(self):
        return self.hp <= 0

    def heal_full(self):
        self.hp = MAX_HEALTH

    def use_energy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0

    def regen_energy(self, amount):
        self.energy += amount
        if self.energy > MAX_ENERGY:
            self.energy = MAX_ENERGY

    # ---------- DIBUJAR ----------
    def draw(self, surface):
        image_rect = self.image.get_rect(midbottom=self.collision_rect.midbottom)
        surface.blit(self.image, image_rect.topleft)
        # debug opcional:
        # pygame.draw.rect(surface, (0, 255, 0), self.collision_rect, 1)
        # pygame.draw.rect(surface, (255, 0, 0), self.hitbox_rect, 1)
