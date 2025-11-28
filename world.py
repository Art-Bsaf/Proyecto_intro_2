import random
from tiles import *

TILE_SIZE = 32

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # matriz de tiles
        self.tiles = [[None for _ in range(width)] for _ in range(height)]

        self.start = None
        self.end = None

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------
    def inside(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def set_tile(self, x, y, tile):
        self.tiles[y][x] = tile

    # ------------------------------------------------------------
    # LABERINTO POR DFS
    # ------------------------------------------------------------
    def _generar_laberinto_dfs(self):
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, Muro(x, y))

        # 2. Punto inicial
        if self.width > 2 and self.height > 2:
            sx, sy = 1, 1
        else:
            sx, sy = 0, 0

        self.start = (sx, sy)
        self.set_tile(sx, sy, Camino(sx, sy))

        stack = [(sx, sy)]
        visited = {(sx, sy)}

        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]

        while stack:
            x, y = stack[-1]

            vecinos = []
            for dx, dy in dirs:
                nx = x + dx
                ny = y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if (nx, ny) not in visited:
                        vecinos.append((nx, ny, dx, dy))

            if vecinos:
                nx, ny, dx, dy = random.choice(vecinos)
                mx = x + dx // 2
                my = y + dy // 2

                self.set_tile(mx, my, Camino(mx, my))
                self.set_tile(nx, ny, Camino(nx, ny))

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()


        ex, ey = self.width - 2, self.height - 2
        self.end = (ex, ey)
        self.set_tile(ex, ey, Camino(ex, ey))

    # ------------------------------------------------------------
    # TÚNELES Y LIANAS EN MUROS
    # ------------------------------------------------------------
    def _generar_tuneles_y_lianas(self):
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):

                if (x, y) == self.start or (x, y) == self.end:
                    continue

                tile = self.tiles[y][x]

                if not isinstance(tile, Muro):
                    continue

                arriba = self.tiles[y - 1][x]
                abajo = self.tiles[y + 1][x]

                if isinstance(arriba, Camino) and isinstance(abajo, Camino):
                    r = random.random()
                    if r < 0.06:
                        self.set_tile(x, y, Tunel(x, y))
                    elif r < 0.12:
                        self.set_tile(x, y, Liana(x, y))

    # ------------------------------------------------------------
    # GENERACIÓN COMPLETA DEL MUNDO
    # ------------------------------------------------------------
    def generate(self):
        self._generar_laberinto_dfs()

        ex, ey = self.end
        self.set_tile(ex, ey, Salida(ex, ey))

        self._generar_tuneles_y_lianas()

    # ------------------------------------------------------------
    # COLISIONES
    # ------------------------------------------------------------
    def can_player_rect_move(self, rect):
        tile_x = rect.centerx // TILE_SIZE
        tile_y = rect.centery // TILE_SIZE

        if not self.inside(tile_x, tile_y):
            return False

        return self.tiles[tile_y][tile_x].puede_pasar_jugador()

    def can_enemy_rect_move(self, rect):
        tile_x = rect.centerx // TILE_SIZE
        tile_y = rect.centery // TILE_SIZE

        if not self.inside(tile_x, tile_y):
            return False

        return self.tiles[tile_y][tile_x].puede_pasar_enemigo()

    def get_tile_at_rect_center(self, rect):
        tile_x = rect.centerx // TILE_SIZE
        tile_y = rect.centery // TILE_SIZE
        if not self.inside(tile_x, tile_y):
            return None
        return self.tiles[tile_y][tile_x]

    # ------------------------------------------------------------
    # DIBUJO
    # ------------------------------------------------------------
    def draw(self, surface, sprites):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                img = sprites[tile.get_codigo()]
                surface.blit(img, (x * TILE_SIZE, y * TILE_SIZE))
