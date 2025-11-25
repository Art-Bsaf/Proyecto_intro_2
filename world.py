import random
from tiles import *

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

    # ---------- LABERINTO DFS ----------
    def _generar_laberinto_dfs(self):
        """
        Genera un laberinto usando DFS sobre una rejilla.
        Usamos solo celdas con coordenadas impares como "nodos" para tener pasillos de 1 tile.
        """

        # 1. llenar TODO con muros
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, Muro(x, y))

        # 2. elegir celda de inicio (1,1) si cabe, si no, (0,0)
        if self.width > 2 and self.height > 2:
            sx, sy = 1, 1
        else:
            sx, sy = 0, 0

        self.start = (sx, sy)
        self.set_tile(sx, sy, Camino(sx, sy))

        stack = [(sx, sy)]
        visited = set([(sx, sy)])

        # movimientos de 2 en 2 para dejar muros entre medio
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]

        while stack:
            x, y = stack[-1]

            vecinos_no_visitados = []
            for dx, dy in dirs:
                nx = x + dx
                ny = y + dy
                if 0 < nx < self.width-1 and 0 < ny < self.height-1:
                    if (nx, ny) not in visited:
                        vecinos_no_visitados.append((nx, ny, dx, dy))

            if vecinos_no_visitados:
                nx, ny, dx, dy = random.choice(vecinos_no_visitados)
                # celda entre medio
                mx = x + dx // 2
                my = y + dy // 2

                # tallamos el pasillo
                self.set_tile(mx, my, Camino(mx, my))
                self.set_tile(nx, ny, Camino(nx, ny))

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        # 3. elegir fin cerca de la esquina inferior derecha
        ex, ey = self.width - 2, self.height - 2
        if not isinstance(self.tiles[ey][ex], Camino):
            # si no es camino, lo convertimos y conectamos a algún vecino camino
            self.set_tile(ex, ey, Camino(ex, ey))
            # intentar conectar con algún vecino
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = ex + dx, ey + dy
                if self.inside(nx, ny) and isinstance(self.tiles[ny][nx], Camino):
                    # ya está conectado por contigüidad
                    break

        self.end = (ex, ey)

    # ---------- AJUSTE DE TÚNELES Y LIANAS ----------
    def _ajustar_tuneles_y_lianas(self):
        """Asegura que túneles y lianas tengan muros a los lados y no se peguen horizontalmente."""
        from tiles import Tunel, Liana, Camino, Muro

        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]

                if isinstance(tile, Tunel) or isinstance(tile, Liana):
                    # Revisar izquierda y derecha
                    for dx in (-1, 1):
                        nx = x + dx
                        if not self.inside(nx, y):
                            continue

                        vecino = self.tiles[y][nx]

                        # Si es camino, no lo tocamos (para no romper el camino principal)
                        if isinstance(vecino, Camino):
                            continue

                        # De lo contrario, forzamos MURO
                        self.tiles[y][nx] = Muro(nx, y)

    # ---------- GENERACIÓN COMPLETA ----------
    def generate(self):
        # 1. Generar laberinto completo de CAMINOS / MUROS
        self._generar_laberinto_dfs()

        # 2. Convertir algunos caminos en TÚNEL o LIANA
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == self.start or (x, y) == self.end:
                    continue

                tile = self.tiles[y][x]
                if isinstance(tile, Camino):
                    r = random.random()
                    # ajusta estos porcentajes como quieras
                    if r < 0.05:
                        self.set_tile(x, y, Tunel(x, y))
                    elif r < 0.10:
                        self.set_tile(x, y, Liana(x, y))

        # 3. Ajustar túneles y lianas para que queden tipo "pasillo vertical"
        self._ajustar_tuneles_y_lianas()

    # ---------- COLISIONES ----------
    def can_player_move_to(self, x, y):
        """Devuelve True si el jugador puede entrar en (x, y)."""
        if not self.inside(x, y):
            return False
        tile = self.tiles[y][x]
        return tile.puede_pasar_jugador()
    
    def can_player_rect_move(self, rect):
        """Chequea si el centro del rectángulo cae en una casilla donde el jugador puede pasar."""
        tile_x = rect.centerx // TILE_SIZE
        tile_y = rect.centery // TILE_SIZE

        if not self.inside(tile_x, tile_y):
            return False

        tile = self.tiles[tile_y][tile_x]
        return tile.puede_pasar_jugador()
    
    def get_tile_at_rect_center(self, rect):
        tile_x = rect.centerx // TILE_SIZE
        tile_y = rect.centery // TILE_SIZE
        if not self.inside(tile_x, tile_y):
            return None
        return self.tiles[tile_y][tile_x]

    # ---------- DIBUJO ----------
    def draw(self, surface, sprites):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                code = tile.get_codigo()
                image = sprites[code]

                screen_x = x * TILE_SIZE
                screen_y = y * TILE_SIZE

                surface.blit(image, (screen_x, screen_y))
