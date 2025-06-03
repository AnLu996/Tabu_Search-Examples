import pygame
import random
from collections import deque

# Constantes (las tuyas)
VACIO = 0
OBSTACULO = 1
INICIO = 2
META = 3
CAMINO = 4
TABU = 5  # Nuevo: para mostrar la lista tabú visualmente

FILAS = 40
COLUMNAS = 60
TAM_CELDA = 15

COLORES = {
    VACIO: (255, 255, 255),
    OBSTACULO: (0, 0, 0),
    INICIO: (0, 255, 0),
    META: (0, 0, 255),
    CAMINO: (255, 0, 0),
    TABU: (255, 165, 0)  # naranja para tabú
}

# Aquí sólo el método de búsqueda Tabú
def busqueda_tabu_visual(laberinto, pantalla, clock):
    filas = len(laberinto)
    columnas = len(laberinto[0])
    destino = (filas - 1, columnas - 1)

    # Estado inicial
    actual = (0, 0)
    padre = {}
    visitado = set()
    visitado.add(actual)
    lista_tabu = deque(maxlen=50)  # tamaño fijo para lista tabú

    while actual != destino:
        vecinos = []
        x, y = actual

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < filas and 0 <= ny < columnas:
                if laberinto[nx][ny] != OBSTACULO and (nx, ny) not in lista_tabu:
                    vecinos.append((nx, ny))

        if not vecinos:
            # No hay vecinos válidos => retrocedemos o terminamos
            if actual in padre:
                actual = padre[actual]
            else:
                print("No se encontró solución.")
                break
        else:
            # Elegir el vecino más cercano al destino (heurística Manhattan)
            vecinos.sort(key=lambda pos: abs(destino[0]-pos[0]) + abs(destino[1]-pos[1]))
            siguiente = vecinos[0]

            padre[siguiente] = actual
            actual = siguiente
            visitado.add(actual)

            # Añadir a lista tabú
            lista_tabu.append(actual)

        # Visualización en pygame
        for i in range(filas):
            for j in range(columnas):
                tipo = laberinto[i][j]
                color = COLORES.get(tipo, (255,255,255))
                rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(pantalla, color, rect)

        # Dibujar la lista tabú
        for tx, ty in lista_tabu:
            rect = pygame.Rect(ty*TAM_CELDA, tx*TAM_CELDA, TAM_CELDA, TAM_CELDA)
            pygame.draw.rect(pantalla, COLORES[TABU], rect)

        # Dibujar el camino recorrido hasta ahora
        for (cx, cy) in visitado:
            if laberinto[cx][cy] not in (INICIO, META):
                rect = pygame.Rect(cy*TAM_CELDA, cx*TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(pantalla, (200, 0, 0), rect)

        pygame.display.flip()
        clock.tick(15)  # Controlar velocidad

    # Reconstruir camino final
    if actual == destino:
        camino = []
        while actual != (0, 0):
            camino.append(actual)
            actual = padre[actual]
        camino.append((0, 0))
        camino.reverse()

        for (cx, cy) in camino:
            if laberinto[cx][cy] not in (INICIO, META):
                laberinto[cx][cy] = CAMINO

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((COLUMNAS*TAM_CELDA, FILAS*TAM_CELDA))
    pygame.display.set_caption("Búsqueda Tabú en Laberinto")
    clock = pygame.time.Clock()

    # Genera laberinto simple (usa tu generador)
    laberinto = [[VACIO for _ in range(COLUMNAS)] for _ in range(FILAS)]
    laberinto[0][0] = INICIO
    laberinto[FILAS-1][COLUMNAS-1] = META

    # Añade obstáculos aleatorios
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if random.random() < 0.3 and laberinto[i][j] == VACIO:
                laberinto[i][j] = OBSTACULO

    corriendo = True
    buscando = True

    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        if buscando:
            busqueda_tabu_visual(laberinto, pantalla, clock)
            buscando = False

        # Dibuja el laberinto final con el camino
        for i in range(FILAS):
            for j in range(COLUMNAS):
                tipo = laberinto[i][j]
                color = COLORES.get(tipo, (255, 255, 255))
                rect = pygame.Rect(j * TAM_CELDA, i * TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(pantalla, color, rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
