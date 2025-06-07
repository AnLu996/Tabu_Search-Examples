import pygame
import random
from collections import deque

# Constantes
VACIO = 0
OBSTACULO = 1
INICIO = 2
META = 3
CAMINO = 4
TABU = 5
VISITADO = 6

FILAS = 20
COLUMNAS = 30
TAM_CELDA = 25

COLORES = {
    VACIO: (255, 255, 255),
    OBSTACULO: (0, 0, 0),
    INICIO: (0, 255, 0),
    META: (0, 0, 255),
    CAMINO: (255, 0, 0),
    TABU: (255, 165, 0), 
    VISITADO: (200, 200, 200)  
}

def generar_laberinto_con_camino():
    laberinto = [[VACIO for _ in range(COLUMNAS)] for _ in range(FILAS)]
    
    # Colocar inicio y meta cercanos (pero no adyacentes)
    inicio = (random.randint(0, FILAS//2), random.randint(0, COLUMNAS//2))
    meta = (
        min(inicio[0] + random.randint(3, FILAS//3), FILAS-1),
        min(inicio[1] + random.randint(3, COLUMNAS//3), COLUMNAS-1)
    )
    
    laberinto[inicio[0]][inicio[1]] = INICIO
    laberinto[meta[0]][meta[1]] = META
    
    # Asegurar un camino directo (con algunos obstáculos)
    for i in range(min(inicio[0], meta[0]), max(inicio[0], meta[0]) + 1):
        for j in range(min(inicio[1], meta[1]), max(inicio[1], meta[1]) + 1):
            if laberinto[i][j] == VACIO and random.random() < 0.2:  # Menos obstáculos en el camino probable
                laberinto[i][j] = OBSTACULO
    
    # Añadir obstáculos aleatorios en el resto del laberinto
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if laberinto[i][j] == VACIO and random.random() < 0.3:
                laberinto[i][j] = OBSTACULO
    
    return laberinto, inicio, meta

def busqueda_tabu_visual(laberinto, pantalla, clock, inicio, meta):
    filas = len(laberinto)
    columnas = len(laberinto[0])
    
    # Estado inicial
    actual = inicio
    padre = {}
    visitado = set()
    visitado.add(actual)
    lista_tabu = deque(maxlen=20)  # tamaño más pequeño para mejor visualización
    
    # Heurística: distancia Manhattan
    def heuristica(pos):
        return abs(meta[0] - pos[0]) + abs(meta[1] - pos[1])
    
    while actual != meta:
        vecinos = []
        x, y = actual
        
        # Generar vecinos válidos
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < filas and 0 <= ny < columnas:
                if laberinto[nx][ny] != OBSTACULO and (nx, ny) not in lista_tabu:
                    vecinos.append((nx, ny))
        
        if not vecinos:
            # No hay vecinos válidos - retroceder
            if actual in padre:
                lista_tabu.append(actual)  # Añadir a lista tabú para no volver
                actual = padre[actual]
            else:
                print("No se encontró solución.")
                return False
        else:
            # Elegir el mejor vecino según heurística
            vecinos.sort(key=heuristica)
            siguiente = vecinos[0]
            
            # Actualizar estructuras
            padre[siguiente] = actual
            actual = siguiente
            visitado.add(actual)
            
            # Añadir a lista tabú para no volver inmediatamente
            lista_tabu.append(actual)
        
        # Visualización
        pantalla.fill((255, 255, 255))
        
        # Dibujar laberinto
        for i in range(filas):
            for j in range(columnas):
                tipo = laberinto[i][j]
                color = COLORES.get(tipo, (255, 255, 255))
                rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(pantalla, color, rect)
        
        # Dibujar visitados
        for (i, j) in visitado:
            if laberinto[i][j] not in (INICIO, META):
                rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
                pygame.draw.rect(pantalla, COLORES[VISITADO], rect)
        
        # Dibujar lista tabú
        for (i, j) in lista_tabu:
            rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
            pygame.draw.rect(pantalla, COLORES[TABU], rect)
        
        # Dibujar camino actual
        camino_actual = []
        temp = actual
        while temp in padre:
            camino_actual.append(temp)
            temp = padre[temp]
        
        for (i, j) in camino_actual:
            rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
            pygame.draw.rect(pantalla, COLORES[CAMINO], rect)
        
        # Dibujar inicio y meta
        pygame.draw.rect(pantalla, COLORES[INICIO], 
                        (inicio[1]*TAM_CELDA, inicio[0]*TAM_CELDA, TAM_CELDA, TAM_CELDA))
        pygame.draw.rect(pantalla, COLORES[META], 
                        (meta[1]*TAM_CELDA, meta[0]*TAM_CELDA, TAM_CELDA, TAM_CELDA))
        
        pygame.display.flip()
        clock.tick(10)  # Velocidad más lenta para mejor visualización
    
    # Reconstruir camino final
    camino = []
    temp = meta
    while temp != inicio:
        camino.append(temp)
        temp = padre[temp]
    camino.append(inicio)
    camino.reverse()
    
    # Dibujar camino final
    for (i, j) in camino:
        if laberinto[i][j] not in (INICIO, META):
            laberinto[i][j] = CAMINO
    
    return True

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((COLUMNAS*TAM_CELDA, FILAS*TAM_CELDA))
    pygame.display.set_caption("Búsqueda Tabú en Laberinto")
    clock = pygame.time.Clock()
    
    # Generar laberinto con inicio y meta cercanos
    laberinto, inicio, meta = generar_laberinto_con_camino()
    
    corriendo = True
    buscando = True
    
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    laberinto, inicio, meta = generar_laberinto_con_camino()
                    buscando = True
        
        if buscando:
            exito = busqueda_tabu_visual(laberinto, pantalla, clock, inicio, meta)
            buscando = False
            
            # Mostrar resultado final
            pantalla.fill((255, 255, 255))
            for i in range(FILAS):
                for j in range(COLUMNAS):
                    tipo = laberinto[i][j]
                    color = COLORES.get(tipo, (255, 255, 255))
                    rect = pygame.Rect(j*TAM_CELDA, i*TAM_CELDA, TAM_CELDA, TAM_CELDA)
                    pygame.draw.rect(pantalla, color, rect)
            
            # Mostrar mensaje
            font = pygame.font.SysFont(None, 24)
            if exito:
                texto = font.render("¡Camino encontrado! Presiona R para reiniciar", True, (0, 0, 0))
            else:
                texto = font.render("No se encontró camino. Presiona R para reiniciar", True, (255, 0, 0))
            pantalla.blit(texto, (10, 10))
            
            pygame.display.flip()
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()