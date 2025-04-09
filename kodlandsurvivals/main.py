# type: ignore
import pgzrun
import pygame
import os
import random
import math
from enum import Enum


WIDTH = 800
HEIGHT = 600
TITLE = "Kodland Survival"


SPAWN_DISTANCE = 800
ENEMY_SPAWN_RATE = 0.5
MAX_ENEMIES = 20
SCALE_FACTOR = 0.3
PROJECTILE_SCALE = 0.15
PLAYER_HEALTH = 100
ENEMY_HEALTH = 30
PROJECTILE_SPEED = 500
PROJECTILE_DAMAGE = 10
PLAYER_INVULNERABILITY_TIME = 0.3 


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    UPGRADE_SELECTION = 3


class UpgradeType(Enum):
    DAMAGE = "Aumentar Dano (+5)"
    HEALTH = "Aumentar Vida (+20)"
    SPEED = "Aumentar Velocidade (+20%)"
    FIRE_RATE = "Aumentar Cadência (+25%)"
    VAMPIRE = "Vampirismo (10% de vida)"

class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.target = None
    
    def follow(self, target):
        self.target = target
        self.offset_x = target.pos[0] - WIDTH // 2
        self.offset_y = target.pos[1] - HEIGHT // 2
    
    def apply(self, pos):
        return (pos[0] - self.offset_x, pos[1] - self.offset_y)

class Projectile:
    def __init__(self, x, y, target_x, target_y):
        if os.path.exists("images/projetil.png"):
            self.sprite = Actor("projetil.png")
            
            orig_width = self.sprite._orig_surf.get_width()
            orig_height = self.sprite._orig_surf.get_height()
            self.sprite._surf = pygame.transform.scale(
                self.sprite._orig_surf,
                (int(orig_width * PROJECTILE_SCALE),
                int(orig_height * PROJECTILE_SCALE)))
            self.sprite.width = int(orig_width * PROJECTILE_SCALE)
            self.sprite.height = int(orig_height * PROJECTILE_SCALE)
            
            
            self.mask = pygame.mask.from_surface(self.sprite._surf)
        else:
            print("AVISO: projetil.png não encontrado - usando fallback")
            self.sprite = Actor('rect')
            self.sprite.width = 10
            self.sprite.height = 5
            self.sprite.color = (255, 255, 0)  
            self.mask = None
        
        self.sprite.x = x
        self.sprite.y = y
        self.width = self.sprite.width
        self.height = self.sprite.height
        
        
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist) * PROJECTILE_SPEED if dist > 0 else 0
        self.vy = (dy / dist) * PROJECTILE_SPEED if dist > 0 else 0
        
        
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.sprite.angle = self.angle
    
    def update(self, dt):
        self.sprite.x += self.vx * dt
        self.sprite.y += self.vy * dt
        
        
        if (self.sprite.x < -50 or self.sprite.x > WIDTH + 50 or
            self.sprite.y < -50 or self.sprite.y > HEIGHT + 50):
            return True  
        return False
    
    def collides_with(self, enemy):
        if not self.mask:
            
            return (abs(self.sprite.x - enemy.sprite.x) < (enemy.width/2 + self.width/2) and
                    abs(self.sprite.y - enemy.sprite.y) < (enemy.height/2 + self.height/2))
        
        
        offset_x = enemy.sprite.x - self.sprite.x
        offset_y = enemy.sprite.y - self.sprite.y
        return self.mask.overlap(enemy.mask, (int(offset_x), int(offset_y))) is not None
    
    def draw(self, camera=None):
        
        rotated_surf = pygame.transform.rotate(self.sprite._orig_surf, self.angle)
        
        if camera:
            
            pos = camera.apply((self.sprite.x - rotated_surf.get_width()/2, 
                             self.sprite.y - rotated_surf.get_height()/2))
            screen.blit(rotated_surf, pos)
        else:
            
            screen.blit(rotated_surf, (self.sprite.x - rotated_surf.get_width()/2,
                                     self.sprite.y - rotated_surf.get_height()/2))

