import pygame
from world import TILE_SIZE
from constants import *
import math


class Player:
    def __init__(self, x_tile, y_tile, animation_list, speed=120):
        # posición en píxeles (top-left de la hitbox, NO del sprite)
        self.px = x_tile * TILE_SIZE
        self.py = y_tile * TILE_SIZE

        self.animation_list = animation_list
        self.action = ANIM_IDLE
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.action][self.frame_index]

        # rect de COLISIÓN: tamaño exacto de un tile
        self.rect = pygame.Rect(self.px, self.py, TILE_SIZE, TILE_SIZE)

        # movimiento
        self.vx = 0.0
        self.vy = 0.0
        self.speed = speed  # px por segundo

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.image = self.animation_list[self.action][self.frame_index]

    def _update_animation(self):
        animation_cooldown = 100  # ms

        current_time = pygame.time.get_ticks()

        # Si está quieto, solo mira al mouse
        if self.action == ANIM_IDLE:
            self.update_idle()
            return

        # Si está moviéndose, animación normal
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time

            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

            self.image = self.animation_list[self.action][self.frame_index]


            # Para animaciones de movimiento, sí avanzamos frames
            if current_time - self.update_time > animation_cooldown:
                self.frame_index += 1
                self.update_time = current_time

                if self.frame_index >= len(self.animation_list[self.action]):
                    self.frame_index = 0

                self.image = self.animation_list[self.action][self.frame_index]

    def handle_input(self, keys):
        vx = 0
        vy = 0

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

        if vx == 0 and vy == 0:
            # quieto → estado idle (la anim se maneja en _update_animation)
            self.set_action(ANIM_IDLE)
        elif vy < 0:
            self.set_action(ANIM_RUN_UP)
        elif vy > 0:
            self.set_action(ANIM_RUN_DOWN)
        elif vx < 0:
            self.set_action(ANIM_RUN_LEFT)
        elif vx > 0:
            self.set_action(ANIM_RUN_RIGHT)

    def _move_axis(self, dt, world, axis):
        if axis == "x":
            if self.vx == 0:
                return
            new_px = self.px + self.vx * dt
            new_rect = self.rect.copy()
            new_rect.x = int(new_px)

            if world.can_player_rect_move(new_rect):
                self.px = new_px
                self.rect.x = int(self.px)
        else:  # "y"
            if self.vy == 0:
                return
            new_py = self.py + self.vy * dt
            new_rect = self.rect.copy()
            new_rect.y = int(new_py)

            if world.can_player_rect_move(new_rect):
                self.py = new_py
                self.rect.y = int(self.py)

    def move(self, dt, world):
        # movimiento por píxeles
        self._move_axis(dt, world, "x")
        self._move_axis(dt, world, "y")
        # animación (incluye mirar al mouse en idle)
        self._update_animation()

    # ----------- MIRAR HACIA EL MOUSE CUANDO ESTÁ IDLE -----------
    def update_idle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.rect.center

        dx = mouse_x - px
        dy = mouse_y - py

        # Determina si el movimiento es más horizontal o vertical
        if abs(dx) > abs(dy):  # mirar izquierda/derecha
            if dx > 0:
                self.image = self.animation_list[ANIM_RUN_RIGHT][0]
            else:
                self.image = self.animation_list[ANIM_RUN_LEFT][0]
        else:  # mirar arriba/abajo
            if dy > 0:
                self.image = self.animation_list[ANIM_RUN_DOWN][0]
            else:
                self.image = self.animation_list[ANIM_RUN_UP][0]

    def draw(self, surface):
        image_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, image_rect.topleft)
