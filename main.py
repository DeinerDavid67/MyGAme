import sys
import pygame
import random
from config import (
    TAMANO_CELDA, FPS, COLOR_MURO,
    COLOR_ENTRADA, COLOR_SALIDA, PALETAS_NIVELES, mapas
)
from entidades import Jugador, Enemigo, Bomba, PowerUp, Llave

pygame.init()

indice_mapa_actual = 0
mapa_ejemplo = mapas[0]
FILAS = len(mapa_ejemplo)
COLUMNAS = len(mapa_ejemplo[0])

ANCHO_PANTALLA = COLUMNAS * TAMANO_CELDA
ALTO_PANTALLA = FILAS * TAMANO_CELDA + 50

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Bomberman - Niveles y Enemigos")
fuente = pygame.font.SysFont("Consolas", 15, bold=True)
fuente_grande = pygame.font.SysFont("Consolas", 36, bold=True)
fuente_pequena = pygame.font.SysFont("Consolas", 18, bold=True)
reloj = pygame.time.Clock()

juego_ganado = False


import os

# Obtener la ruta de la carpeta actual de main.py
DIRECTORIO_ACTUAL = os.path.dirname(__file__)

def buscar_posicion_bloque(matriz, tipo):
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            if matriz[fila][col] == tipo:
                return col, fila
    return 1, 1


def limpiar_zona_inicio(matriz, col_ini, fila_ini):
    matriz[fila_ini][col_ini] = 8
    if fila_ini - 1 >= 0 and matriz[fila_ini - 1][col_ini] == 3:
        matriz[fila_ini - 1][col_ini] = 0
    if col_ini + 1 < COLUMNAS and matriz[fila_ini][col_ini + 1] == 3:
        matriz[fila_ini][col_ini + 1] = 0


def obtener_posiciones_libres_amplias_y_seguras(matriz, col_ini, fila_ini):
    libres = []
    for fila in range(1, FILAS - 1):
        for col in range(1, COLUMNAS - 1):
            if matriz[fila][col] == 0:
                espacios_libres = 0
                if matriz[fila - 1][col] == 0: espacios_libres += 1
                if matriz[fila + 1][col] == 0: espacios_libres += 1
                if matriz[fila][col - 1] == 0: espacios_libres += 1
                if matriz[fila][col + 1] == 0: espacios_libres += 1
                
                distancia_inicio = abs(col - col_ini) + abs(fila - fila_ini)
                if espacios_libres >= 2 and distancia_inicio > 3:
                    libres.append((col, fila))
    
    if len(libres) < 3:
        for fila in range(1, FILAS - 1):
            for col in range(1, COLUMNAS - 1):
                if matriz[fila][col] == 0 and (col, fila) not in libres:
                    distancia_inicio = abs(col - col_ini) + abs(fila - fila_ini)
                    if distancia_inicio > 2:
                        libres.append((col, fila))
                        if len(libres) >= 3:
                            break
            if len(libres) >= 3:
                break
                
    return libres


def reiniciar_nivel(indice):
    global matriz_actual, jugador, enemigos, bombas, power_ups, llave, celda_con_llave, celdas_con_powerup
    matriz_actual = [fila[:] for fila in mapas[indice]]
    
    col_ini, fila_ini = buscar_posicion_bloque(matriz_actual, 8)
    limpiar_zona_inicio(matriz_actual, col_ini, fila_ini)
    
    jugador = Jugador(col_ini, fila_ini)
    
    enemigos = []
    posiciones_libres = obtener_posiciones_libres_amplias_y_seguras(matriz_actual, col_ini, fila_ini)
    
    cantidad_enemigos = min(3, len(posiciones_libres))
    
    for _ in range(cantidad_enemigos):
        if posiciones_libres:
            pos = random.choice(posiciones_libres)
            posiciones_libres.remove(pos)
            enemigos.append(Enemigo(pos[0], pos[1]))

    bombas = []
    power_ups = []
    llave = None

    bloques_destructibles = []
    for f in range(FILAS):
        for c in range(COLUMNAS):
            if matriz_actual[f][c] == 3:
                bloques_destructibles.append((c, f))
    
    celda_con_llave = None
    celdas_con_powerup = set()
    
    if bloques_destructibles:
        random.shuffle(bloques_destructibles)
        celda_con_llave = bloques_destructibles.pop()
        
        cantidad_power_ups = min(2, len(bloques_destructibles))
        celdas_con_powerup = set(bloques_destructibles[:cantidad_power_ups])


