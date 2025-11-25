import pygame
from world import World, TILE_SIZE
from tiles import CAMINO, MURO, TUNEL, LIANA
import os

BASE = os.path.dirname(__file__)

print("BASE =", BASE)
print("Contenido de BASE:", os.listdir(BASE))
print("Contenido de assets:", os.listdir(os.path.join(BASE, "assets")))
print("Contenido de tiles:", os.listdir(os.path.join(BASE, "assets", "tiles")))


def load_sprites():
    sprites = {}

    path_camino = os.path.join(BASE, "assets", "tiles", "1.png")
    print("Ruta CAMINO =", path_camino)
    print("Existe CAMINO? ->", os.path.exists(path_camino))

    sprites[CAMINO] = pygame.image.load(path_camino).convert_alpha()
    sprites[MURO]   = pygame.image.load(os.path.join(BASE, "assets", "tiles", "7.png")).convert_alpha()
    sprites[TUNEL]  = pygame.image.load(os.path.join(BASE, "assets", "tiles", "8.png")).convert_alpha()
    sprites[LIANA]  = pygame.image.load(os.path.join(BASE, "assets", "Mage-Red", "idle", "0.png")).convert_alpha()

    for k, img in sprites.items():
        sprites[k] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    return sprites


def main():
    pygame.init()

    world_w = 20
    world_h = 15

    screen = pygame.display.set_mode((world_w*TILE_SIZE, world_h*TILE_SIZE))
    pygame.display.set_caption("Mapa del Proyecto")

    clock = pygame.time.Clock()

    world = World(world_w, world_h)
    world.generate()

    sprites = load_sprites()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        world.draw(screen, sprites)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
