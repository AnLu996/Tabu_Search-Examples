import pygame
import sys
import numpy as np
import random

class SudokuTabu:
    def __init__(self, tablero, max_iteraciones=1000):
        self.tablero = np.array(tablero)
        self.max_iteraciones = max_iteraciones
        self.tabu_list = []
        self.mejor_conflictos = float('inf')
        self.mejor_solucion = None
        self.celdas_vacias_originales = self.obtener_celdas_vacias()

    def obtener_celdas_vacias(self):
        vacias = []
        for i in range(9):
            for j in range(9):
                if self.tablero[i,j] == 0:
                    vacias.append((i,j))
        return vacias

    def inicializar_tablero(self):
        for (i,j) in self.celdas_vacias_originales:
            self.tablero[i,j] = random.randint(1,9)

    def contar_conflictos(self, tablero):
        conflictos = 0
        # Filas
        for fila in tablero:
            conflictos += 9 - len(set(fila))
        # Columnas
        for col in tablero.T:
            conflictos += 9 - len(set(col))
        # Cuadrantes 3x3
        for i in range(3):
            for j in range(3):
                block = tablero[i*3:(i+1)*3, j*3:(j+1)*3].flatten()
                conflictos += 9 - len(set(block))
        return conflictos

    def generar_vecinos(self):
        vecinos = []
        # Generar vecinos intercambiando valores en dos celdas vacías al azar
        if len(self.celdas_vacias_originales) < 2:
            return vecinos
        for _ in range(10):  # 10 vecinos por iteración
            c1, c2 = random.sample(self.celdas_vacias_originales, 2)
            vecino = np.copy(self.tablero)
            vecino[c1], vecino[c2] = vecino[c2], vecino[c1]
            vecinos.append((c1, c2, vecino))
        return vecinos

    def dibujar_tablero_pygame(self, screen, font, celda1=None, celda2=None):
        screen.fill((255,255,255))
        size_celda = 40
        for i in range(9):
            for j in range(9):
                rect = pygame.Rect(j*size_celda, i*size_celda+40, size_celda, size_celda)
                color = (200,200,200)
                if (i,j) == celda1 or (i,j) == celda2:
                    color = (255,200,200)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0,0,0), rect, 1)
                valor = self.tablero[i,j]
                if valor != 0:
                    text = font.render(str(valor), True, (0,0,0))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
        # Líneas gruesas para cuadrantes
        for i in range(10):
            grosor = 3 if i%3 == 0 else 1
            pygame.draw.line(screen, (0,0,0), (0, i*size_celda+40), (9*size_celda, i*size_celda+40), grosor)
            pygame.draw.line(screen, (0,0,0), (i*size_celda, 40), (i*size_celda, 9*size_celda+40), grosor)

    def resolver_tabu_paso_a_paso(self, screen, font):
        self.inicializar_tablero()

        iteracion = 0
        while iteracion < self.max_iteraciones:
            vecinos = self.generar_vecinos()
            if not vecinos:
                break

            mejor_vecino = None
            mejor_conflictos_vecino = float('inf')
            mejor_celda1 = None
            mejor_celda2 = None

            for (pos1, pos2, vecino) in vecinos:
                conflictos = self.contar_conflictos(vecino)
                if conflictos < mejor_conflictos_vecino:
                    mejor_vecino = vecino
                    mejor_conflictos_vecino = conflictos
                    mejor_celda1, mejor_celda2 = pos1, pos2

            if mejor_vecino is None:
                break

            self.tablero = mejor_vecino
            if mejor_conflictos_vecino < self.mejor_conflictos:
                self.mejor_conflictos = mejor_conflictos_vecino
                self.mejor_solucion = np.copy(mejor_vecino)

            self.dibujar_tablero_pygame(screen, font, celda1=mejor_celda1, celda2=mejor_celda2)
            texto_iter = font.render(f"Iter: {iteracion} Conflictos: {mejor_conflictos_vecino}", True, (0, 128, 0))
            screen.blit(texto_iter, (10, 10))

            pygame.display.flip()
            pygame.time.wait(200)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.mejor_conflictos == 0:
                break

            iteracion += 1

        return self.mejor_solucion

def main():
    pygame.init()
    screen = pygame.display.set_mode((360, 400))
    pygame.display.set_caption("Sudoku Tabu Paso a Paso")
    font = pygame.font.SysFont(None, 30)

    # Ejemplo tablero: 0 son celdas vacías
    tablero_inicial = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9]
    ]

    sudoku = SudokuTabu(tablero_inicial, max_iteraciones=1000)
    solucion = sudoku.resolver_tabu_paso_a_paso(screen, font)

    # Mostrar resultado final por 5 segundos
    sudoku.dibujar_tablero_pygame(screen, font)
    texto_final = font.render(f"Conflictos finales: {sudoku.mejor_conflictos}", True, (0, 0, 255))
    screen.blit(texto_final, (10, 10))
    pygame.display.flip()
    pygame.time.wait(5000)

    pygame.quit()

if __name__ == "__main__":
    main()
