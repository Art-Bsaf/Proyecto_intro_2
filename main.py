import pygame
import random
import os

from world import World
from tiles import CAMINO, MURO, TUNEL, LIANA, SALIDA, Salida
from player import Player
from enemy import Enemy
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


# ---------- GESTIÓN DE SCORES ----------
def load_scores(mode=None):
    """Si mode = 'ESCAPA' o 'CAZADOR', devuelve solo esos.
       Si mode = None → devuelve todos (pero ya no lo usaremos)."""
    scores = []
    if not os.path.exists(SCORES_FILE):
        return scores

    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) != 6:
                continue

            name, m, score, time_s, kills, traps_used = parts
            try:
                score = int(score)
                time_s = float(time_s)
                kills = int(kills)
                traps_used = int(traps_used)
            except:
                continue

            if mode is None or m == mode:
                scores.append({
                    "name": name,
                    "mode": m,
                    "score": score,
                    "time": time_s,
                    "kills": kills,
                    "traps": traps_used
                })

    return scores


def save_score(name, mode, score, elapsed_time, kills, traps_used):
    # cargar solo scores del modo indicado
    scores = load_scores(mode)

    # agregar el nuevo
    scores.append({
        "name": name,
        "mode": mode,
        "score": score,
        "time": elapsed_time,
        "kills": kills,
        "traps": traps_used
    })

    # ordenar → top 5 del modo
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:5]

    # PERO ahora debemos guardar TODOS los modos, no solo este.
    # cargamos todos, filtramos los del otro modo y luego reconstruimos.
    all_scores = load_scores(None)

    # limpiamos los del modo actual
    all_scores = [s for s in all_scores if s["mode"] != mode]

    # agregamos el top5 del modo actual
    all_scores.extend(scores)

    # ordenar archivo final (por modo y por score)
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        for s in all_scores:
            f.write(f"{s['name']};{s['mode']};{s['score']};"
                    f"{s['time']:.2f};{s['kills']};{s['traps']}\n")


def compute_final_score(elapsed_time, enemies_killed_by_trap, traps_used):
    base_time_score = int(SCORE_TIME_FACTOR / max(elapsed_time, 1.0))
    kills_score = enemies_killed_by_trap * SCORE_TRAP_KILL
    traps_penalty = traps_used * SCORE_TRAP_USED_PENALTY

    total = base_time_score + kills_score - traps_penalty
    if total < 0:
        total = 0
    return total


