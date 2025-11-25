from abc import ABC, abstractmethod

CAMINO = 0
MURO = 1
TUNEL = 2
LIANA = 3

class Casilla(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abstractmethod
    def puede_pasar_jugador(self):
        pass

    @abstractmethod
    def puede_pasar_enemigo(self):
        pass

    @abstractmethod
    def get_codigo(self):
        """Número que representa el tipo de casilla."""
        pass


class Camino(Casilla):
    def puede_pasar_jugador(self):
        return True

    def puede_pasar_enemigo(self):
        return True

    def get_codigo(self):
        return CAMINO


class Muro(Casilla):
    def puede_pasar_jugador(self):
        return False

    def puede_pasar_enemigo(self):
        return False

    def get_codigo(self):
        return MURO


class Tunel(Casilla):
    def puede_pasar_jugador(self):
        return True

    def puede_pasar_enemigo(self):
        return False

    def get_codigo(self):
        return TUNEL


class Liana(Casilla):
    def puede_pasar_jugador(self):
        return False

    def puede_pasar_enemigo(self):
        return True

    def get_codigo(self):
        return LIANA
