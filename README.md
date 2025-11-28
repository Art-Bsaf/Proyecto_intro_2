# 🧩 Proyecto 2: Escapa del Laberinto / Cazador

Este proyecto es la implementación de un juego 2D de laberinto desarrollado en Python y Pygame, donde el mapa se genera proceduralmente para asegurar la re-jugabilidad.

El proyecto incluye dos modos de juego principales:
1.  **Modo Escapa:** El jugador debe huir de los cazadores y alcanzar la salida.
2.  **Modo Cazador:** El jugador debe atrapar a los enemigos antes de que escapen.

---

## 🛠️ Requisitos de Ejecución e Instalación

Para ejecutar el juego, necesitas tener instalado **Python 3.x** y la librería **Pygame**.

### 1. Clona el Repositorio

Asegúrate de clonar el código en tu máquina local:

git clone [TU ENLACE DE GITHUB]

cd [NOMBRE DE LA CARPETA DEL PROYECTO]

### Instalar Librería
Instala Pygame usando pip: pip install pygame

### 3. Ejecutar el Juego
Inicia el juego desde la línea de comandos ejecutando el archivo principal:

### 4🕹️ Guía de Controles y Mecánicas
El juego utiliza un sistema de movimiento basado en tiles con física de colisiones deslizantes.

## Controles Generales
Acción,Tecla,Efecto
Movimiento,"W, A, S, D o Flechas",Desplazamiento del personaje.
Correr/Sprint,SHIFT (mantener),"Aumenta la velocidad, pero consume energía."
Ayuda,H,Muestra/Oculta la pantalla de ayuda con las reglas.
Salir,ESC,Sale del juego.

### 5 Tipos de Terreno
## El mapa se compone de cuatro tipos de casillas:
Terreno,Jugador,Enemigos
Camino,✅ Pasa,✅ Pasa
Muros,❌ Bloquea,❌ Bloquea
Túneles,✅ Pasa,❌ Bloquea
Lianas,❌ Bloquea,✅ Pasa

### 6 Mecánica de Modos

Modo,Objetivo Principal,Mecánica Única
Escapa,Llegar a la Salida sin morir.,El jugador puede colocar Trampas (ESPACIO) para eliminar a los cazadores temporalmente.
Cazador,Atrapar al mayor número de enemigos.,Los enemigos huyen del jugador y buscan la salida. Se gana por atrapar y se pierden puntos por cada enemigo que escapa.

### 7 ⚙️ Estructura del Código

## El proyecto utiliza un diseño Modular basado en la Programación Orientada a Objetos (POO).

Archivo,Responsabilidad Principal,Algoritmos Clave
main.py,"Bucle de juego, UI, gestión de modos y score.",
world.py,"Generación del laberinto, mapa (tiles) y colisiones.",DFS (Depth-First Search) para generar laberinto.
tiles.py,"Definición de clases de terreno (Casilla, Muro, Tunel, Liana).",Herencia y Polimorfismo en las reglas de paso.
enemy.py,Lógica de la IA (Patrulla/Persecución/Huida).,Álgebra Vectorial para el movimiento en tiempo real.
player.py,"Física de movimiento, vida, energía y manejo de input.",
constants.py,"Almacenamiento de variables globales de configuración (velocidad, tamaño de mapa, etc.).",

# Para un análisis técnico completo, incluyendo el Diagrama de Clases UML, consulte el documento adjunto: Documentación de Proyecto Escapa del Laberinto y Cazador.pdf