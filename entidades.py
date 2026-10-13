import pygame
import random
import os
from config import TAMANO_CELDA

DIRECTORIO_ACTUAL = os.path.dirname(__file__)

class Jugador:
    
 
    def __init__(self, x, y):  # <-- Debe recibir x e y obligatoriamente
        self.x = x * TAMANO_CELDA + 5
        self.y = y * TAMANO_CELDA + 5
        self.ancho = TAMANO_CELDA - 10
        self.alto = TAMANO_CELDA - 10
        self.velocidad = 3
        self.vidas = 3
        self.max_bombas = 2
        self.radio_bomba = 1
        self.tiene_llave = False

        self.animacion_frames = []
        self.frame_actual = 0
        self.contador_anim = 0
        self.cargando_sprites()
    
    
    
    
    def cargando_sprites(self):
        nombres_posibles = [
            "sprites_nes.png",
            "NES - Bomberman - Miscellaneous - General Sprites.png",
            "sprites_jugador.png"
        ]
        
        hoja = None
        for nombre in nombres_posibles:
            ruta = os.path.join(DIRECTORIO_ACTUAL, nombre)
            if os.path.exists(ruta):
                try:
                    hoja = pygame.image.load(ruta).convert_alpha()
                    break
                except pygame.error:
                    pass

        if hoja:
            try:
                self.animacion_frames = [
                    pygame.transform.scale(hoja.subsurface(pygame.Rect(0, 0, 16, 16)), (self.ancho, self.alto)),
                    pygame.transform.scale(hoja.subsurface(pygame.Rect(16, 0, 16, 16)), (self.ancho, self.alto)),
                    pygame.transform.scale(hoja.subsurface(pygame.Rect(32, 0, 16, 16)), (self.ancho, self.alto))
                ]
            except pygame.error:
                self.animacion_frames = []
        else:
            # Si no encuentra ninguna imagen, usa una lista vacía para que dibuje el rectángulo de respaldo sin crashear
            self.animacion_frames = []

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def mover(self, dx, dy, matriz, bombas=None):
        filas = len(matriz)
        columnas = len(matriz[0])

        if dx != 0 or dy != 0:
            self.contador_anim += 1
            if self.contador_anim >= 10:
                if self.animacion_frames:
                    self.frame_actual = (self.frame_actual + 1) % len(self.animacion_frames)
                self.contador_anim = 0

        def hay_colision(rect_prueba):
            if rect_prueba.left < 0 or rect_prueba.right > columnas * TAMANO_CELDA:
                return True
            if rect_prueba.top < 0 or rect_prueba.bottom > filas * TAMANO_CELDA:
                return True

            for fila in range(filas):
                for col in range(columnas):
                    val = matriz[fila][col]
                    if val in [1, 2, 3]:
                        wall_rect = pygame.Rect(col * TAMANO_CELDA, fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                        if rect_prueba.colliderect(wall_rect):
                            return True
            
            if bombas:
                for bomba in bombas:
                    bomba_rect = pygame.Rect(bomba.col * TAMANO_CELDA, bomba.fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                    if rect_prueba.colliderect(bomba_rect):
                        if not bomba.player_left:
                            pass
                        else:
                            return True
                    else:
                        bomba.player_left = True
            return False

        self.x += dx * self.velocidad
        if hay_colision(self.obtener_rect()):
            self.x -= dx * self.velocidad

        self.y += dy * self.velocidad
        if hay_colision(self.obtener_rect()):
            self.y -= dy * self.velocidad

    def dibujar(self, superficie):
        if self.animacion_frames:
            superficie.blit(self.animacion_frames[self.frame_actual], (self.x, self.y))
        else:
            pygame.draw.rect(superficie, (0, 0, 255), (*self.obtener_rect().topleft, self.ancho, self.alto), border_radius=6)


class Enemigo:
    
    
    
    
    def __init__(self, col, fila):  # <-- Asegúrate de que tenga estos dos argumentos
        self.x = col * TAMANO_CELDA + 5
        self.y = fila * TAMANO_CELDA + 5
        self.ancho = TAMANO_CELDA - 10
        self.alto = TAMANO_CELDA - 10
        self.velocidad = 1
        
        self.animacion_frames = []
        self.frame_actual = 0
        self.contador_anim = 0
        self.cargando_sprites()

        if random.choice([True, False]):
            self.dir_x = random.choice([-1, 1])
            self.dir_y = 0
        else:
            self.dir_x = 0
            self.dir_y = random.choice([-1, 1])
    def cargando_sprites(self):
        nombres_posibles = [
            "sprites_nes.png",
            "NES - Bomberman - Miscellaneous - General Sprites.png",
            "enemigos.png"
        ]
        
        hoja = None
        for nombre in nombres_posibles:
            ruta = os.path.join(DIRECTORIO_ACTUAL, nombre)
            if os.path.exists(ruta):
                try:
                    hoja = pygame.image.load(ruta).convert_alpha()
                    break
                except pygame.error:
                    pass

        if hoja:
            try:
                self.animacion_frames = [
                    pygame.transform.scale(hoja.subsurface(pygame.Rect(0, 112, 16, 16)), (self.ancho, self.alto)),
                    pygame.transform.scale(hoja.subsurface(pygame.Rect(16, 112, 16, 16)), (self.ancho, self.alto))
                ]
            except pygame.error:
                self.animacion_frames = []
        else:
            self.animacion_frames = []

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def actualizar(self, matriz, bombas=None, otros_enemigos=None):
        filas = len(matriz)
        columnas = len(matriz[0])

        self.contador_anim += 1
        if self.contador_anim >= 15:
            if self.animacion_frames:
                self.frame_actual = (self.frame_actual + 1) % len(self.animacion_frames)
            self.contador_anim = 0

        def celda_bloqueada(c, f):
            if not (0 <= f < filas and 0 <= c < columnas):
                return True
            val = matriz[f][c]
            if val in [1, 2, 3, 8, 9]:
                return True
            if bombas:
                for b in bombas:
                    if b.col == c and b.fila == f:
                        return True
            return False

        if self.dir_x != 0:
            self.x += self.dir_x * self.velocidad
            rect = self.obtener_rect()
            
            colision = False
            for fila in range(filas):
                for col in range(columnas):
                    if matriz[fila][col] in [1, 2, 3, 8, 9]:
                        if rect.colliderect(pygame.Rect(col * TAMANO_CELDA, fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)):
                            colision = True
            if bombas:
                for b in bombas:
                    if rect.colliderect(pygame.Rect(b.col * TAMANO_CELDA, b.fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)):
                        colision = True

            if otros_enemigos:
                for otro in otros_enemigos:
                    if otro != self and rect.colliderect(otro.obtener_rect()):
                        colision = True

            if colision:
                self.x -= self.dir_x * self.velocidad
                celda_c = int((self.x + self.ancho / 2) // TAMANO_CELDA)
                celda_f = int((self.y + self.alto / 2) // TAMANO_CELDA)
                
                opciones = []
                if not celda_bloqueada(celda_c, celda_f - 1):
                    opciones.append(-1)
                if not celda_bloqueada(celda_c, celda_f + 1):
                    opciones.append(1)
                
                if opciones:
                    self.dir_y = random.choice(opciones)
                    self.dir_x = 0
                else:
                    self.dir_x *= -1

        elif self.dir_y != 0:
            self.y += self.dir_y * self.velocidad
            rect = self.obtener_rect()
            
            colision = False
            for fila in range(filas):
                for col in range(columnas):
                    if matriz[fila][col] in [1, 2, 3, 8, 9]:
                        if rect.colliderect(pygame.Rect(col * TAMANO_CELDA, fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)):
                            colision = True
            if bombas:
                for b in bombas:
                    if rect.colliderect(pygame.Rect(b.col * TAMANO_CELDA, b.fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)):
                        colision = True

            if otros_enemigos:
                for otro in otros_enemigos:
                    if otro != self and rect.colliderect(otro.obtener_rect()):
                        colision = True

            if colision:
                self.y -= self.dir_y * self.velocidad
                celda_c = int((self.x + self.ancho / 2) // TAMANO_CELDA)
                celda_f = int((self.y + self.alto / 2) // TAMANO_CELDA)
                
                opciones = []
                if not celda_bloqueada(celda_c - 1, celda_f):
                    opciones.append(-1)
                if not celda_bloqueada(celda_c + 1, celda_f):
                    opciones.append(1)
                
                if opciones:
                    self.dir_x = random.choice(opciones)
                    self.dir_y = 0
                else:
                    self.dir_y *= -1

    def dibujar(self, superficie):
        if self.animacion_frames:
            superficie.blit(self.animacion_frames[self.frame_actual], (self.x, self.y))
        else:
            pygame.draw.rect(superficie, (255, 69, 0), (*self.obtener_rect().topleft, self.ancho, self.alto), border_radius=6)


class Bomba:
    def __init__(self, col, fila, radio):
        self.col = col
        self.fila = fila
        self.timer = 120
        self.radio = radio
        self.player_left = False

    def actualizar(self):
        self.timer -= 1


class PowerUp:
    def __init__(self, col, fila, tipo="radio"):
        self.col = col
        self.fila = fila
        self.tipo = tipo

    def obtener_rect(self):
        return pygame.Rect(self.col * TAMANO_CELDA + 8, self.fila * TAMANO_CELDA + 8, TAMANO_CELDA - 16, TAMANO_CELDA - 16)

    def dibujar(self, superficie):
        centro_x = self.col * TAMANO_CELDA + TAMANO_CELDA // 2
        centro_y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        pygame.draw.circle(superficie, (255, 215, 0), (centro_x, centro_y), 12)
        pygame.draw.circle(superficie, (255, 255, 255), (centro_x, centro_y), 6)


class Llave:
    def __init__(self, col, fila):
        self.col = col
        self.fila = fila

    def obtener_rect(self):
        return pygame.Rect(self.col * TAMANO_CELDA + 10, self.fila * TAMANO_CELDA + 10, TAMANO_CELDA - 20, TAMANO_CELDA - 20)

    def dibujar(self, superficie):
        centro_x = self.col * TAMANO_CELDA + TAMANO_CELDA // 2
        centro_y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        pygame.draw.circle(superficie, (192, 192, 192), (centro_x, centro_y - 2), 7)
        pygame.draw.rect(superficie, (192, 192, 192), (centro_x - 2, centro_y, 4, 12))