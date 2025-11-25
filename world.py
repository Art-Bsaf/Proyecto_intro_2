import random
from tiles import Camino, Muro, Tunel, Liana, CAMINO, MURO, TUNEL, LIANA

TILE_SIZE = 32  # ajusta al tamaño real de tus sprites

class World:
    def __init__(self, width, height):
        self.width = width      # en tiles
        self.height = height    # en tiles
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        self.start = None
        self.end = None

    def inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def set_tile(self, x, y, tile):
        self.tiles[y][x] = tile

    def generate(self):
        # Llenar todo con muros
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, Muro(x, y))

        # Crear camino garantizado de (0,0) a (width-1, height-1)
        x, y = 0, 0
        self.start = (x, y)
        self.set_tile(x, y, Camino(x, y))

        while x < self.width - 1 or y < self.height - 1:
            moves = []
            if x < self.width - 1:
                moves.append("D")
            if y < self.height - 1:
                moves.append("B")
            move = random.choice(moves)
            if move == "D":
                x += 1
            else:
                y += 1
            self.set_tile(x, y, Camino(x, y))

        self.end = (x, y)

        # Rellenar el resto al azar
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in (self.start, self.end):
                    continue
                if isinstance(self.tiles[y][x], Camino):
                    continue

                t = random.choice([CAMINO, MURO, TUNEL, LIANA])

                if t == CAMINO:
                    self.set_tile(x, y, Camino(x, y))
                elif t == MURO:
                    self.set_tile(x, y, Muro(x, y))
                elif t == TUNEL:
                    self.set_tile(x, y, Tunel(x, y))
                elif t == LIANA:
                    self.set_tile(x, y, Liana(x, y))

    def draw(self, surface, sprites):
        import pygame
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                code = tile.get_codigo()
                image = sprites[code]
                surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