class Player:
    def __init__(self):
        self.sprites = []
        for i in range(1, 4):
            sprite_name = f"player{i}sprite.png"
            if os.path.exists(f"images/{sprite_name}"):
                actor = Actor(sprite_name)
                actor._surf = pygame.transform.scale(actor._orig_surf, 
                    (int(actor._orig_surf.get_width() * SCALE_FACTOR), 
                    int(actor._orig_surf.get_height() * SCALE_FACTOR)))
                actor.width = actor._surf.get_width()
                actor.height = actor._surf.get_height()
                self.sprites.append(actor)
            else:
                print(f"AVISO: Arquivo {sprite_name} não encontrado na pasta images/")
        
        if not self.sprites:
            print("Usando fallback - retângulo vermelho")
            self.sprites = [Actor('rect')]
            self.sprites[0].width = 30 * SCALE_FACTOR
            self.sprites[0].height = 30 * SCALE_FACTOR
            self.sprites[0].color = (255, 0, 0)
        
        self.current_sprite = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        self.speed = 300
        self.pos = [WIDTH//2, HEIGHT//2]
        self.width = self.sprites[0].width
        self.height = self.sprites[0].height
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.invulnerable = False
        self.invulnerability_timer = 0
        self.damage_multiplier = 1.0
        self.vampirism = 0.0  
        self.fire_rate_multiplier = 1.0
        
        for sprite in self.sprites:
            sprite.pos = self.pos
    
    def take_damage(self, amount):
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.invulnerability_timer = PLAYER_INVULNERABILITY_TIME
            return True
        return False
    
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
    
    def update(self, dt, collision_map=None):
        if self.invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.invulnerable = False
        
        move_x = keyboard.d - keyboard.a
        move_y = keyboard.s - keyboard.w
        
        new_pos = [
            self.pos[0] + move_x * self.speed * dt,
            self.pos[1] + move_y * self.speed * dt
        ]
        
        if collision_map is None or self.check_collision(new_pos, collision_map):
            self.pos = new_pos
        
        for sprite in self.sprites:
            sprite.pos = self.pos
        
        if move_x != 0 or move_y != 0:
            self.animate(dt)
        else:
            self.current_sprite = 0
    
    def check_collision(self, new_pos, collision_map):
        x, y = int(new_pos[0]), int(new_pos[1])
        if 0 <= x < collision_map.get_width() and 0 <= y < collision_map.get_height():
            return collision_map.get_at((x, y)) == (0, 0, 0, 255)
        return False
    
    def animate(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
    
    def draw(self, camera=None):
        if len(self.sprites) > 0:
            
            if not self.invulnerable or (self.invulnerability_timer * 10) % 2 < 1:
                if camera:
                    screen.blit(self.sprites[self.current_sprite]._surf, 
                              camera.apply((self.pos[0] - self.width/2, 
                                          self.pos[1] - self.height/2)))
                else:
                    self.sprites[self.current_sprite].draw()
        
        
        health_width = 50
        health_height = 5
        health_x = self.pos[0] - health_width/2
        health_y = self.pos[1] - self.height/2 - 10
        
        if camera:
            screen.draw.filled_rect(
                Rect(camera.apply((health_x, health_y)), (health_width, health_height)),
                (255, 0, 0)
            )
            screen.draw.filled_rect(
                Rect(camera.apply((health_x, health_y)), (health_width * (self.health/self.max_health), health_height)),
                (0, 255, 0)
            )

class Enemy:
    def __init__(self, player_pos, health_multiplier=1.0, speed_multiplier=1.0):
        if os.path.exists("images/enemy.png"):
            self.sprite = Actor("enemy.png")
            self.sprite._surf = pygame.transform.scale(self.sprite._orig_surf, 
                (int(self.sprite._orig_surf.get_width() * SCALE_FACTOR), 
                 int(self.sprite._orig_surf.get_height() * SCALE_FACTOR)))
            self.width = self.sprite._surf.get_width()
            self.height = self.sprite._surf.get_height()
            self.mask = pygame.mask.from_surface(self.sprite._surf)
        else:
            print("AVISO: enemy.png não encontrado - usando fallback")
            self.sprite = Actor('rect')
            self.width = 25 * SCALE_FACTOR
            self.height = 25 * SCALE_FACTOR
            self.sprite.width = self.width
            self.sprite.height = self.height
            self.sprite.color = (255, 165, 0)
            self.mask = None
        
        self.spawn_away_from_player(player_pos)
        self.base_speed = random.uniform(50, 100)
        self.speed = self.base_speed * speed_multiplier
        self.base_health = ENEMY_HEALTH
        self.health = int(self.base_health * health_multiplier)
        self.max_health = self.health
    
    def spawn_away_from_player(self, player_pos):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(SPAWN_DISTANCE, SPAWN_DISTANCE + 100)
        x = player_pos[0] + math.cos(angle) * distance
        y = player_pos[1] + math.sin(angle) * distance
        self.sprite.pos = (x, y)
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
    
    def update(self, player_pos, dt):
        dx = player_pos[0] - self.sprite.x
        dy = player_pos[1] - self.sprite.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            dx, dy = dx/dist, dy/dist
            self.sprite.x += dx * self.speed * dt
            self.sprite.y += dy * self.speed * dt
    
    def draw(self, camera=None):
        if camera:
            screen.blit(self.sprite._surf, 
                       camera.apply((self.sprite.x - self.width/2, 
                                   self.sprite.y - self.height/2)))
        else:
            self.sprite.draw()
        
        
        health_width = 30
        health_height = 3
        health_x = self.sprite.x - health_width/2
        health_y = self.sprite.y - self.height/2 - 5
        
        if camera:
            screen.draw.filled_rect(
                Rect(camera.apply((health_x, health_y)), (health_width, health_height)),
                (255, 0, 0)
            )
            screen.draw.filled_rect(
                Rect(camera.apply((health_x, health_y)), (health_width * (self.health/self.max_health), health_height)),
                (0, 255, 0)
            )

class CustomCursor:
    def __init__(self):
        if os.path.exists("images/cursor.png"):
            self.original_image = pygame.image.load("images/cursor.png").convert_alpha()
            self.scale_factor = 0.07
            self.image = pygame.transform.scale(
                self.original_image,
                (int(self.original_image.get_width() * self.scale_factor),
                 int(self.original_image.get_height() * self.scale_factor))
            )
        else:
            print("AVISO: cursor.png não encontrado - usando fallback")
            self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
            self.image.fill((0, 255, 0, 255))
        
        self.pos = [0, 0]
        pygame.mouse.set_visible(False)
    
    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        smooth_factor = 0.2
        self.pos[0] += (mouse_x - self.pos[0]) * smooth_factor
        self.pos[1] += (mouse_y - self.pos[1]) * smooth_factor
    
    def draw(self):
        screen.blit(self.image, 
                   (self.pos[0] - self.image.get_width()//2,
                    self.pos[1] - self.image.get_height()//2))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 255), hover_color=(150, 150, 255)):
        self.rect = Rect((x - width//2, y - height//2), (width, height))
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontsize=24,
            color="white"
        )
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.is_hovered and click

class Game:
    def __init__(self):
        
        self.music_enabled = True
        self.sound_enabled = True
        self.load_sounds()
        
        
        self.menu_video = None
        self.menu_video_playing = False
        self.menu_video_restart_time = 0
        
        
        if os.path.exists("images/background.png"):
            self.background = pygame.image.load("images/background.png").convert()
            self.background_width = self.background.get_width()
            self.background_height = self.background.get_height()
        else:
            print("AVISO: background.png não encontrado - usando fundo branco")
            self.background = None
        
        if os.path.exists("images/colisaobackground.png"):
            self.collision_map = pygame.image.load("images/colisaobackground.png").convert()
        else:
            print("AVISO: colisaobackground.png não encontrado - sem colisões")
            self.collision_map = None
        
       
        self.camera = Camera()
        self.player = Player()
        self.camera.follow(self.player)
        self.cursor = CustomCursor()
        self.enemies = []
        self.projectiles = []
        
        
        self.spawn_timer = 0
        self.shoot_cooldown = 0
        self.SHOOT_COOLDOWN_TIME = 0.2  
        
        
        self.state = GameState.MENU
        self.wave = 1
        self.enemies_killed = 0
        self.enemies_to_next_wave = 10
        self.available_upgrades = []
        self.difficulty_multiplier = 1.0
        self.wave_in_progress = False
        
        
        self.play_button = Button(WIDTH//2, HEIGHT//2, 200, 50, "Jogar")
        self.music_button = Button(WIDTH//2, HEIGHT//2 + 70, 200, 50, "Desligar Musica")
        self.quit_button = Button(WIDTH//2, HEIGHT//2 + 140, 200, 50, "Sair")
        
        
        if self.music_enabled and hasattr(self, 'background_music'):
            self.background_music.play(-1)  
        
        
        self.load_menu_video() #tentei carregar um video na tela de menu mas nao consegui a tempo
    
    def load_menu_video(self):
        """Tenta carregar o vídeo do menu de forma alternativa"""
        try:
            
            video_path = "video/telamenu.mp4"
            if os.path.exists(video_path):
                
                self.menu_video_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
                
                self.menu_video_image = pygame.image.load(video_path).convert()
                self.menu_video_image = pygame.transform.scale(self.menu_video_image, (WIDTH, HEIGHT))
                self.menu_video_available = True
            else:
                print("AVISO: Vídeo do menu não encontrado")
                self.menu_video_available = False
        except Exception as e:
            print(f"Erro ao carregar vídeo do menu: {e}")
            self.menu_video_available = False
    
    def load_sounds(self):
        
        try:
            
            if os.path.exists("music/background.mp3"):
                self.background_music = pygame.mixer.Sound("music/background.mp3")
                self.background_music.set_volume(0.5)
            else:
                print("AVISO: background.mp3 não encontrado")
            
            
            self.menu_click_sound = self.load_sound("sounds/botaomenu.mp3", volume=0.3)
            self.shoot_sound = self.load_sound("sounds/tiro.mp3", volume=0.2)  # Volume mais baixo
            self.enemy_spawn_sound = self.load_sound("sounds/inimigo.mp3", volume=0.3)
            self.death_sound = self.load_sound("sounds/morte.mp3", volume=0.4)
            
        except Exception as e:
            print(f"Erro ao carregar sons: {e}")
            self.sound_enabled = False
    
    def load_sound(self, path, volume=1.0):
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        print(f"AVISO: {path} não encontrado")
        return None
    
    def play_sound(self, sound):
        if self.sound_enabled and sound:
            sound.play()
    
    def reset(self):
        self.player = Player()
        self.camera.follow(self.player)
        self.enemies = []
        self.projectiles = []
        self.state = GameState.PLAYING
        self.wave = 1
        self.enemies_killed = 0
        self.enemies_to_next_wave = 10
        self.difficulty_multiplier = 1.0
        self.wave_in_progress = False
    
    def spawn_wave(self):
        self.wave_in_progress = True
        num_enemies = min(5 + self.wave, MAX_ENEMIES)
        health_multiplier = 1.0 + (self.wave * 0.1)
        speed_multiplier = 1.0 + (self.wave * 0.05)
        
        for _ in range(num_enemies):
            self.enemies.append(Enemy(
                self.player.pos,
                health_multiplier,
                speed_multiplier
            ))
            self.play_sound(self.enemy_spawn_sound)
    
    def generate_upgrades(self):
        self.available_upgrades = random.sample(list(UpgradeType), 3)
    
    def apply_upgrade(self, upgrade_type):
        if upgrade_type == UpgradeType.DAMAGE:
            self.player.damage_multiplier += 0.5
        elif upgrade_type == UpgradeType.HEALTH:
            self.player.max_health += 20
            self.player.heal(20)
        elif upgrade_type == UpgradeType.SPEED:
            self.player.speed *= 1.2
        elif upgrade_type == UpgradeType.FIRE_RATE:
            self.player.fire_rate_multiplier *= 1.25
        elif upgrade_type == UpgradeType.VAMPIRE:
            self.player.vampirism += 0.1
        
        self.state = GameState.PLAYING
        self.wave += 1
        self.enemies_killed = 0
        self.enemies_to_next_wave = 10 + self.wave * 2
        self.difficulty_multiplier = 1.0 + self.wave * 0.1
        self.spawn_wave()
    
    def update(self, dt):
        self.cursor.update()
        
        
        if self.state in [GameState.PLAYING, GameState.UPGRADE_SELECTION]:
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.state = GameState.MENU
                if self.music_enabled and hasattr(self, 'background_music'):
                    self.background_music.play(-1)
                return
        
        if self.state == GameState.MENU:
            
            self.menu_video_restart_time += dt
            if self.menu_video_restart_time > 10: 
                self.menu_video_restart_time = 0
            
           
            mouse_pos = pygame.mouse.get_pos()
            self.play_button.check_hover(mouse_pos)
            self.music_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)
            
            
            self.music_button.text = "Desligar Musica" if self.music_enabled else "Ligar Musica"
            
            return
        
        elif self.state == GameState.GAME_OVER:
            if keyboard.r:
                self.reset()
            return
        
        elif self.state == GameState.UPGRADE_SELECTION:
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                self.apply_upgrade(self.available_upgrades[0])
            elif keys[pygame.K_2]:
                self.apply_upgrade(self.available_upgrades[1])
            elif keys[pygame.K_3]:
                self.apply_upgrade(self.available_upgrades[2])
            return
        
        
        self.player.update(dt, self.collision_map)
        self.camera.follow(self.player)
        
        
        self.shoot_cooldown -= dt
        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click and self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.SHOOT_COOLDOWN_TIME / self.player.fire_rate_multiplier
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse_x = mouse_x + self.camera.offset_x
            world_mouse_y = mouse_y + self.camera.offset_y
            self.projectiles.append(
                Projectile(self.player.pos[0], self.player.pos[1], 
                          world_mouse_x, world_mouse_y)
            )
            self.play_sound(self.shoot_sound)
        
        
        for proj in self.projectiles[:]:
            if proj.update(dt):
                self.projectiles.remove(proj)
        
        
        enemies_to_remove = []
        projectiles_to_remove = []
        
        for enemy in self.enemies[:]:
            enemy.update(self.player.pos, dt)
            
            
            for proj in self.projectiles[:]:
                if proj.collides_with(enemy):
                    damage = PROJECTILE_DAMAGE * self.player.damage_multiplier
                    if enemy.take_damage(damage):
                        enemies_to_remove.append(enemy)
                        self.enemies_killed += 1
                        
                        
                        if self.player.vampirism > 0:
                            self.player.heal(damage * self.player.vampirism)
                    
                    projectiles_to_remove.append(proj)
                    break
            
            
            if (abs(self.player.pos[0] - enemy.sprite.x) < (self.player.width/2 + enemy.width/2) and
                abs(self.player.pos[1] - enemy.sprite.y) < (self.player.height/2 + enemy.height/2)):
                
                if self.player.take_damage(10):
                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER
                        self.play_sound(self.death_sound)
        
        
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        
        for proj in projectiles_to_remove:
            if proj in self.projectiles:
                self.projectiles.remove(proj)
        
        
        if self.wave_in_progress and len(self.enemies) == 0:
            if self.enemies_killed >= self.enemies_to_next_wave:
                self.generate_upgrades()
                self.state = GameState.UPGRADE_SELECTION
                self.wave_in_progress = False
            else:
                
                remaining_enemies = self.enemies_to_next_wave - self.enemies_killed
                if remaining_enemies > 0:
                    self.spawn_wave()
        
        
        if not self.wave_in_progress and self.state == GameState.PLAYING:
            self.spawn_wave()
    
    def draw_menu(self):
        
        if self.menu_video_available:
            
            screen.blit(self.menu_video_image, (0, 0))
        else:
            #Fundo preto se não houver vídeo
            screen.fill((0, 0, 0))
        
        
        screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (0, 0, 0, 128))
        
        
        screen.draw.text(
            "KODLAND SURVIVAL",
            center=(WIDTH//2, HEIGHT//4),
            fontsize=64,
            color="white"
        )
        screen.draw.text(
            "por Luiz Henrique",
            center=(WIDTH//2, HEIGHT//3),
            fontsize=30,
            color="white"
        )
        
        
        self.play_button.draw()
        self.music_button.draw()
        self.quit_button.draw()
        
        # Instruções
        screen.draw.text(
            "Pressione ESC durante o jogo para voltar ao menu",
            center=(WIDTH//2, HEIGHT - 30),
            fontsize=20,
            color="white"
        )
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
            self.cursor.draw()
            return
        
        if self.background:
            bg_x = -self.camera.offset_x % self.background_width - self.background_width
            bg_y = -self.camera.offset_y % self.background_height - self.background_height
            
            for y in range(0, HEIGHT + self.background_height, self.background_height):
                for x in range(0, WIDTH + self.background_width, self.background_width):
                    screen.blit(self.background, (bg_x + x, bg_y + y))
        else:
            screen.fill("white")
        
        if self.state == GameState.PLAYING:
            self.player.draw(self.camera)
            
            for enemy in self.enemies:
                enemy.draw(self.camera)
            
            for proj in self.projectiles:
                proj.draw(self.camera)
            
            
            screen.draw.filled_rect(Rect((10, 10), (220, 110)), (240, 240, 240, 220))
            screen.draw.text(
                f"Player: ({int(self.player.pos[0])}, {int(self.player.pos[1])})\n"
                f"Vida: {self.player.health}/{self.player.max_health}\n"
                f"Inimigos: {len(self.enemies)}\n"
                f"Wave: {self.wave}\n"
                f"Matados: {self.enemies_killed}/{self.enemies_to_next_wave}",
                topleft=(15, 15),
                color="black"
            )
            screen.draw.text("WASD para mover | Clique para atirar", bottomleft=(10, HEIGHT-10), color="black")
            screen.draw.text("ESC para menu", bottomright=(WIDTH-10, HEIGHT-10), color="black")
        
        elif self.state == GameState.GAME_OVER:
            screen.draw.filled_rect(Rect((WIDTH//2 - 150, HEIGHT//2 - 100), (300, 200)), (50, 50, 50, 200))
            screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=48, color="red")
            screen.draw.text(f"Wave alcancada: {self.wave}", center=(WIDTH//2, HEIGHT//2), fontsize=24, color="white")
            screen.draw.text("Pressione R para reiniciar", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=24, color="white")
        
        elif self.state == GameState.UPGRADE_SELECTION:
            screen.draw.filled_rect(Rect((WIDTH//2 - 200, HEIGHT//2 - 150), (400, 300)), (50, 50, 100, 200))
            screen.draw.text("ESCOLHA UM UPGRADE", center=(WIDTH//2, HEIGHT//2 - 120), fontsize=32, color="white")
            
            for i, upgrade in enumerate(self.available_upgrades):
                y_pos = HEIGHT//2 - 70 + i * 60
                screen.draw.text(
                    f"{i+1}. {upgrade.value}",
                    center=(WIDTH//2, y_pos),
                    fontsize=24,
                    color="yellow" if i == 0 else "cyan" if i == 1 else "magenta"
                )
            screen.draw.text("Pressione 1, 2 ou 3 para selecionar", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=20, color="white")
        
        self.cursor.draw()

def on_mouse_down(pos):
    if game.state == GameState.MENU:
       
        if game.play_button.is_clicked(pos, True):
            game.play_sound(game.menu_click_sound)
            game.reset()
        elif game.music_button.is_clicked(pos, True):
            game.play_sound(game.menu_click_sound)
            game.music_enabled = not game.music_enabled
            if game.music_enabled and hasattr(game, 'background_music'):
                game.background_music.play(-1)
            else:
                pygame.mixer.stop()
        elif game.quit_button.is_clicked(pos, True):
            game.play_sound(game.menu_click_sound)
            pygame.quit()
            exit()


game = Game()

def update(dt):
    game.update(dt)

def draw():
    game.draw()

pgzrun.go()