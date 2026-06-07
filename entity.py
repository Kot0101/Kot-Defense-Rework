from pathlib import Path
from classes import *
from managers import *
from config import *
import pygame
from pygame import gfxdraw

def load_entity(game):
    class Product(Object):
        def __init__(self, sprite, cost):
            super().__init__(sprite, (0,0))
            self.cost = cost
            self.color = (255, 255, 255)
        
        def render(self, font):
            size = self.game.storeManager.shop_size
            self.text = font.render(f"{self.cost}$", True, self.color)
            self.text_rect = self.text.get_rect()
            setattr(self.text_rect, "center", (self.rect.x+size//2, self.rect.y-23))
        
        def draw(self):
            super().draw()
            screen.blit(self.text, self.text_rect)
    
    class TowerProduct(Product):
        def __init__(self, sprite, cost, name):
            super().__init__(sprite, cost)
            self.tower = name
    
        def update(self):
            super().update()
            if self.clicked == True and self.game.player.money >= self.cost:
                if self.game.storeManager.ghostTower != None:
                    self.game.storeManager.ghostTower = None
                else:
                    self.game.storeManager.ghostTower = self.game.towerManager.prew(self.tower, self)
    
    class Tower(Object):
        def __init__(self, parent, sprite, pos, hp, rate, range, strength):
            super().__init__(sprite, pos)
            self.parent = parent
            self.cost = parent.cost
            self.max_hp = hp
            self.rate = rate
            self.range = range
            self.count = 3
            self.strength = strength
            self.prew = False
            
            self.cooldown = 0
            self.hp = self.max_hp
            
            self.alive = True
        
        def death(self):
            pass
        
        def take_damage(self, dmg):
            self.game.soundManager.play("bump")
            self.hp -= dmg
            if self.hp <= 0:
                self.alive = False
        
        def attack(self, target):
            self.cooldown=0
            target.take_damage(self.strength)
        
        def cheak(self):
            damaged = 0
            for e in self.game.enemyManager.enemies:
                if pygame.Vector2(self.rect.center).distance_to(e.rect.center) <= self.range+e.rect.width//2 and damaged <= self.count:
                    damaged += 1
                    self.attack(e)
        
        def sell(self, per):
            self.alive = False
            self.game.player.money += round(self.parent.cost * per * 0.01)
        
        def update(self):
            input = self.game.input
            super().update()
            if self.cooldown < self.rate:
                self.cooldown+=1
            else:
                self.cheak()
            if self.hovered == True:
                health = round(max(0, self.hp*10))/10
                self.game.infoBar.text = f"{health:g}/{self.max_hp} HP"
                if (input.mouse_down(3) and input.key_down(pygame.K_LCTRL)) or input.mouse_pressed(3):
                    self.sell(50)
        
        def radius(self):
            gfxdraw.aacircle(screen, self.rect.centerx, self.rect.centery, self.range, (255, 255, 255))
        
        def draw(self):
            super().draw()
            if self.hovered == True:
                self.radius()
    
    class Enemy(Object):
        def __init__(self, sprite, pos, budget, cost, hp, rate, speed, strength):
            super().__init__(sprite, pos)
            self.budget = budget
            self.cost = cost
            self.max_hp = hp
            self.rate = rate
            self.speed = speed
            self.strength = strength
            
            self.cooldown = 0
            self.hp = self.max_hp
            
            self.alive = True
            
        def move(self):
            target = None
            for t in self.game.towerManager.towers:
                if self.rect.colliderect(t.rect):
                    target = t
                    break
            if target == None:
                self.rect.x -= self.speed # Movment
            elif self.cooldown==self.rate:
                self.attack(target)
        
        def attack(self, tower):
            self.cooldown = 0
            tower.take_damage(self.strength)
        
        def death(self):
            self.game.player.money += self.cost
        
        def take_damage(self, dmg):
            self.game.soundManager.play("bump")
            self.hp -= dmg
            if self.hp <= 0:
                self.alive = False
        
        def damage_player(self):
            self.game.player.health -= 1
            self.game.player.money += 30
            
            self.alive = False
        
        def update(self):
            super().update()
            if self.cooldown < self.rate:
                self.cooldown+=1
            self.move()
            if self.hovered == True:
                health = round(max(0, self.hp*10))/10
                self.game.infoBar.text = f"{health:g}/{self.max_hp} HP"
            if self.clicked == True:
                self.take_damage(self.game.player.strength)

    class Dog(Enemy):
        def __init__(self, pos):
            sprite = Sprite(game.pathManager.TEXTURES / "Dog1.png", (60, 60))
            sprite.image = pygame.transform.flip(sprite.image, True, False)
            super().__init__(sprite, pos, budget=1, cost=2, hp=2, rate=FPS, speed=1, strength=1)
    
    class FastDog(Enemy):
        def __init__(self, pos):
            sprite = Sprite(game.pathManager.TEXTURES / "Dog1.png", (45, 45))
            sprite.image = pygame.transform.flip(sprite.image, True, False)
            super().__init__(sprite, pos, budget=3, cost=3, hp=1, rate=FPS/3, speed=4, strength=0.25)
    
    #      = Attack Cat =
    class AttackCat(Tower):
        def __init__(self, parent, pos):
            sprite = Sprite(game.pathManager.TEXTURES / "Cat1.png", (60, 60))
            super().__init__(parent, sprite, pos, hp=3, rate=FPS*2, range=152, strength=1)
    
    class AttackCatProduct(TowerProduct):
        def __init__(self):
            sprite = Sprite(game.pathManager.TEXTURES / "Cat1.png", (90, 90))
            super().__init__(sprite, cost=10, name="Cat")
    
    #      = DefenseCat Cat =
    class DefenseCat(Tower):
        def __init__(self, parent, pos):
            sprite = Sprite(game.pathManager.TEXTURES / "Cat2.png", (60, 60))
            sprite.image = pygame.transform.flip(sprite.image, True, False)
            super().__init__(parent, sprite, pos, hp=15, rate=0, range=0, strength=0)
    
    class DefenseCatProduct(TowerProduct):
        def __init__(self):
            sprite = Sprite(game.pathManager.TEXTURES / "Cat2.png", (90, 90))
            super().__init__(sprite, cost=5, name="DefenseCat")

    game.enemyManager.init(Dog, "Dog")
    game.enemyManager.init(FastDog, "FastDog")
    
    game.towerManager.init(AttackCat, "Cat")
    game.storeManager.init(AttackCatProduct())
    
    game.towerManager.init(DefenseCat, "DefenseCat")
    game.storeManager.init(DefenseCatProduct())