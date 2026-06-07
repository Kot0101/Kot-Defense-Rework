import pygame, random, time, threading, queue
from pathlib import Path
from config import *
from classes import *

# Core
if phone == False:
    from pypresence import Presence
    class RPC:
        def __init__(self):
            self.connected = False
            self.running = True
            
            self.text = ""
            self.small_text = ""
            self.queue = queue.Queue()
            self.CLIENT_ID = 1210980897281802330
            
            self.last_data = None
            
            self.start()
            self.update()
        
        def worker(self):
            while self.running:
                if not self.connected:
                    try:
                        self.RPC = Presence(self.CLIENT_ID)
                        self.RPC.connect()
                        self.start_time = int(time.time())
                        
                        self.connected = True
                    except Exception as e:
                        time.sleep(5)
                        continue
                try:
                    data = self.queue.get(timeout=1)
                    
                    if data == self.last_data:
                        continue
                    
                    self.last_data = data
                    text, small_text = data
                    self.text = text
                    self.small_text = small_text
                    self.RPC.update(state=small_text, details=text, large_image="kotdefense", large_text="Kot Defense")
                except queue.Empty:
                    pass
        
        def update(self, text=None, small_text=None):
            self.queue.put((
                text,
                small_text
            ))
        
        def start(self):
            self.threading = threading.Thread(target=self.worker, daemon=True)
            self.threading.start()
            
        def stop(self):
            self.running = False
else:
    class RPC:
        def __init__(self):
            self.connected = False
            self.running = True
            
            self.text = ""
            self.small_text = ""
            self.queue = queue.Queue()
            self.CLIENT_ID = 1210980897281802330
            
            self.last_data = None
        
        def worker(self):
            pass
        
        def update(self, text=None, small_text=None):
            pass
        
        def start(self):
            pass
            
        def stop(self):
            pass


class PathManager:
    def __init__(self):
        self.DATA = Path("Data")
        
        self.TEXTURES = self.DATA / "textures"
        self.AUDIO = self.DATA / "audio"

class InputManager:
    def __init__(self):
        self.down, self.pressed, self.released = set(), set(), set()
        self.m_down, self.m_pressed, self.m_released = set(), set(), set()
        self.mouse_pos = (0, 0)

    def update(self, events):
        self.pressed.clear(); self.released.clear()
        self.m_pressed.clear(); self.m_released.clear()
        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.KEYUP):
                k = getattr(e, 'key', None)
                if k is None:
                    continue
                if e.type == pygame.KEYDOWN:
                    if k not in self.down:
                        self.pressed.add(k)
                    self.down.add(k)
                else:
                    self.down.discard(k)
                    self.released.add(k)
            elif e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                b = getattr(e, 'button', None)
                if b is None:
                    continue
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if b not in self.m_down:
                        self.m_pressed.add(b)
                    self.m_down.add(b)
                else:
                    self.m_down.discard(b)
                    self.m_released.add(b)
            elif e.type == pygame.MOUSEMOTION:
                self.mouse_pos = getattr(e, 'pos', self.mouse_pos)

    key_down = lambda s, k: k in s.down
    key_pressed = lambda s, k: k in s.pressed
    key_released = lambda s, k: k in s.released
    mouse_down = lambda s, b: b in s.m_down
    mouse_pressed = lambda s, b: b in s.m_pressed
    mouse_released = lambda s, b: b in s.m_released

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.curent = None
    
    def init(self, scene, name):
        self.scenes[name] = scene
    
    def go(self, name):
        self.curent = self.scenes[name]

# Dvizok
class SoundManager:
    def __init__(self, game):
        self.game = game
        self.sounds = {}
        self.localVolume = {}
        
        self.volume = 1
    
    def init(self, path, name, volume=1):
        self.sounds[name] = pygame.mixer.Sound(path)
        self.localVolume[name] = volume
    
    def change_volume(self, name, volume):
        self.sounds[name] = volume
    
    def play(self, name, volume=1, loops=0):
        sound = self.sounds[name]
        # volume - локальный звука * volume - менеджера * volume - фукции. Крч чтобы регулировать почти везде можно было громкость
        sound.set_volume(self.localVolume[name]*self.volume*volume)
        sound.play(loops)
    
    def stop(self, name):
        self.sounds[name].stop()
    
    def pause(self, name):
        self.sounds[name].stop()
    
    def unpause(self, name):
        self.sounds[name].stop()

class ObjectManager:
    def __init__(self, game):
        self.game = game
        self.objects = []
    
    def new_object(self, sprite, pos, anchor="topleft"):
        obj = Object(sprite, pos, anchor)
        obj.game = self.game
        self.objects.append(obj)
        
        return obj
    
    def update(self):
        for obj in self.objects:
            obj.update()
    
    def draw(self):
        for obj in self.objects:
            obj.draw()

class TextManager:
    def __init__(self, game):
        self.game = game
        self.texts = []
    
    def make(self, font, text, color, pos, anchor="topleft"):
        text = Text(font, text, color, pos, anchor)
        self.texts.append(text)
        return text
    
    def draw(self):
        for text in self.texts:
            text.draw()


