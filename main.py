import pygame
import random
import os

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


# ---------- GESTIÓN DE SCORES (MODO ESCAPA) ----------
def load_scores():
    scores = []
    if not os.path.exists(SCORES_FILE):
        return scores

    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) != 6:
                continue
            name, mode, score_str, time_str, kills_str, traps_str = parts
            try:
                score = int(score_str)
                time_s = float(time_str)
                kills = int(kills_str)
                traps = int(traps_str)
            except ValueError:
                continue
            scores.append({
                "name": name,
                "mode": mode,
                "score": score,
                "time": time_s,
                "kills": kills,
                "traps": traps
            })
    return scores


def save_score(name, mode, score, elapsed_time, kills, traps_used):
    scores = load_scores()
    scores.append({
        "name": name,
        "mode": mode,
        "score": score,
        "time": elapsed_time,
        "kills": kills,
        "traps": traps_used
    })

    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:5]

    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        for s in scores:
            line = f"{s['name']};{s['mode']};{s['score']};{s['time']:.2f};{s['kills']};{s['traps']}\n"
            f.write(line)


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

        screen.blit(txt1, (SCREEN_WIDTH // 2 - txt1.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(txt2, (SCREEN_WIDTH // 2 - txt2.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

    return name.strip()


def show_end_screen(screen, font, final_score, elapsed_time, kills, traps_used, win, mode_label):
    clock = pygame.time.Clock()

    if win:
        name = get_player_name(screen, font)
        save_score(name, mode_label, final_score, elapsed_time, kills, traps_used)
    else:
        name = "-----"

    top_scores = load_scores()
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
        titulo_txt = f"{'VICTORIA' if win else 'DERROTA'} - MODO {mode_label}"
        color_titulo = (255, 255, 0) if win else (255, 80, 80)

        title = font.render(titulo_txt, True, color_titulo)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 40

        stats = [
            f"Jugador: {name if win else '-----'}",
            f"Tiempo: {elapsed_time:.1f} s",
            f"Enemigos eliminados con trampas: {kills}",
            f"Trampas usadas: {traps_used}",
            f"Puntaje final: {final_score}",
            "",
            "TOP 5:"
        ]

        for line in stats:
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, (40, y))
            y += 30

        for i, s in enumerate(top_scores):
            line = f"{i+1}. {s['name']} [{s['mode']}]  |  Score: {s['score']}  |  T: {s['time']:.1f}s  |  K: {s['kills']}  |  Traps: {s['traps']}"
            txt = font.render(line, True, (200, 200, 200))
            screen.blit(txt, (60, y))
            y += 24

        info = font.render("ENTER o ESC para volver al menú", True, (150, 150, 255))
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)


# ---------- CARGA DE RECURSOS ----------
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
    anims = ["idle", "running_up", "running_down", "running_left", "running_right"]
    for anim_name in anims:
        frames = []
        for i in range(4):
            path = f"assets/{folder_name}/{anim_name}/{i}.png"
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE * PLAYER_SCALE, TILE_SIZE * PLAYER_SCALE))
            frames.append(img)
        animation_list.append(frames)
    return animation_list


def load_enemy_animations(folder_name):
    animation_list = []
    anims = ["idle", "running_up", "running_down", "running_left", "running_right"]
    for anim_name in anims:
        frames = []
        for i in range(4):
            path = f"assets/{folder_name}/{anim_name}/{i}.png"
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE_SIZE * PLAYER_SCALE, TILE_SIZE * PLAYER_SCALE))
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
    idx = max(0, min(idx, ENERGY_FRAMES - 1))
    img = energy_frames[idx]
    x = 10
    y = 10 + img.get_height() + 8
    screen.blit(img, (x, y))


def draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time):
    draw_hearts(screen, hearts_sprites, player.hp)
    draw_energy(screen, energy_frames, player.energy)
    txt = font.render(f"Score: {score}  Tiempo: {elapsed_time:.1f}s", True, (255, 255, 255))
    screen.blit(txt, (SCREEN_WIDTH - 260, 10))


