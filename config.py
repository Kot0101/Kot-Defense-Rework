import pygame

version = "1.1"
phone = True
WIDTH, HEIGHT = 1400, 800

downbar = 160
upbar = 80

FPS = 60

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync= 1 if phone == False else 0)