# Game
class WaveManager:
    def __init__(self, game):
        self.game = game
        self.enemyManager = self.game.enemyManager
        self.active = False
        self.wave = 0
        self.mega_wave = 5
        self.budget = 0
        self.curentBudget = 0
        self.concentration = 25
    
    def next_wave(self):
        self.active = True
        self.wave += 1
        self.budget = round(self.wave*(self.wave*0.35+3)) * (2 if self.game.waveManager.wave % self.game.waveManager.mega_wave == 0 else 1)
        self.curentBudget = self.budget
        print(f"Wave {self.wave} started. Budget [{str(self.budget)}]")
    
    def update(self):
        if self.active == True and self.curentBudget > 0 and len(self.enemyManager.enemies) < self.concentration:
            enemy = self.enemyManager.spawn(self)
            self.curentBudget -= enemy.budget

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemies = []
        self.initEnemies = {}
    
    def draw(self):
        for enemy in self.enemies:
            enemy.draw()
    
    def update(self):
        for enemy in self.enemies:
            enemy.update()
            
            if enemy.rect.x <= -enemy.sprite.scale[0]:
                enemy.damage_player()
            
            if enemy.alive == False:
                enemy.death()
                self.enemies.remove(enemy)
    
    def init(self, enemy, name):
        self.initEnemies[name] = enemy
    
    def spawn(self, wave):
        enemyClass = random.choice(list(self.initEnemies.values()))
        enemy = enemyClass((random.randint(WIDTH, WIDTH+80*3), 0))
        enemy.rect.y = random.randint(upbar, HEIGHT-downbar-enemy.sprite.scale[1])
        enemy.game = self.game
        self.enemies.append(enemy)
        return enemy

class StoreManager:
    def __init__(self, game):
        self.game = game
        self.spacing = 10
        self.shop_size = 90
        self.font = pygame.font.SysFont("Arial", 40)
        
        self.startPos = (10, HEIGHT-downbar*0.5+15)
        self.ghostTower = None
        
        self.products = []
    
    def init(self, product):
        self.products.append(product)
        product.game = self.game
        self.restore()
    
    def restore(self):
        x=self.startPos[0]
        y=self.startPos[1]
        self.products.sort(key=lambda cls: cls.cost)
        for product in self.products:
            product.rect.midleft = (x, y)
            product.render(self.font)
            x+=self.shop_size+self.spacing
    
    def draw(self):
        for product in self.products:
            product.draw()
        if self.ghostTower:
            if self.ghostTower.error == True:
                self.ghostTower.sprite.image = self.ghostTower.sprite.error_image
            else:
                self.ghostTower.sprite.image = self.ghostTower.sprite.original_image
            self.ghostTower.draw()
            self.ghostTower.radius()
    
    def snap(self, pos):
        GRID_SIZE = 60
        x = round(pos[0]/GRID_SIZE)*GRID_SIZE
        y = round(pos[1]/GRID_SIZE)*GRID_SIZE
        
        return (x, y)
    
    def update(self):
        for product in self.products:
            product.update()
        if self.ghostTower != None:
            self.ghostTower.rect.center = self.snap(self.game.input.mouse_pos)
            tower_collides = any(self.ghostTower.rect.colliderect(t.rect) for t in self.game.towerManager.towers if t != self.ghostTower)
            enemy_collides = any(self.ghostTower.rect.colliderect(e.rect) for e in self.game.enemyManager.enemies)
            if self.ghostTower.rect.y >= HEIGHT-downbar-self.ghostTower.rect.height+1 or self.ghostTower.rect.y <= upbar-1 or tower_collides or enemy_collides:
                self.ghostTower.error = True
            else:
                self.ghostTower.error = False
                if self.game.input.mouse_down(1) and self.game.player.money >= self.ghostTower.parent.cost:
                    self.game.player.money -= self.ghostTower.parent.cost
                    self.game.towerManager.spawn(self.ghostTower.parent.tower, self.ghostTower.rect.center, self.ghostTower.parent)
                    if self.game.player.money >= self.ghostTower.parent.cost and self.game.input.key_down(pygame.K_LCTRL):
                        return
                    self.ghostTower = None 

class TowerManager:
    def __init__(self, game):
        self.game = game
        self.towers = []
        self.initTowers = {}
    
    def draw(self):
        for tower in self.towers:
            tower.draw()
    
    def update(self):
        for tower in self.towers:
            tower.update()
            
            if tower.alive == False:
                tower.death()
                self.towers.remove(tower)
    
    def init(self, tower, name):
        self.initTowers[name] = tower
    
    def spawn(self, name, pos, parent):
        tower = self.initTowers[name](parent, pos)
        tower.rect.center = pos
        tower.game = self.game
        self.towers.append(tower)
        return tower
    
    def prew(self, name, parent):
        tower = self.initTowers[name](parent, (0,0))
        tower.game = self.game
        tower.prew = True
        tower.sprite.original_image = tower.sprite.image.copy()
        tower.sprite.original_image.set_alpha(120)
        tower.sprite.error_image    = tower.sprite.original_image.copy()
        tower.sprite.error_image.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        
        return tower