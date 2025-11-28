import pygame
import random

from world import *
from tiles import *
from player import *
from enemy import *
from constants import *


# ---------- TRAMPA SENCILLA ----------
class Trap:
    def __init__(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.rect = pygame.Rect(
            tile_x * TILE_SIZE,
            tile_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )


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
    """Dibuja HEART_COUNT corazones, cada uno con HEART_HP de vida."""
    x0 = 10
    y0 = 10
    img_full = hearts_sprites["full"]
    spacing = img_full.get_width() + 4

    for i in range(HEART_COUNT):
        heart_hp = current_hp - i * HEART_HP

        if heart_hp >= HEART_HP:
            img = hearts_sprites["full"]
        elif heart_hp > 0:
            img = hearts_sprites["half"]
        else:
            img = hearts_sprites["empty"]

        screen.blit(img, (x0 + i * spacing, y0))


def draw_energy(screen, energy_frames, current_energy):
    # current_energy es float 0..MAX_ENERGY
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


def draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time):
    draw_hearts(screen, hearts_sprites, player.hp)
    draw_energy(screen, energy_frames, player.energy)

    # texto con score y tiempo
    txt = font.render(f"Score: {score}  Tiempo: {elapsed_time:.1f}s", True, (255, 255, 255))
    screen.blit(txt, (SCREEN_WIDTH - 260, 10))


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
    font = pygame.font.SysFont(None, 24)

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

    # ----- Trampas, respawn y score -----
    traps = []
    trap_cooldown = 0.0
    respawn_queue = []   # lista de tiempos absolutos (segundos) para respawn
    score = 0
    start_time = pygame.time.get_ticks() / 1000.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - start_time

        # EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    # intentar colocar trampa
                    if trap_cooldown <= 0 and len(traps) < MAX_TRAPS:
                        tile_x = player.collision_rect.centerx // TILE_SIZE
                        tile_y = player.collision_rect.centery // TILE_SIZE
                        traps.append(Trap(tile_x, tile_y))
                        trap_cooldown = TRAP_COOLDOWN

        # cooldown de trampas
        if trap_cooldown > 0:
            trap_cooldown -= dt
            if trap_cooldown < 0:
                trap_cooldown = 0

        # INPUT
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        scale_x = SCREEN_WIDTH  / render_w
        scale_y = SCREEN_HEIGHT / render_h

        player.handle_input(keys, mouse_pos, scale_x, scale_y)

        # UPDATE
        player.move(dt, world)
        for enemy in enemies:
            enemy.update(dt, world, player)

        # COLISIÓN JUGADOR–ENEMIGO
        for enemy in enemies:
            if player.hitbox_rect.colliderect(enemy.hitbox_rect):
                player.take_damage(1)

        # COLISIÓN ENEMIGO–TRAMPA
        enemies_to_kill = []
        traps_to_remove = []

        for enemy in enemies:
            for trap in traps:
                if enemy.hitbox_rect.colliderect(trap.rect):
                    enemies_to_kill.append(enemy)
                    traps_to_remove.append(trap)
                    score += SCORE_TRAP_KILL

        enemies_to_kill = list(set(enemies_to_kill))
        traps_to_remove = list(set(traps_to_remove))

        for enemy in enemies_to_kill:
            if enemy in enemies:
                enemies.remove(enemy)
                respawn_queue.append(current_time + ENEMY_RESPAWN_TIME)

        for trap in traps_to_remove:
            if trap in traps:
                traps.remove(trap)

        # REAPARECER ENEMIGOS PROGRAMADOS
        new_respawn_queue = []
        for t_respawn in respawn_queue:
            if current_time >= t_respawn:
                # crear nuevo enemigo en casilla válida
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemy = Enemy(x, y, enemy_animations, world)
                        enemies.append(enemy)
                        break
            else:
                new_respawn_queue.append(t_respawn)
        respawn_queue = new_respawn_queue

        # MUERTE → reiniciar run
        if player.is_dead():
            world = World(world_w, world_h)
            world.generate()

            tile_sprites = load_tiles()

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

            traps = []
            respawn_queue = []
            trap_cooldown = 0.0
            score = 0
            start_time = pygame.time.get_ticks() / 1000.0

        # VICTORIA: llegar a la SALIDA
        tile_bajo = world.get_tile_at_rect_center(player.collision_rect)
        from tiles import Salida
        if isinstance(tile_bajo, Salida):
            # nuevo laberinto, resetea run pero podrías guardar mejor score
            world = World(world_w, world_h)
            world.generate()

            tile_sprites = load_tiles()

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

            traps = []
            respawn_queue = []
            trap_cooldown = 0.0
            score = 0
            start_time = pygame.time.get_ticks() / 1000.0

        # DRAW en superficie pequeña
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        # DIBUJAR TRAMPAS (placeholder verde)
        for trap in traps:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((0, 255, 0, 120))
            render_surface.blit(s, (trap.tile_x * TILE_SIZE, trap.tile_y * TILE_SIZE))

        # ESCALAR
        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        # HUD encima
        draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
