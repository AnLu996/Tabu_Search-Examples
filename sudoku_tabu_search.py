import numpy as np
import pygame
import random
import time

class SudokuTabu:
    def __init__(self, tablero_inicial, velocidad_ms=500):
        self.tablero = np.array(tablero_inicial)
        self.tablero_original = self.tablero.copy()
        self.celdas_vacias_originales = self.obtener_celdas_vacias()
        self.tabu_lista = []
        self.tabu_tamano = 100
        self.velocidad_ms = velocidad_ms
        self.mejor_solucion = None
        self.mejor_conflictos = float('inf')
        self.soluciones_encontradas = []
        self.iteracion_actual = 0
        self.max_iteraciones = 100

    def obtener_celdas_vacias(self):
        return [(i, j) for i in range(9) for j in range(9) if self.tablero[i][j] == 0]

    def es_valido(self, i, j, num):
        if num in self.tablero[i]: return False
        if num in self.tablero[:, j]: return False
        f, c = 3 * (i // 3), 3 * (j // 3)
        if num in self.tablero[f:f+3, c:c+3]: return False
        return True

    def rellenar_logicamente(self, screen, font):
        self.mostrar_mensaje(screen, font, "Iniciando relleno lógico...", (385, 10))
        progreso = True
        while progreso:
            progreso = False
            for (i, j) in self.celdas_vacias_originales:
                if self.tablero[i, j] == 0:
                    posibles = [n for n in range(1, 10) if self.es_valido(i, j, n)]
                    if len(posibles) == 1:
                        self.tablero[i, j] = posibles[0]
                        progreso = True
                        self.dibujar_tablero_pygame(screen, font, celda_actual=(i, j))
                        self.mostrar_mensaje(screen, font, f"Rellenando ({i},{j}) con {posibles[0]}", (385, 10))
                        pygame.display.flip()
                        pygame.time.wait(self.velocidad_ms)
        
        # Verificar si quedan celdas vacías
        vacias = self.obtener_celdas_vacias()
        if vacias:
            self.mostrar_mensaje(screen, font, "No se pueden rellenar más celdas lógicamente", (385, 40))
            self.mostrar_mensaje(screen, font, "Se rellenarán los espacios con números aleatorios", (385, 70))
            pygame.display.flip()
            pygame.time.wait(self.velocidad_ms * 2)

    def inicializar_tablero(self, screen, font):
        for (i, j) in self.celdas_vacias_originales:
            if self.tablero[i, j] == 0:
                self.tablero[i, j] = random.randint(1, 9)
        self.dibujar_tablero_pygame(screen, font)
        pygame.display.flip()
        pygame.time.wait(self.velocidad_ms)

    def contar_conflictos(self, tablero=None):
        if tablero is None:
            tablero = self.tablero
        conflictos = 0
        for i in range(9):
            conflictos += 9 - len(set(tablero[i, :]))
            conflictos += 9 - len(set(tablero[:, i]))
        for f in range(0, 9, 3):
            for c in range(0, 9, 3):
                subcuadro = tablero[f:f+3, c:c+3].flatten()
                conflictos += 9 - len(set(subcuadro))
        return conflictos

    def resolver_tabu_paso_a_paso(self, screen, font):
        # Fase 1: Relleno lógico
        self.rellenar_logicamente(screen, font)
        self.celdas_vacias_originales = self.obtener_celdas_vacias()
        
        # Fase 2: Inicialización aleatoria
        self.inicializar_tablero(screen, font)
        
        # Fase 3: Búsqueda Tabú
        self.mostrar_mensaje(screen, font, "Iniciando búsqueda Tabú...", (385, 10))
        pygame.display.flip()
        pygame.time.wait(self.velocidad_ms)
        
        self.mejor_solucion = self.tablero.copy()
        self.mejor_conflictos = self.contar_conflictos()
        self.soluciones_encontradas.append((self.mejor_solucion.copy(), self.mejor_conflictos))
        
        while self.mejor_conflictos > 0 and self.iteracion_actual < self.max_iteraciones:
            vecinos = []
            celdas_cambiadas = []  # Lista para guardar las celdas que cambian
            
            for _ in range(50):
                vecino = self.tablero.copy()
                if len(self.celdas_vacias_originales) < 2:
                    continue
                (i1, j1), (i2, j2) = random.sample(self.celdas_vacias_originales, 2)
                vecino[i1, j1], vecino[i2, j2] = vecino[i2, j2], vecino[i1, j1]
                if (i1, j1, i2, j2) not in self.tabu_lista:
                    vecinos.append((vecino, (i1, j1, i2, j2)))
                    celdas_cambiadas.append((i1, j1))  # Añadir celdas cambiadas
                    celdas_cambiadas.append((i2, j2))

            if not vecinos:
                break

            # Evaluar vecinos
            vecinos_conflictos = [(v, m, self.contar_conflictos(v)) for v, m in vecinos]
            vecinos_conflictos.sort(key=lambda x: x[2])
            
            mejor_vecino, movimiento, conflictos_vecino = vecinos_conflictos[0]
            
            # Actualizar mejor solución
            if conflictos_vecino < self.mejor_conflictos:
                self.mejor_solucion = mejor_vecino.copy()
                self.mejor_conflictos = conflictos_vecino
                self.soluciones_encontradas.append((self.mejor_solucion.copy(), self.mejor_conflictos))
                
                # Mostrar alerta de nueva solución
                self.dibujar_tablero_pygame(screen, font)
                
                # Fondo para el mensaje de alerta
                alerta_rect = pygame.Rect(385, 240, 320, 110)
                pygame.draw.rect(screen, (200, 255, 200), alerta_rect)  # Fondo verde claro
                pygame.draw.rect(screen, (0, 180, 0), alerta_rect, 3)  # Borde verde oscuro
                
                # Texto de la alerta
                texto_alertas = [
                    f"¡NUEVA MEJOR SOLUCIÓN ENCONTRADA!",
                    f"Solución #{len(self.soluciones_encontradas)}",
                    f"Conflictos reducidos a: {self.mejor_conflictos}",
                    f"Iteración actual: {self.iteracion_actual}"
                ]
                
                for i, texto in enumerate(texto_alertas):
                    color = (0, 100, 0) if i == 0 else (0, 0, 0)  # Primer línea en verde oscuro
                    texto_surface = font.render(texto, True, color)
                    screen.blit(texto_surface, (410, 250 + i * 25))
                
                pygame.display.flip()
                pygame.time.wait(self.velocidad_ms * 2)

            # Actualizar tablero actual y lista tabú
            self.tablero = mejor_vecino.copy()
            self.tabu_lista.append(movimiento)
            if len(self.tabu_lista) > self.tabu_tamano:
                self.tabu_lista.pop(0)

            # Mostrar información de la iteración
            self.dibujar_tablero_pygame(screen, font, celdas_cambiadas=celdas_cambiadas)
            self.mostrar_info_iteracion(screen, font)
            pygame.display.flip()
            pygame.time.wait(self.velocidad_ms // 2)

            self.iteracion_actual += 1

        # Mostrar resultado final
        self.tablero = self.mejor_solucion.copy()
        self.dibujar_tablero_pygame(screen, font)
        if self.mejor_conflictos == 0:
            self.mostrar_mensaje(screen, font, "¡Solución encontrada!", (385, 10), color=(0, 200, 0))
        else:
            self.mostrar_mensaje(screen, font, "Solución no óptima encontrada", (385, 10), color=(200, 0, 0))
        
        self.mostrar_mensaje(screen, font, f"Total iteraciones: {self.iteracion_actual}", (385, 40))
        self.mostrar_mensaje(screen, font, f"Conflictos finales: {self.mejor_conflictos}", (385, 70))
        self.mostrar_mensaje(screen, font, f"Mejores soluciones encontradas: {len(self.soluciones_encontradas)}", (385, 100))
        pygame.display.flip()
        pygame.time.wait(self.velocidad_ms * 10)

        return self.mejor_conflictos == 0

    def mostrar_info_iteracion(self, screen, font):
        self.mostrar_mensaje(screen, font, f"Búsqueda Tabú en progreso...", (385, 10))
        self.mostrar_mensaje(screen, font, f"Solución actual: #{len(self.soluciones_encontradas)}", (385, 40))
        self.mostrar_mensaje(screen, font, f"Mejor solución: {self.mejor_conflictos} conflictos", (385, 70))
        self.mostrar_mensaje(screen, font, f"Iteración: {self.iteracion_actual}/{self.max_iteraciones}", (385, 100))
        self.mostrar_mensaje(screen, font, f"Conflictos actuales: {self.contar_conflictos()}", (385, 130))

    def mostrar_mensaje(self, screen, font, texto, posicion, color=(0, 0, 0)):
        texto_surface = font.render(texto, True, color)
        screen.blit(texto_surface, posicion)

    def dibujar_tablero_pygame(self, screen, font, celda_actual=None, celdas_cambiadas=None):
        # Fondo blanco
        screen.fill((255, 255, 255))
        
        # Dibujar cuadrícula
        for i in range(10):
            ancho = 3 if i % 3 == 0 else 1
            pygame.draw.line(screen, (0, 0, 0), (10, i * 40 + 10), (370, i * 40 + 10), ancho)
            pygame.draw.line(screen, (0, 0, 0), (i * 40 + 10, 10), (i * 40 + 10, 370), ancho)

        # Dibujar números
        for i in range(9):
            for j in range(9):
                num = self.tablero[i, j]
                if num != 0:
                    color = (0, 0, 255) if self.tablero_original[i, j] != 0 else (0, 128, 0)
                    texto = font.render(str(num), True, color)
                    screen.blit(texto, (j * 40 + 25, i * 40 + 20))

        # Resaltar celdas cambiadas (nuevo)
        if celdas_cambiadas:
            for i, j in celdas_cambiadas:
                pygame.draw.rect(screen, (255, 100, 0), (j * 40 + 10, i * 40 + 10, 40, 40), 3)  # Naranja

        # Resaltar celda actual si se especifica (original)
        if celda_actual:
            i, j = celda_actual
            pygame.draw.rect(screen, (255, 0, 0), (j * 40 + 10, i * 40 + 10, 40, 40), 3)  # Rojo

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("Resolución de Sudoku con Búsqueda Tabú")
    font = pygame.font.SysFont("Arial", 16)
    font_bold = pygame.font.SysFont("Arial", 16, bold=True)

    sudoku = [
        [5, 0, 7, 6, 0, 0, 0, 3, 4],
        [0, 0, 9, 0, 0, 4, 0, 0, 0],
        [3, 0, 6, 2, 0, 5, 0, 9, 0],
        [6, 0, 2, 0, 0, 0, 0, 1, 0],
        [0, 3, 8, 0, 0, 6, 0, 4, 7],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 9, 0, 0, 0, 0, 0, 7, 8],
        [7, 0, 3, 4, 0, 0, 5, 6, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    velocidad = 500  # Velocidad de visualización en ms
    juego = SudokuTabu(sudoku, velocidad_ms=velocidad)

    # Dibujar tablero inicial
    screen.fill((255, 255, 255))
    juego.dibujar_tablero_pygame(screen, font)
    juego.mostrar_mensaje(screen, font_bold, "Tablero inicial de Sudoku", (385, 20))
    pygame.display.flip()
    pygame.time.wait(velocidad * 2)

    corriendo = True
    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
        
        # Resolver el sudoku
        juego.resolver_tabu_paso_a_paso(screen, font)
        
        # Esperar antes de salir
        pygame.time.wait(velocidad * 5)
        corriendo = False

    pygame.quit()

if __name__ == "__main__":
    main()