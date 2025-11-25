import random
from tiles import Camino, Muro, Tunel, Liana, CAMINO, MURO, TUNEL, LIANA

TILE_SIZE = 32  # ajusta al tamaño de tus sprites

class Mapa:
    def __init__(self, ancho, alto):
        self.ancho = ancho   # en tiles
        self.alto = alto     # en tiles
        self.celdas = [[None for _ in range(ancho)] for _ in range(alto)]
        self.inicio = None
        self.salida = None

    def dentro_limites(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def get_casilla(self, x, y):
        if not self.dentro_limites(x, y):
            return None
        return self.celdas[y][x]

    def set_casilla(self, x, y, casilla):
        self.celdas[y][x] = casilla

    def _llenar_con_muros(self):
        for y in range(self.alto):
            for x in range(self.ancho):
                self.set_casilla(x, y, Muro(x, y))

    def _crear_camino_simple(self):
        """
        Crea un camino desde (0,0) hasta (ancho-1, alto-1) moviéndose
        solo derecha/abajo. Es feo pero funciona: garantiza un camino.
        """
        x, y = 0, 0
        self.inicio = (x, y)
        self.set_casilla(x, y, Camino(x, y))

        while x < self.ancho - 1 or y < self.alto - 1:
            opciones = []
            if x < self.ancho - 1:
                opciones.append("D")
            if y < self.alto - 1:
                opciones.append("B")
            mov = random.choice(opciones)
            if mov == "D":
                x += 1
            else:
                y += 1
            self.set_casilla(x, y, Camino(x, y))

        self.salida = (x, y)

    def generar_mapa(self):
        """Llenar todo con muros y luego crear un camino y rellenar el resto al azar."""
        self._llenar_con_muros()
        self._crear_camino_simple()

        for y in range(self.alto):
            for x in range(self.ancho):
                if (x, y) == self.inicio or (x, y) == self.salida:
                    continue
                if isinstance(self.get_casilla(x, y), Camino):
                    continue

                tipo = random.choice([CAMINO, MURO, TUNEL, LIANA])
                if tipo == CAMINO:
                    self.set_casilla(x, y, Camino(x, y))
                elif tipo == MURO:
                    self.set_casilla(x, y, Muro(x, y))
                elif tipo == TUNEL:
                    self.set_casilla(x, y, Tunel(x, y))
                elif tipo == LIANA:
                    self.set_casilla(x, y, Liana(x, y))

    def dibujar(self, surface, tile_sprites):
        import pygame  # evitar dependencia circular
        for y in range(self.alto):
            for x in range(self.ancho):
                casilla = self.get_casilla(x, y)
                codigo = casilla.get_codigo()
                imagen = tile_sprites[codigo]
                surface.blit(imagen, (x * TILE_SIZE, y * TILE_SIZE))