# Inicializar el juego
matriz_actual = []
jugador = None
enemigos = []
bombas = []
power_ups = []
llave = None
celda_con_llave = None
celdas_con_powerup = set()
reiniciar_nivel(indice_mapa_actual)

ejecutando = True
while ejecutando:
    if juego_ganado:
        pantalla.fill((20, 20, 40))
        
        texto_felicitaciones = fuente_grande.render("FELICIDADES", True, (255, 215, 0))
        texto_gracias = fuente_pequena.render("gracias por jugar", True, (200, 200, 200))
        texto_salir = fuente.render("Presiona ESC o cierra la ventana para salir", True, (140, 140, 140))

        pantalla.blit(texto_felicitaciones, (ANCHO_PANTALLA // 2 - texto_felicitaciones.get_width() // 2, ALTO_PANTALLA // 2 - 50))
        pantalla.blit(texto_gracias, (ANCHO_PANTALLA // 2 - texto_gracias.get_width() // 2, ALTO_PANTALLA // 2))
        pantalla.blit(texto_salir, (ANCHO_PANTALLA // 2 - texto_salir.get_width() // 2, ALTO_PANTALLA // 2 + 50))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                ejecutando = False
        reloj.tick(FPS)
        continue

    paleta_actual = PALETAS_NIVELES[indice_mapa_actual % len(PALETAS_NIVELES)]

    # 1. Procesar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                col_b = int((jugador.x + jugador.ancho / 2) // TAMANO_CELDA)
                fila_b = int((jugador.y + jugador.alto / 2) // TAMANO_CELDA)
                
                lugar_ocupado = any(b.col == col_b and b.fila == fila_b for b in bombas)
                
                if len(bombas) < jugador.max_bombas and not lugar_ocupado:
                    bombas.append(Bomba(col_b, fila_b, jugador.radio_bomba))

    # 2. Controles de movimiento del jugador
    teclas = pygame.key.get_pressed()
    dx, dy = 0, 0
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        dx = -1
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        dx = 1
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        dy = -1
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        dy = 1
    jugador.mover(dx, dy, matriz_actual, bombas)

    # 2.5 Verificar si el jugador recoge algún Power-Up
    for pu in power_ups[:]:
        if jugador.obtener_rect().colliderect(pu.obtener_rect()):
            if pu.tipo == "radio":
                jugador.radio_bomba += 1
            power_ups.remove(pu)

    # 2.6 Verificar si el jugador recoge la llave
    if llave and jugador.obtener_rect().colliderect(llave.obtener_rect()):
        jugador.tiene_llave = True
        llave = None

    # 3. Comprobar si el jugador llega a la puerta final (9) [Requiere llave]
    col_j = int((jugador.x + jugador.ancho / 2) // TAMANO_CELDA)
    fila_j = int((jugador.y + jugador.alto / 2) // TAMANO_CELDA)
    if matriz_actual[fila_j][col_j] == 9 and jugador.tiene_llave:
        indice_mapa_actual += 1
        if indice_mapa_actual < len(mapas):
            reiniciar_nivel(indice_mapa_actual)
        else:
            juego_ganado = True

    # 4. Actualizar enemigos y verificar colisión con el jugador
    for enemigo in enemigos[:]:
        enemigo.actualizar(matriz_actual, bombas, enemigos)
        if jugador.obtener_rect().colliderect(enemigo.obtener_rect()):
            jugador.vidas -= 1
            reiniciar_nivel(indice_mapa_actual)
            if jugador.vidas <= 0:
                print("¡Game Over!")
                ejecutando = False

    # 5. Actualizar bombas, procesar explosiones y revelar objetos
    celdas_afectadas_totales = []
    for bomba in bombas[:]:
        bomba.actualizar()
        if bomba.timer <= 0:
            bc, bf = bomba.col, bomba.fila
            celdas_afectadas_bomba = [(bc, bf)]
            
            for dx_dir, dy_dir in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for r in range(1, bomba.radio + 1):
                    nc = bc + dx_dir * r
                    nf = bf + dy_dir * r
                    
                    if 0 <= nf < FILAS and 0 <= nc < COLUMNAS:
                        tipo_bloque = matriz_actual[nf][nc]
                        if tipo_bloque == 1 or tipo_bloque == 2:
                            break
                        celdas_afectadas_bomba.append((nc, nf))
                        if tipo_bloque == 3:
                            matriz_actual[nf][nc] = 0
                            
                            if celda_con_llave == (nc, nf):
                                llave = Llave(nc, nf)
                                celda_con_llave = None
                            
                            if (nc, nf) in celdas_con_powerup:
                                power_ups.append(PowerUp(nc, nf, "radio"))
                                celdas_con_powerup.remove((nc, nf))
                            break
                    else:
                        break
            
            celdas_afectadas_totales.extend(celdas_afectadas_bomba)
            bombas.remove(bomba)

    explosion_activa = len(celdas_afectadas_totales) > 0
    if explosion_activa:
        col_jugador_celda = int((jugador.x + jugador.ancho / 2) // TAMANO_CELDA)
        fila_jugador_celda = int((jugador.y + jugador.alto / 2) // TAMANO_CELDA)
        
        if (col_jugador_celda, fila_jugador_celda) in celdas_afectadas_totales:
            jugador.vidas -= 1
            reiniciar_nivel(indice_mapa_actual)
            if jugador.vidas <= 0:
                print("¡Game Over por explosión!")
                ejecutando = False

        enemigos = [e for e in enemigos if (int((e.x + e.ancho/2) // TAMANO_CELDA), int((e.y + e.alto/2) // TAMANO_CELDA)) not in celdas_afectadas_totales]

    # 6. Dibujar todo en pantalla
    pantalla.fill(paleta_actual["piso"])

    for x in range(0, ANCHO_PANTALLA, TAMANO_CELDA):
        pygame.draw.line(pantalla, paleta_actual["grid"], (x, 0), (x, FILAS * TAMANO_CELDA))
    for y in range(0, FILAS * TAMANO_CELDA, TAMANO_CELDA):
        pygame.draw.line(pantalla, paleta_actual["grid"], (0, y), (ANCHO_PANTALLA, y))

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            valor = matriz_actual[fila][col]
            x = col * TAMANO_CELDA
            y = fila * TAMANO_CELDA
            rect = pygame.Rect(x, y, TAMANO_CELDA, TAMANO_CELDA)

            if valor == 1:
                pygame.draw.rect(pantalla, COLOR_MURO, rect)
            elif valor == 2:
                pygame.draw.rect(pantalla, paleta_actual["estructura"], rect, border_radius=4)
            elif valor == 3:
                pygame.draw.rect(pantalla, paleta_actual["destructible"], rect, border_radius=4)
            elif valor == 8:
                pygame.draw.rect(pantalla, COLOR_ENTRADA, rect)
            elif valor == 9:
                pygame.draw.rect(pantalla, COLOR_SALIDA, rect)

    if llave:
        llave.dibujar(pantalla)
    for pu in power_ups:
        pu.dibujar(pantalla)

    for bomba in bombas:
        bx = bomba.col * TAMANO_CELDA + TAMANO_CELDA // 2
        by = bomba.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        pygame.draw.circle(pantalla, (0, 0, 0), (bx, by), 12)

    if explosion_activa:
        for ec, ef in celdas_afectadas_totales:
            ex = ec * TAMANO_CELDA
            ey = ef * TAMANO_CELDA
            pygame.draw.rect(pantalla, (255, 140, 0), (ex, ey, TAMANO_CELDA, TAMANO_CELDA))

    jugador.dibujar(pantalla)
    for enemigo in enemigos:
        enemigo.dibujar(pantalla)

    estado_llave = "SÍ" if jugador.tiene_llave else "NO"
    texto = fuente.render(
        f"NIVEL: {indice_mapa_actual + 1}/{len(mapas)} | LLAVE: {estado_llave} | VIDAS: {jugador.vidas} | RADIO: {jugador.radio_bomba}",
        True,
        (255, 255, 255),
    )
    pantalla.blit(texto, (10, ALTO_PANTALLA - 35))

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()