def draw_help_panel(screen, font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    lines = [
        "CONTROLES - MODO ESCAPA",
        "",
        "Moverse: W / A / S / D",
        "Correr: mantener SHIFT (consume energía)",
        "Colocar trampa: ESPACIO (máx 3, con cooldown)",
        "",
        "Objetivo:",
        "- Llegar a la salida evitando a los enemigos.",
        "- Las trampas matan enemigos y dan puntaje.",
        "- Si la vida llega a 0, pierdes.",
        "",
        "Score final:",
        "- Depende del tiempo, enemigos eliminados y trampas usadas.",
        "",
        "Pulsa H para cerrar esta ayuda."
    ]

    y = 60
    for line in lines:
        color = (255, 255, 0) if "CONTROLES" in line or "Objetivo" in line or "Score" in line else (255, 255, 255)
        txt = font.render(line, True, color)
        screen.blit(txt, (60, y))
        y += 28


# ---------- MODO ESCAPA ----------
def run_escapa(screen, font):
    pygame.display.set_caption("Proyecto Laberinto - Modo Escapa")

    render_w = WORLD_W * TILE_SIZE
    render_h = WORLD_H * TILE_SIZE
    render_surface = pygame.Surface((render_w, render_h))

    clock = pygame.time.Clock()

    player_animations = load_player_animations("player")
    enemy_animations = load_enemy_animations("enemies")
    hearts_sprites = load_hearts_sprites()
    energy_frames = load_energy_frames()
    trap_img = load_trap_sprite()

    world = None
    tile_sprites = None
    player = None
    enemies = []
    traps = []
    trap_cooldown = 0.0
    respawn_queue = []
    score = 0
    start_time = 0.0
    traps_used = 0
    enemies_killed_by_trap = 0
    show_help = False
    elapsed_time = 0.0

    def reset_run():
        nonlocal world, tile_sprites, player, enemies
        nonlocal traps, trap_cooldown, respawn_queue
        nonlocal score, start_time, traps_used, enemies_killed_by_trap, show_help, elapsed_time

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
                    enemy = Enemy(x, y, enemy_animations, world)
                    enemies.append(enemy)
                    break

        traps = []
        trap_cooldown = 0.0
        respawn_queue = []
        score = 0
        start_time = pygame.time.get_ticks() / 1000.0
        traps_used = 0
        enemies_killed_by_trap = 0
        show_help = False
        elapsed_time = 0.0

    reset_run()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # volver al menú

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
                    show_help = not show_help

        # PAUSA: si está activa, no actualizar nada salvo dibujar
        if show_help:
            render_surface.fill((0, 0, 0))
            world.draw(render_surface, tile_sprites)

            for trap in traps:
                render_surface.blit(trap_img, (trap.tile_x * TILE_SIZE, trap.tile_y * TILE_SIZE))

            player.draw(render_surface)

            for enemy in enemies:
                enemy.draw(render_surface)

            scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled, (0, 0))
            draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time)
            draw_help_panel(screen, font)
            pygame.display.flip()
            continue


        elapsed_time += dt

        if trap_cooldown > 0:
            trap_cooldown -= dt
            if trap_cooldown < 0:
                trap_cooldown = 0

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        scale_x = SCREEN_WIDTH / render_w
        scale_y = SCREEN_HEIGHT / render_h

        player.handle_input(keys, mouse_pos, scale_x, scale_y)
        player.move(dt, world)

        for enemy in enemies:
            enemy.update(dt, world, player)

        # daño por contacto
        for enemy in enemies:
            if player.hitbox_rect.colliderect(enemy.hitbox_rect):
                player.take_damage(1)

        # trampas
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

        # respawn enemigos
        new_respawn_queue = []
        for t_respawn in respawn_queue:
            if current_time >= t_respawn:
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

        # muerte
        if player.is_dead():
            final_score = compute_final_score(elapsed_time, enemies_killed_by_trap, traps_used)
            show_end_screen(screen, font, final_score, elapsed_time, enemies_killed_by_trap, traps_used, win=False, mode_label="ESCAPA")
            reset_run()
            continue

        # victoria
        tile_bajo = world.get_tile_at_rect_center(player.collision_rect)
        from tiles import Salida
        if isinstance(tile_bajo, Salida):
            final_score = compute_final_score(elapsed_time, enemies_killed_by_trap, traps_used)
            show_end_screen(screen, font, final_score, elapsed_time, enemies_killed_by_trap, traps_used, win=True, mode_label="ESCAPA")
            reset_run()
            continue

        # DRAW
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        for trap in traps:
            render_surface.blit(trap_img, (trap.tile_x * TILE_SIZE, trap.tile_y * TILE_SIZE))
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time)
        pygame.display.flip()


