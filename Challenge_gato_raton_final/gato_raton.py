import sys
import random
import pygame

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
TAMANIO_TABLERO = 8
CELL_SIZE = 50
WIDTH, HEIGHT = TAMANIO_TABLERO * CELL_SIZE, TAMANIO_TABLERO * CELL_SIZE
max_profundidad = 3
max_historial = 5  # Limitar el historial a los últimos 5 movimientos
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ratón y Gato")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# Inicializar posiciones del ratón, el gato y la madriguera
posicion_raton = (random.randint(0, TAMANIO_TABLERO - 1), random.randint(0, TAMANIO_TABLERO - 1))
posicion_gato = (random.randint(0, TAMANIO_TABLERO - 1), random.randint(0, TAMANIO_TABLERO - 1))
posiciones_esquinas = [(0, 0), (0, TAMANIO_TABLERO - 1), (TAMANIO_TABLERO - 1, 0), (TAMANIO_TABLERO - 1, TAMANIO_TABLERO - 1)]
posicion_madriguera = random.choice(posiciones_esquinas)

# Asegurarse de que el ratón y el gato no empiecen en la misma posición
while posicion_raton == posicion_gato:
    posicion_gato = (random.randint(0, TAMANIO_TABLERO - 1), random.randint(0, TAMANIO_TABLERO - 1))

# Historial de movimientos
historial_raton = []
historial_gato = []

def dibujar_tablero():
    for fila in range(TAMANIO_TABLERO):
        for columna in range(TAMANIO_TABLERO):
            rect = pygame.Rect(columna * CELL_SIZE, fila * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def dibujar_raton(pos):
    x, y = pos
    rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.ellipse(screen, GRAY, rect)

def dibujar_gato(pos):
    x, y = pos
    rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.ellipse(screen, ORANGE, rect)

def dibujar_madriguera(pos):
    x, y = pos
    rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, GREEN, rect)

def evaluar(pos_raton, pos_gato, pos_madriguera):
    distancia_raton_madriguera = abs(pos_raton[0] - pos_madriguera[0]) + abs(pos_raton[1] - pos_madriguera[1])
    distancia_gato_raton = abs(pos_gato[0] - pos_raton[0]) + abs(pos_gato[1] - pos_raton[1])
    
    if pos_raton == pos_gato:
        return -100  # Pierde el raton
    if pos_raton == pos_madriguera:
        return 100  # Pierde el gato
    return distancia_gato_raton - distancia_raton_madriguera

def movimientos_validos(posicion):
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    resultado = []
    for movimiento in movimientos:
        nueva_posicion = (posicion[0] + movimiento[0], posicion[1] + movimiento[1])
        if 0 <= nueva_posicion[0] < TAMANIO_TABLERO and 0 <= nueva_posicion[1] < TAMANIO_TABLERO:
            resultado.append(nueva_posicion)
    return resultado

def minimax(pos_raton, pos_gato, pos_madriguera, profundidad, maximizando):
    if profundidad == 0 or pos_raton == pos_gato or pos_raton == pos_madriguera:
        return evaluar(pos_raton, pos_gato, pos_madriguera)

    if maximizando:
        mejor_valor = -float('inf')
        for movimiento in movimientos_validos(pos_raton):
            valor = minimax(movimiento, pos_gato, pos_madriguera, profundidad - 1, False)
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        mejor_valor = float('inf')
        for movimiento in movimientos_validos(pos_gato):
            valor = minimax(pos_raton, movimiento, pos_madriguera, profundidad - 1, True)
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor

def mejor_movimiento(pos_inicial, pos_oponente, pos_madriguera, maximizando, historial):
    mejor_mov = None
    mejor_valor = -float('inf') if maximizando else float('inf')

    for movimiento in movimientos_validos(pos_inicial):
        if movimiento in historial:
            continue  # Evitar movimientos repetidos

        valor = minimax(movimiento, pos_oponente, pos_madriguera, max_profundidad, not maximizando)
        if (maximizando and valor > mejor_valor) or (not maximizando and valor < mejor_valor):
            mejor_valor = valor
            mejor_mov = movimiento

    return mejor_mov

def mover_raton():
    global posicion_raton
    siguiente_paso = mejor_movimiento(posicion_raton, posicion_gato, posicion_madriguera, True, historial_raton)
    if siguiente_paso:
        posicion_raton = siguiente_paso
        historial_raton.append(posicion_raton)
        if len(historial_raton) > max_historial:
            historial_raton.pop(0)
    if posicion_raton == posicion_madriguera:
        terminar_juego("El ratón ha escapado")

def mover_gato():
    global posicion_gato
    siguiente_paso = mejor_movimiento(posicion_gato, posicion_raton, posicion_madriguera, False, historial_gato)
    if siguiente_paso:
        posicion_gato = siguiente_paso
        historial_gato.append(posicion_gato)
        if len(historial_gato) > max_historial:
            historial_gato.pop(0)
    if posicion_gato == posicion_raton:
        terminar_juego("El gato atrapó al ratón")

# Variable para manejar los turnos
turno_raton = True

def terminar_juego(mensaje):
    print(mensaje)
    pygame.quit()
    sys.exit()

# Ciclo principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if turno_raton:
        mover_raton()
    else:
        mover_gato()
    turno_raton = not turno_raton

    # Dibujar el estado actual del juego
    screen.fill(WHITE)
    dibujar_tablero()
    dibujar_madriguera(posicion_madriguera)
    dibujar_raton(posicion_raton)
    dibujar_gato(posicion_gato)
    pygame.display.flip()
    
    # Controlar la velocidad del juego
    pygame.time.delay(500)
