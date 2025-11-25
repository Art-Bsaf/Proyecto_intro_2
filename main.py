import pygame
import os
from world import *
from tiles import *
from player import *
from constants import *




PLAYER_SCALE = 2

BASE = os.path.dirname(__file__)

# ============================================
# 1) LOAD TILES (ya lo tienes, queda igual)
# ============================================
def load_tiles():
    sprites = {}
    sprites[CAMINO] = pygame.image.load(os.path.join(BASE, "assets", "tiles", "1.png")).convert_alpha()
    sprites[MURO]   = pygame.image.load(os.path.join(BASE, "assets", "tiles", "7.png")).convert_alpha()
    sprites[TUNEL]  = pygame.image.load(os.path.join(BASE, "assets", "tiles", "8.png")).convert_alpha()
    sprites[LIANA]  = pygame.image.load(os.path.join(BASE, "assets", "tiles", "0.png")).convert_alpha()

    for k, img in sprites.items():
        sprites[k] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    return sprites

# ============================================
# 2) LOAD PLAYER ANIMATIONS  (NUEVO - PEGAR AQUÍ)
# ============================================

def load_animation_folder(subfolder):
    frames = []
    i = 0
    while True:
        path = os.path.join(BASE, "assets", "Mage-Red", subfolder, f"{i}.png")
        if not os.path.exists(path):
            break
        img = pygame.image.load(path).convert_alpha()
        

        img = pygame.transform.scale(img, (TILE_SIZE * PLAYER_SCALE, TILE_SIZE * PLAYER_SCALE))
        frames.append(img)
        i += 1

    if not frames:
        raise RuntimeError(f"No se encontraron frames en {subfolder}")

    return frames

def load_player_animations():
    animation_list = []

    # 0 - IDLE
    idle_frames = load_animation_folder("idle")
    animation_list.append(idle_frames)

    # 1 - RUN UP
    run_up = load_animation_folder("running_up")
    animation_list.append(run_up)

    # 2 - RUN DOWN
    run_down = load_animation_folder("running_down")
    animation_list.append(run_down)

    # 3 - RUN LEFT
    run_left = load_animation_folder("running_left")
    animation_list.append(run_left)

    # 4 - RUN RIGHT
    run_right = load_animation_folder("running_right")
    animation_list.append(run_right)

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

    # ----- Tiles y Animaciones -----
    tile_sprites = load_tiles()
    player_animations = load_player_animations()
    


    # ----- Crear jugador (NUEVO) -----
    start_x, start_y = world.start
    player = Player(start_x, start_y, player_animations)

    # ----- LOOP -----
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

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

        # DRAW en superficie pequeña
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)

        # ESCALAR A LA PANTALLA
        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