# ---------- MODO CAZADOR ----------
def show_cazador_results(screen, font, score, elapsed_time, kills, exits):
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    running = False

        screen.fill((0, 0, 0))
        y = 60
        title = font.render("FIN - MODO CAZADOR", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 40

        lines = [
            f"Tiempo jugado: {elapsed_time:.1f} s",
            f"Enemigos atrapados: {kills}",
            f"Enemigos que alcanzaron la salida: {exits}",
            f"Puntaje final: {score}",
            "",
            "ENTER o ESC para volver al menú"
        ]
        for line in lines:
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, (60, y))
            y += 30

        pygame.display.flip()
        clock.tick(60)


def run_cazador(screen, font):
    pygame.display.set_caption("Proyecto Laberinto - Modo Cazador")

    render_w = WORLD_W * TILE_SIZE
    render_h = WORLD_H * TILE_SIZE
    render_surface = pygame.Surface((render_w, render_h))

    clock = pygame.time.Clock()

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
                enemy = Enemy(x, y, enemy_animations, world)
                enemies.append(enemy)
                break

    score = 0
    kills = 0
    exits = 0
    elapsed_time = 0.0
    TIME_LIMIT = 60.0  # 1 minuto, ajusta si quieres

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        scale_x = SCREEN_WIDTH / render_w
        scale_y = SCREEN_HEIGHT / render_h

        player.handle_input(keys, mouse_pos, scale_x, scale_y)
        player.move(dt, world)

        for enemy in enemies:
            enemy.update_cazador(dt, world, player)


        # si jugador toca enemigo -> lo atrapa
        for enemy in enemies[:]:
            if player.hitbox_rect.colliderect(enemy.hitbox_rect):
                kills += 1
                score += CAZADOR_KILL_SCORE
                enemies.remove(enemy)
                # respawn inmediato
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemies.append(Enemy(x, y, enemy_animations, world))
                        break

        # si enemigo llega a salida -> penalización
        for enemy in enemies:
            tile_bajo = world.get_tile_at_rect_center(enemy.collision_rect)
            if isinstance(tile_bajo, Salida):
                exits += 1
                score -= CAZADOR_EXIT_PENALTY
                if score < 0:
                    score = 0
                # respawn enemigo
                while True:
                    x = random.randrange(world.width)
                    y = random.randrange(world.height)
                    tile = world.tiles[y][x]
                    if tile.puede_pasar_enemigo():
                        enemy.collision_rect.x = x * TILE_SIZE
                        enemy.collision_rect.y = y * TILE_SIZE
                        enemy.px = float(enemy.collision_rect.x)
                        enemy.py = float(enemy.collision_rect.y)
                        enemy.hitbox_rect.midbottom = enemy.collision_rect.midbottom
                        break

        # fin por tiempo
        if elapsed_time >= TIME_LIMIT:
            show_cazador_results(screen, font, score, elapsed_time, kills, exits)
            return

        # DRAW
        render_surface.fill((0, 0, 0))
        world.draw(render_surface, tile_sprites)
        player.draw(render_surface)
        for enemy in enemies:
            enemy.draw(render_surface)

        scaled = pygame.transform.scale(render_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        draw_hud(screen, hearts_sprites, energy_frames, player, font, score, elapsed_time)
        pygame.display.flip()


# ---------- MENÚ PRINCIPAL ----------
def show_menu(screen, font):
    clock = pygame.time.Clock()
    selecting = True
    option = None

    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "QUIT"
                if event.key == pygame.K_1:
                    return "ESCAPA"
                if event.key == pygame.K_2:
                    return "CAZADOR"
                if event.key == pygame.K_3:
                    return "AYUDA"

        screen.fill((0, 0, 0))
        title = font.render("PROYECTO 2 - ESCAPA DEL LABERINTO", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        l1 = font.render("1 - Modo Escapa", True, (255, 255, 255))
        l2 = font.render("2 - Modo Cazador", True, (255, 255, 255))
        l3 = font.render("3 - Controles", True, (255, 255, 255))
        l4 = font.render("ESC - Salir", True, (200, 200, 200))
        l5 = font.render("Más adelante: música y opciones aquí", True, (150, 150, 255))

        screen.blit(l1, (100, 180))
        screen.blit(l2, (100, 220))
        screen.blit(l3, (100, 260))
        screen.blit(l4, (100, 320))
        screen.blit(l5, (100, 360))

        pygame.display.flip()
        clock.tick(60)


# ---------- MAIN ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        mode = show_menu(screen, font)
        if mode == "QUIT":
            running = False
        elif mode == "ESCAPA":
            run_escapa(screen, font)
        elif mode == "CAZADOR":
            run_cazador(screen, font)
        elif mode == "AYUDA":
            draw_help_panel(screen, font)

    pygame.quit()


if __name__ == "__main__":
    main()
