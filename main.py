import pygame
from world import Mapa, TILE_SIZE
from tiles import CAMINO, MURO, TUNEL, LIANA

ANCHO_TILES = 20
ALTO_TILES = 15

def cargar_sprites():
    sprites = {}
    sprites[CAMINO] = pygame.image.load(r"assets\tiles\1.png").convert_alpha()
    sprites[MURO]   = pygame.image.load(r"assets\tiles\7.png").convert_alpha()
    sprites[TUNEL]  = pygame.image.load(r"assets\tiles\8.png").convert_alpha()
    sprites[LIANA]  = pygame.image.load(r"assets\Mage-Red\idle\0.png").convert_alpha()

    # opcional: escalar al tamaño definido
    for key, img in sprites.items():
        sprites[key] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    return sprites

def main():
    pygame.init()

    ancho_px = ANCHO_TILES * TILE_SIZE
    alto_px = ALTO_TILES * TILE_SIZE

    pantalla = pygame.display.set_mode((ancho_px, alto_px))
    pygame.display.set_caption("Mapa - Proyecto Intro")

    clock = pygame.time.Clock()

    # crear mapa
    mapa = Mapa(ANCHO_TILES, ALTO_TILES)
    mapa.generar_mapa()

    # cargar sprites
    tile_sprites = cargar_sprites()

    corriendo = True
    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    corriendo = False

        pantalla.fill((0, 0, 0))
        mapa.dibujar(pantalla, tile_sprites)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
