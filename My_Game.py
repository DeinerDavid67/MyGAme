import pygame
import sys

pygame.init()

VERDE = (204, 250, 180)
ROJO = (255, 82, 119)
BLANCO =(255, 255, 255)


ventana = pygame.display.set_mode((800,600))
pygame.display.set_caption("simulación de la pantalla - Unidad 2 ")
reloj = pygame.time.Clock()


ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False


        ventana.fill((252, 248, 235))
        pygame.draw.rect(ventana, ROJO, (0, 0, 200, 100),width=2)
        pygame.draw.circle(ventana, VERDE, (200, 200), 50, width=0)


        pygame.display.flip()
        reloj.tick(60)

pygame.quit()
sys.exit()




             



             
  
