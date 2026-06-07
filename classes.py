import pygame
from config import *

# Classes
class Sprite:
    def __init__(self, path, scale=None):
        self.image = pygame.image.load(path).convert_alpha()
        self.scale = scale
        if scale != None:
            self.image = pygame.transform.scale(self.image, (scale[0], scale[1]))

class Object:
    def __init__(self, sprite, pos, anchor="topleft"):
        self.sprite  = sprite
        self.anchor  = anchor
        self.pos     = pos
        self.rect    = self.sprite.image.get_rect(topleft=pos)
        setattr(self.rect, self.anchor, self.pos)
        self.clicked = False
        self.hovered = False
    
    def click(self):
        return self.game.input.mouse_pressed(1) and self.rect.collidepoint(self.game.input.mouse_pos)
    
    def hover(self):
        return self.rect.collidepoint(self.game.input.mouse_pos)
    
    def update(self):
        self.clicked = self.click()
        self.hovered = self.hover()

    def draw(self):
        screen.blit(self.sprite.image, self.rect)

class Text:
    def __init__(self, font, text, color, pos, anchor="topleft"):
        self.font = font
        self.text = text
        self.color = color
        self.oldVals = []
        self.pos = pos
        self.anchor = anchor
        
        self.render()
    
    def render(self):
        self.oldVals = [self.font, self.text, self.color, self.anchor]
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        
        setattr(self.rect, self.anchor, self.pos)
    
    def draw(self):
        if self.oldVals[0] != self.font or self.oldVals[1] != self.text or self.oldVals[2] != self.color or self.oldVals[3] != self.anchor:
            self.render()
        screen.blit(self.surface, self.rect)

class InfoBar:
    def __init__(self):
        self.font = self.font = pygame.font.SysFont("Arial", 26)
        
        self.text = ""
        
        self.color_text = (170, 170, 170)
        self.color_outlining = (0, 0, 0)
        self.power_outlining = 2

    
    def draw(self, position):
        if self.text == "": return
        self.text_surface = self.font.render(self.text, True, self.color_text)
        self.text_rect = self.text_surface.get_rect()
        if position[0] > WIDTH / 2:
            self.text_rect.right = position[0]-25
            self.text_rect.y = position[1]-10
        else:
            self.text_rect.topleft = position

        self.outlining(self.color_outlining, self.power_outlining)
        screen.blit(self.text_surface, self.text_rect.topleft)
    
    def outlining(self, color, power):
        screen.blit(self.font.render(self.text, True, color), (self.text_rect.x - power, self.text_rect.y))
        screen.blit(self.font.render(self.text, True, color), (self.text_rect.x + power, self.text_rect.y))
        screen.blit(self.font.render(self.text, True, color), (self.text_rect.x, self.text_rect.y - power))
        screen.blit(self.font.render(self.text, True, color), (self.text_rect.x, self.text_rect.y + power))