import pygame
import sys
from pathlib import Path
from classes import *
from managers import *
from config import *
from entity import *

pygame.display.set_caption("Kot Defense v" + version)
clock = pygame.time.Clock()

# Player
class Player:
    def __init__(self):
        self.health = 9
        self.money = 30
        self.strength = 0.1


# Scenes
class GameScene:
    def __init__(self, game):
        self.game = game 
        self.objectManager = ObjectManager(self.game)
        self.textManager = TextManager(self.game)
        skipImg = Sprite(self.game.pathManager.TEXTURES / "skip.png", (100, 100))
        skipImg.image = pygame.transform.flip(skipImg.image, True, False)
        self.skip = self.objectManager.new_object(skipImg, (WIDTH-125, HEIGHT-125))
        
        self.cell1 = (101, 155, 94)
        self.cell2 = (93,143,86)# (94,136,89)
        
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.health = self.textManager.make(self.font, "Health: -", (255, 255, 255), (5, 2))
        self.money = self.textManager.make(self.font, "Money: -", (255, 255, 255), (5, 26))
        self.wave = self.textManager.make(self.font, "Press the red button to start", (255, 255, 255), (5, 28+22))
    
    def update(self):
        self.objectManager.update()
        self.game.waveManager.update()
        self.game.enemyManager.update()
        self.game.towerManager.update()
        self.game.storeManager.update()
        self.health.text = f"Health: {str(self.game.player.health)}"
        self.money.text = f"Money: {str(self.game.player.money)}"
        
        # RPC
        waveText = f"Mega Wave: {str(self.game.waveManager.wave)}" if self.game.waveManager.wave % self.game.waveManager.mega_wave == 0 else f"Wave: {str(self.game.waveManager.wave)}"
        rpc.update(f"{self.game.player.money} 💵 {self.game.player.health} ❤", waveText)
        
        
        if self.game.waveManager.wave > 0:
            self.wave.text = waveText
        if self.skip.clicked == True and len(self.game.enemyManager.enemies) == 0:
            self.game.waveManager.next_wave()
    
    def background(self):
        cell_size = 60
        
        width_cells  = WIDTH//cell_size
        height_cells = HEIGHT//cell_size
        
        offsets = (-cell_size//2, -cell_size//2)
        for row in range(height_cells):
            for col in range(width_cells+2):
                color = self.cell1 if (row+col) % 2 == 0 else self.cell2
                
                pygame.draw.rect(screen, color, (col*cell_size+offsets[0], row*cell_size+offsets[1], cell_size, cell_size))
    
    def draw(self):
        screen.fill((101, 155, 94))
        self.background()
        
        pygame.draw.rect(screen, (40, 63, 59), (0, HEIGHT-downbar, WIDTH, downbar))
        pygame.draw.rect(screen, (40, 63, 59), (0, upbar, WIDTH, 3))
        
        self.objectManager.draw()
        self.game.enemyManager.draw()
        self.game.towerManager.draw()
        self.game.storeManager.draw()
        self.textManager.draw()
        
        self.game.infoBar.draw(self.game.input.mouse_pos)

class MainMenu:
    def __init__(self, game):
        self.game = game 
        self.objectManager = ObjectManager(self.game)
        self.textManager = TextManager(self.game)
        playImg = Sprite(self.game.pathManager.TEXTURES / "play.png", (300,300))
        self.play = self.objectManager.new_object(playImg, (WIDTH/2-300/2, HEIGHT/2-200/2))
        self.font = pygame.font.SysFont("Arial", 80)
        self.font2 = pygame.font.SysFont("Arial", 50)
        
        self.welcome = self.textManager.make(self.font, "Kot Defense REWORK", (255, 255, 255), (WIDTH/2, 20), "midtop")
        self.info = self.textManager.make(self.font2, f"welcome to {version} version", (230, 230, 230), (WIDTH/2, 100), "midtop")
    
    def update(self):
        self.objectManager.update()
        if self.play.clicked == True:
            self.game.sceneManager.go("mainGame")
            
    
    def draw(self):
        screen.fill((101, 155, 94))
           
        self.objectManager.draw()
        self.textManager.draw()

# Game
class Game:
    def __init__(self):
        self.running = True
        
        # Managers
        self.input = InputManager()
        self.pathManager = PathManager()
        self.player = Player()
        self.sceneManager = SceneManager()
        self.soundManager = SoundManager(self)
        
        self.enemyManager = EnemyManager(self)
        self.towerManager = TowerManager(self)
        self.storeManager = StoreManager(self)
        self.waveManager = WaveManager(self)
        
        self.infoBar = InfoBar()
        
        self.sounds_init()
        
        load_entity(self)
        
        self.sceneManager.init(MainMenu(self), "mainMenu")
        self.sceneManager.init(GameScene(self), "mainGame")
        
        self.sceneManager.go("mainMenu")
        self.loop()
    
    def sounds_init(self):
        pm = self.pathManager # Чтобы не писать миллион писек
        self.soundManager.init(pm.AUDIO / "bump.mp3", "bump")
    
    def update(self):
        events = pygame.event.get()
        self.input.update(events)
        self.infoBar.text = ""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.sceneManager.curent.update()
    
    def draw(self):
        self.sceneManager.curent.draw()
    
    def loop(self):
        while self.running:
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(FPS)

rpc = RPC()
game = Game()
rpc.stop()