import pygame
import os
import random

from world import *
from tiles import *
from player import *
from constants import *
from enemy import *

PLAYER_SCALE = 2

# ============================================
# 1) LOAD TILES 
# ============================================
def load_tiles():
    sprites = {}
    # Rutas simples, relativas al proyecto
    sprites[CAMINO] = pygame.image.load("assets/tiles/1.png").convert_alpha()
    sprites[MURO]   = pygame.image.load("assets/tiles/7.png").convert_alpha()
    sprites[TUNEL]  = pygame.image.load("assets/tiles/8.png").convert_alpha()
    sprites[LIANA]  = pygame.image.load("assets/tiles/0.png").convert_alpha()
    sprites[SALIDA] = pygame.image.load("assets/tiles/9.png").convert_alpha()

    for k, img in sprites.items():
        sprites[k] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    return sprites

def load_player_animations(folder_name):
    animation_list = []

    anims = [
        "idle",          # 0
        "running_up",    # 1
        "running_down",  # 2
        "running_left",  # 3
        "running_right"  # 4
    ]

    for anim_name in anims:
        frames = []
        for i in range(4):   # 0,1,2,3
            path = f"assets/{folder_name}/{anim_name}/{i}.png"
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(
                img, (TILE_SIZE * PLAYER_SCALE, TILE_SIZE * PLAYER_SCALE)
            )
            frames.append(img)

        animation_list.append(frames)

    return animation_list


def load_enemy_animations(folder_name):
    animation_list = []

    anims = [
        "idle",          # 0
        "running_up",    # 1
        "running_down",  # 2
        "running_left",  # 3
        "running_right"  # 4
    ]

    for anim_name in anims:
        frames = []
        for i in range(4):
            path = f"assets/{folder_name}/{anim_name}/{i}.png"
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(
                img, (TILE_SIZE * PLAYER_SCALE, TILE_SIZE * PLAYER_SCALE)
            )
            frames.append(img)

        animation_list.append(frames)

    return animation_list


# ============================================
# 3) MAIN LOOP
# ============================================
def main():
    pygame.init()

    world_w = 20
    world_h = 15

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    render_w = world_w * TILE_SIZE
    render_h = world_h * TILE_SIZE
    render_surface = pygame.Surface((render_w, render_h))

    pygame.display.set_caption("Proyecto Laberinto")
    
    clock = pygame.time.Clock()

    # ----- Mapa -----
    world = World(world_w, world_h)
    world.generate()

    # ----- Tiles -----
    tile_sprites = load_tiles()

    # ----- Animaciones jugador -----
    player_animations = load_player_animations("player")

    # ----- Crear jugador -----
    start_x, start_y = world.start
    player = Player(start_x, start_y, player_animations)

    # ----- Enemigos -----
    enemy_animations = load_enemy_animations("enemies")
    enemies = []
    NUM_ENEMIES = 6

    for _ in range(NUM_ENEMIES):
        while True:
            x = random.randrange(world.width)
            y = random.randrange(world.height)
            tile = world.tiles[y][x]

            if tile.puede_pasar_enemigo():
                enemy = Enemy(x, y, enemy_animations, world)
                enemies.append(enemy)
                break

    # ----- LOOP -----
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # INPUT
        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        # UPDATE
        player.move(dt, world)

        for enemy in enemies:
            enemy.update(dt, world, player)

        # DRAW en superficie pequeña
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        # ESCALAR
        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