def get_player_name(screen, font):
    clock = pygame.time.Clock()
    name = ""
    entering = True

    while entering:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        name = "Anon"
                    entering = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    ch = event.unicode
                    if ch.isalnum() or ch == " ":
                        if len(name) < 12:
                            name += ch

        screen.fill((0, 0, 0))
        txt1 = font.render("Nombre (ENTER para confirmar):", True, (255, 255, 255))
        txt2 = font.render(name, True, (0, 255, 0))

        screen.blit(txt1, (SCREEN_WIDTH // 2 - txt1.get_width() // 2,
                           SCREEN_HEIGHT // 2 - 40))
        screen.blit(txt2, (SCREEN_WIDTH // 2 - txt2.get_width() // 2,
                           SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

    return name.strip()


def show_end_screen(screen, font, final_score, elapsed_time,
                    kills, traps_used, win):
    clock = pygame.time.Clock()

    if win:
        name = get_player_name(screen, font)
        save_score(name, "ESCAPA", final_score, elapsed_time, kills, traps_used)
    else:
        name = "-----"

    top_scores = load_scores("ESCAPA")

    showing = True
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    showing = False

        screen.fill((0, 0, 0))
        y = 40

        titulo_txt = "VICTORIA - MODO ESCAPA" if win else "DERROTA - MODO ESCAPA"
        color_titulo = (255, 255, 0) if win else (255, 80, 80)

        title = font.render(titulo_txt, True, color_titulo)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 40

        stats = [
            f"Jugador: {name}",
            f"Tiempo: {elapsed_time:.1f} s",
            f"Enemigos eliminados con trampas: {kills}",
            f"Trampas usadas: {traps_used}",
            f"Puntaje final: {final_score}",
            "",
            "TOP 5 GLOBAL:"
        ]
        for line in stats:
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, (40, y))
            y += 30

        for i, s in enumerate(top_scores):
            linea = (
                f"{i+1}. {s['name']} [{s['mode']}]  |  "
                f"Score: {s['score']}  |  T: {s['time']:.1f}s  |  "
                f"K: {s['kills']}  |  Traps: {s['traps']}"
            )
            txt = font.render(linea, True, (200, 200, 200))
            screen.blit(txt, (60, y))
            y += 24

        info = font.render("ENTER o ESC para volver al menú", True, (150, 150, 255))
        screen.blit(info,
                    (SCREEN_WIDTH // 2 - info.get_width() // 2,
                     SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)


def show_cazador_results(screen, font, score, elapsed_time, kills, exits):
    clock = pygame.time.Clock()
    running = True

    top_scores = load_scores("CAZADOR")


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    running = False

        screen.fill((0, 0, 0))
        y = 40

        title = font.render("FIN - MODO CAZADOR", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 40

        lines = [
            f"Tiempo jugado: {elapsed_time:.1f} s",
            f"Enemigos atrapados: {kills}",
            f"Enemigos que alcanzaron la salida: {exits}",
            f"Puntaje final: {score}",
            "",
            "TOP 5 GLOBAL:"
        ]
        for line in lines:
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, (40, y))
            y += 30

        for i, s in enumerate(top_scores):
            linea = (
                f"{i+1}. {s['name']} [{s['mode']}]  |  "
                f"Score: {s['score']}  |  T: {s['time']:.1f}s  |  "
                f"K: {s['kills']}  |  Traps: {s['traps']}"
            )
            txt = font.render(linea, True, (200, 200, 200))
            screen.blit(txt, (60, y))
            y += 24

        info = font.render("ENTER o ESC para volver al menú", True, (150, 150, 255))
        screen.blit(info,
                    (SCREEN_WIDTH // 2 - info.get_width() // 2,
                     SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)


# ---------- LOADERS ----------
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
        for i in range(4):
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


def load_trap_sprite():
    img = pygame.image.load("assets/tiles/2.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return img


# ---------- HUD ----------
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


def draw_hud(screen, hearts_sprites, energy_frames, player, font,
             score, elapsed_time):
    draw_hearts(screen, hearts_sprites, player.hp)
    draw_energy(screen, energy_frames, player.energy)

    txt = font.render(f"Score: {score}  Tiempo: {elapsed_time:.1f}s",
                      True, (255, 255, 255))
    screen.blit(txt, (SCREEN_WIDTH - 260, 10))


# ---------- PANELES DE AYUDA ----------
def draw_help_panel_escapa(screen, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    lines = [
        "CONTROLES - MODO ESCAPA",
        "",
        "Moverse: W / A / S / D",
        "Correr: SHIFT (consume energía)",
        "Colocar trampa: ESPACIO (máx 3, con cooldown)",
        "",
        "Objetivo:",
        "- Llegar a la salida sin morir.",
        "- Evitar a los cazadores (enemigos).",
        "- Usar trampas para eliminarlos y ganar puntos.",
        "",
        "Score final:",
        "- Depende del tiempo, enemigos eliminados por trampas",
        "  y trampas usadas.",
        "",
        "Pulsa H para reanudar."
    ]

    y = 60
    for line in lines:
        if ("CONTROLES" in line or
                "Objetivo" in line or
                "Score" in line):
            color = (255, 255, 0)
        else:
            color = (255, 255, 255)
        txt = font.render(line, True, color)
        screen.blit(txt, (60, y))
        y += 28


def draw_cazador_help_panel(screen, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    lines = [
        "MODO CAZADOR - CONTROLES Y OBJETIVO",
        "",
        "Moverse: W / A / S / D",
        "Correr: SHIFT (si lo usas, gasta energía igual que en Escapa)",
        "",
        "Objetivo:",
        "- Tienes un tiempo límite.",
        "- Atrapa la mayor cantidad posible de enemigos.",
        "- Los enemigos huyen de ti y buscan la salida.",
        "- Si un enemigo llega a la salida, pierdes puntos.",
        "",
        "Puntaje:",
        "- Cada enemigo atrapado suma CAZADOR_KILL_SCORE.",
        "- Cada enemigo que alcanza la salida resta CAZADOR_EXIT_PENALTY.",
        "- Si tu score entra en el Top 5, se actualiza el récord.",
        "",
        "Pulsa H para reanudar."
    ]

    y = 60
    for line in lines:
        if ("MODO CAZADOR" in line or
                "Objetivo" in line or
                "Puntaje" in line):
            color = (255, 255, 0)
        else:
            color = (255, 255, 255)
        txt = font.render(line, True, color)
        screen.blit(txt, (60, y))
        y += 28


# ---------- MODO ESCAPA ----------
def run_escapa(screen, font):
    clock = pygame.time.Clock()

    render_w = WORLD_W * TILE_SIZE
    render_h = WORLD_H * TILE_SIZE
    render_surface = pygame.Surface((render_w, render_h))

    player_animations = load_player_animations("player")
    enemy_animations = load_enemy_animations("enemies")
    hearts_sprites = load_hearts_sprites()
    energy_frames = load_energy_frames()
    trap_img = load_trap_sprite()

    # Mundo y estado inicial
    world = World(WORLD_W, WORLD_H)
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
                enemies.append(Enemy(x, y, enemy_animations, world))
                break

    traps = []
    trap_cooldown = 0.0
    respawn_queue = []  # tiempos para respawn de enemigos

    score = 0
    traps_used = 0
    enemies_killed_by_trap = 0

    show_help = False
    paused = False
    pause_start = 0.0

    start_time = pygame.time.get_ticks() / 1000.0

    running = True
    elapsed_time = 0.0   # <-- NUEVO

    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks() / 1000.0

        if not paused:
            elapsed_time = current_time - start_time


        # EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # volver al menú

                elif event.key == pygame.K_SPACE:
                    if trap_cooldown <= 0 and len(traps) < MAX_TRAPS:
                        tile_x = player.collision_rect.centerx // TILE_SIZE
                        tile_y = player.collision_rect.centery // TILE_SIZE
                        traps.append(Trap(tile_x, tile_y))
                        trap_cooldown = TRAP_COOLDOWN
                        traps_used += 1

                elif event.key == pygame.K_h:
                    if not show_help:
                        show_help = True
                        paused = True
                        pause_start = current_time
                    else:
                        show_help = False
                        paused = False
                        pause_duration = current_time - pause_start
                        start_time += pause_duration

        # Pausa
        if paused:
            render_surface.fill((0, 0, 0))
            world.draw(render_surface, tile_sprites)
            for trap in traps:
                render_surface.blit(trap_img,
                                    (trap.tile_x * TILE_SIZE,
                                     trap.tile_y * TILE_SIZE))
            player.draw(render_surface)
            for enemy in enemies:
                enemy.draw(render_surface)

            scaled = pygame.transform.scale(render_surface,
                                            (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled, (0, 0))
            draw_hud(screen, hearts_sprites, energy_frames, player,
                     font, score, elapsed_time)
            draw_help_panel_escapa(screen, font)
            pygame.display.flip()
            continue

        # cooldown trampas
        if trap_cooldown > 0:
            trap_cooldown -= dt
            if trap_cooldown < 0:
                trap_cooldown = 0

        # INPUT
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        scale_x = SCREEN_WIDTH / render_w
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
                    enemies_killed_by_trap += 1

        enemies_to_kill = list(set(enemies_to_kill))
        traps_to_remove = list(set(traps_to_remove))

        for enemy in enemies_to_kill:
            if enemy in enemies:
                enemies.remove(enemy)
                respawn_queue.append(current_time + ENEMY_RESPAWN_TIME)

        for trap in traps_to_remove:
            if trap in traps:
                traps.remove(trap)

        # REAPARECER ENEMIGOS
        new_respawn_queue = []
        for t_respawn in respawn_queue:
            if current_time >= t_respawn:
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemies.append(Enemy(x, y, enemy_animations, world))
                        break
            else:
                new_respawn_queue.append(t_respawn)
        respawn_queue = new_respawn_queue

        # MUERTE → derrota
        if player.is_dead():
            final_score = compute_final_score(
                elapsed_time,
                enemies_killed_by_trap,
                traps_used
            )
            show_end_screen(screen, font, final_score, elapsed_time,
                            enemies_killed_by_trap, traps_used, win=False)
            return

        # VICTORIA → llegar a la salida
        tile_bajo = world.get_tile_at_rect_center(player.collision_rect)
        if isinstance(tile_bajo, Salida):
            final_score = compute_final_score(
                elapsed_time,
                enemies_killed_by_trap,
                traps_used
            )
            show_end_screen(screen, font, final_score, elapsed_time,
                            enemies_killed_by_trap, traps_used, win=True)
            return

        # DIBUJO
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)

        # trampas
        for trap in traps:
            render_surface.blit(trap_img,
                                (trap.tile_x * TILE_SIZE,
                                 trap.tile_y * TILE_SIZE))

        player.draw(render_surface)

        for enemy in enemies:
            enemy.draw(render_surface)

        scaled = pygame.transform.scale(render_surface,
                                        (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        draw_hud(screen, hearts_sprites, energy_frames, player,
                 font, score, elapsed_time)

        pygame.display.flip()


# ---------- MODO CAZADOR ----------
def run_cazador(screen, font):
    clock = pygame.time.Clock()

    render_w = WORLD_W * TILE_SIZE
    render_h = WORLD_H * TILE_SIZE
    render_surface = pygame.Surface((render_w, render_h))

    player_animations = load_player_animations("player")
    enemy_animations = load_enemy_animations("enemies")
    hearts_sprites = load_hearts_sprites()
    energy_frames = load_energy_frames()

    world = World(WORLD_W, WORLD_H)
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
                enemies.append(Enemy(x, y, enemy_animations, world))
                break

    score = 0
    kills = 0
    exits = 0

    TIME_LIMIT = CAZADOR_TIME_LIMIT
    start_time = pygame.time.get_ticks() / 1000.0

    show_help = False
    paused = False
    pause_start = 0.0

    running = True
    elapsed_time = 0.0   # <-- NUEVO

    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks() / 1000.0

        if not paused:
            elapsed_time = current_time - start_time


        # EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # volver al menú

                elif event.key == pygame.K_h:
                    if not show_help:
                        show_help = True
                        paused = True
                        pause_start = current_time
                    else:
                        show_help = False
                        paused = False
                        pause_duration = current_time - pause_start
                        start_time += pause_duration

        if paused:
            render_surface.fill((0, 0, 0))
            world.draw(render_surface, tile_sprites)
            player.draw(render_surface)
            for enemy in enemies:
                enemy.draw(render_surface)

            scaled = pygame.transform.scale(render_surface,
                                            (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled, (0, 0))
            draw_hud(screen, hearts_sprites, energy_frames, player,
                     font, score, elapsed_time)
            draw_cazador_help_panel(screen, font)
            pygame.display.flip()
            continue

        # INPUT
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        scale_x = SCREEN_WIDTH / render_w
        scale_y = SCREEN_HEIGHT / render_h
        player.handle_input(keys, mouse_pos, scale_x, scale_y)

        # UPDATE
        player.move(dt, world)
        for enemy in enemies:
            enemy.update_cazador(dt, world, player)

        # JUGADOR atrapa enemigo
        for enemy in list(enemies):
            if player.hitbox_rect.colliderect(enemy.hitbox_rect):
                kills += 1
                score += CAZADOR_KILL_SCORE
                enemies.remove(enemy)
                # respawn
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemies.append(Enemy(x, y, enemy_animations, world))
                        break

        # ENEMIGOS que llegan a la salida
        for enemy in list(enemies):
            tile_enemy = world.get_tile_at_rect_center(enemy.collision_rect)
            if isinstance(tile_enemy, Salida):
                exits += 1
                score -= CAZADOR_EXIT_PENALTY
                enemies.remove(enemy)
                # respawn
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemies.append(Enemy(x, y, enemy_animations, world))
                        break

        # fin por tiempo
        if elapsed_time >= TIME_LIMIT:
            name = get_player_name(screen, font)
            save_score(name, "CAZADOR", score, elapsed_time, kills, 0)
            show_cazador_results(screen, font, score, elapsed_time, kills, exits)
            return

        # DIBUJO
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))

        # HUD genérico (vidas, energía, score, tiempo jugado)
        draw_hud(screen, hearts_sprites, energy_frames, player,
                 font, score, elapsed_time)

        # TIEMPO RESTANTE específico de MODO CAZADOR
        time_left = max(0, TIME_LIMIT - elapsed_time)
        txt_time = font.render(f"Tiempo restante: {time_left:4.1f}s", True, (255, 255, 0))
        screen.blit(txt_time, (SCREEN_WIDTH - 260, 30))

        pygame.display.flip()



# ---------- MENÚ PRINCIPAL ----------
def show_main_menu(screen, font):
    clock = pygame.time.Clock()
    selected = 0  # 0 = Escapa, 1 = Cazador, 2 = Salir
    options = ["MODO ESCAPA", "MODO CAZADOR", "SALIR"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return selected

        screen.fill((0, 0, 0))

        title = font.render("ESCAPA DEL LABERINTO", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        y = 120
        for i, txt in enumerate(options):
            color = (255, 255, 255)
            if i == selected:
                color = (0, 255, 0)
            rtxt = font.render(txt, True, color)
            screen.blit(rtxt, (SCREEN_WIDTH // 2 - rtxt.get_width() // 2, y))
            y += 40

        # info de modos
        y += 10
        lines = [
            "Controles generales: W/A/S/D para moverse, SHIFT para correr.",
            "ESC para salir, H para ver/ocultar la ayuda en cada modo.",
            "",
            "MODO ESCAPA:",
            "- Objetivo: llegar a la salida sin morir.",
            "- Los cazadores te persiguen.",
            "- Puedes colocar trampas (ESPACIO) para eliminarlos.",
            "",
            "MODO CAZADOR:",
            "- Objetivo: en tiempo límite atrapar el máximo de enemigos.",
            "- Los enemigos huyen de ti y buscan la salida.",
            "- Si llegan a la salida pierdes puntos; si los cazas, ganas puntos."
        ]
        for line in lines:
            col = (255, 255, 255)
            if "ESCAPA" in line or "CAZADOR" in line:
                col = (255, 255, 0)
            t = font.render(line, True, col)
            screen.blit(t, (40, y))
            y += 24

        pygame.display.flip()
        clock.tick(60)


# ---------- MAIN ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Proyecto Laberinto")
    font = pygame.font.SysFont(None, 24)

    while True:
        opcion = show_main_menu(screen, font)
        if opcion == 0:
            run_escapa(screen, font)
        elif opcion == 1:
            run_cazador(screen, font)
        else:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
