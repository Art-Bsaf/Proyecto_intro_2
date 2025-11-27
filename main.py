import pygame
import random

from world import *
from tiles import *
from player import *
from enemy import *
from constants import *

# ---------- TILES ----------
def load_tiles():
    sprites = {}
    sprites[CAMINO] = pygame.image.load("assets/tiles/1.png").convert_alpha()
    sprites[MURO]   = pygame.image.load("assets/tiles/7.png").convert_alpha()
    sprites[TUNEL]  = pygame.image.load("assets/tiles/8.png").convert_alpha()
    sprites[LIANA]  = pygame.image.load("assets/tiles/0.png").convert_alpha()
    sprites[SALIDA] = pygame.image.load("assets/tiles/9.png").convert_alpha()

    for k, img in sprites.items():
        sprites[k] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    return sprites

# ---------- ANIMACIONES JUGADOR ----------
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


# ---------- ANIMACIONES ENEMIGOS ----------
def load_enemy_animations(folder_name):
    animation_list = []

    anims = [
        "idle",
        "running_up",
        "running_down",
        "running_left",
        "running_right"
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


# ---------- HUD: CORAZONES Y ENERGÍA ----------
def load_hearts_sprites():
    hearts = {}

    hearts["full"]  = pygame.image.load("assets/hearts/0.png").convert_alpha()
    hearts["half"]  = pygame.image.load("assets/hearts/1.png").convert_alpha()
    hearts["empty"] = pygame.image.load("assets/hearts/2.png").convert_alpha()

    return hearts


def load_energy_frames():
    frames = []
    for i in range(ENERGY_FRAMES):
        img = pygame.image.load(f"assets/energy/{i}.png").convert_alpha()
        frames.append(img)
    return frames


def draw_hearts(screen, hearts_sprites, current_hp):
    """Dibuja 3 corazones, cada uno con 2 HP."""
    x0 = 10
    y0 = 10
    img_full = hearts_sprites["full"]
    spacing = img_full.get_width() + 4

    for i in range(HEART_COUNT):
        heart_hp = current_hp - i * HEART_HP  # hp que le queda a este corazón

        if heart_hp >= 2:
            img = hearts_sprites["full"]
        elif heart_hp == 1:
            img = hearts_sprites["half"]
        else:
            img = hearts_sprites["empty"]

        screen.blit(img, (x0 + i * spacing, y0))


def draw_energy(screen, energy_frames, current_energy):
    """
    current_energy va de 0..MAX_ENERGY (0 vacío, MAX_ENERGY lleno o al revés, tú decides).
    Aquí asumo: 0 = lleno, MAX_ENERGY = vacío.
    """
    # invertimos: 0 energía -> último frame, full energía -> frame 0
    pct = current_energy / MAX_ENERGY if MAX_ENERGY > 0 else 0
    idx = int((1 - pct) * (ENERGY_FRAMES - 1))

    if idx < 0:
        idx = 0
    if idx >= ENERGY_FRAMES:
        idx = ENERGY_FRAMES - 1

    img = energy_frames[idx]

    x = 10
    y = 10 + img.get_height() + 8  # debajo de corazones
    screen.blit(img, (x, y))


def draw_hud(screen, hearts_sprites, energy_frames, player):
    draw_hearts(screen, hearts_sprites, player.hp)
    draw_energy(screen, energy_frames, player.energy)

def draw_energy(screen, energy_frames, current_energy):
    """
    current_energy va de 0..MAX_ENERGY.
    0 = lleno, MAX_ENERGY = vacío.
    """
    pct = current_energy / MAX_ENERGY if MAX_ENERGY > 0 else 0
    idx = int((1 - pct) * (ENERGY_FRAMES - 1))

    if idx < 0:
        idx = 0
    if idx >= ENERGY_FRAMES:
        idx = ENERGY_FRAMES - 1

    img = energy_frames[idx]

    x = 10
    y = 10 + img.get_height() + 8
    screen.blit(img, (x, y))

    


# ---------- MAIN ----------
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

    # ----- Animaciones -----
    player_animations = load_player_animations("player")
    enemy_animations = load_enemy_animations("enemies")

    # ----- HUD -----
    hearts_sprites = load_hearts_sprites()
    energy_frames = load_energy_frames()

    # ----- Jugador -----
    start_x, start_y = world.start
    player = Player(start_x, start_y, player_animations)

    # ----- Enemigos -----
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
        mouse_pos = pygame.mouse.get_pos()

        scale_x = SCREEN_WIDTH  / (world_w * TILE_SIZE)
        scale_y = SCREEN_HEIGHT / (world_h * TILE_SIZE)

        player.handle_input(keys, mouse_pos, scale_x, scale_y)

        # UPDATE
        player.move(dt, world)
        for enemy in enemies:
            enemy.update(dt, world, player)

        # COLISIÓN JUGADOR–ENEMIGO (cada toque = medio corazón)
        for enemy in enemies:
            if player.hitbox_rect.colliderect(enemy.hitbox_rect):
                player.take_damage(1)

        # MUERTE → reiniciar laberinto
        if player.is_dead():
            world = World(world_w, world_h)
            world.generate()

            start_x, start_y = world.start
            player = Player(start_x, start_y, player_animations)

            enemies = []
            for _ in range(NUM_ENEMIES):
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemy = Enemy(x, y, enemy_animations, world)
                        enemies.append(enemy)
                        break

        # VICTORIA: llegar a la SALIDA
        tile_bajo = world.get_tile_at_rect_center(player.collision_rect)
        from tiles import Salida
        if isinstance(tile_bajo, Salida):
            # nuevo laberinto, resetea hp/energía
            world = World(world_w, world_h)
            world.generate()

            start_x, start_y = world.start
            player = Player(start_x, start_y, player_animations)

            enemies = []
            for _ in range(NUM_ENEMIES):
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemy = Enemy(x, y, enemy_animations, world)
                        enemies.append(enemy)
                        break

        # DRAW en superficie pequeña
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        # ESCALAR
        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        # HUD encima
        draw_hud(screen, hearts_sprites, energy_frames, player)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
