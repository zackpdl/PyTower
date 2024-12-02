import pygame
import os
from .tower import Tower, TowerType
from .enemy import Enemy, EnemyType
from .boss import Boss, BossType

class GameState:
    def __init__(self, stage_level):
        self.stage_level = stage_level
        self.money = 500
        self.wave = 1
        self.score = 0
        self.lives = 20
        
        # Game objects
        self.towers = []
        self.enemies = []
        self.selected_tower_type = TowerType.QI_CONDENSATION
        
        # Wave control
        self.spawn_timer = 0
        self.wave_started = False
        self.enemies_in_wave = 0
        self.base_spawn_delay = 120  # Frames between enemy spawns (2 seconds at 60 FPS)
        self.wave_size = 5  # Base number of enemies per wave
        
        # Boss wave settings
        self.boss_waves = [5, 10, 15, 20, 25]  # Waves that spawn bosses
        self.current_boss = None
        
    def get_current_spawn_delay(self):
        wave_factor = max(0.5, 1 - (self.wave - 1) * 0.1)
        stage_factor = max(0.3, 1 - (self.stage_level - 1) * 0.1)
        return int(self.base_spawn_delay * wave_factor * stage_factor)
        
    def get_current_wave_size(self):
        return self.wave_size + (self.wave - 1) + (self.stage_level - 1) * 2
        
    def spawn_enemy(self):
        # Determine enemy type based on wave and stage
        enemy_type = EnemyType.MORTAL
        if self.wave >= 3:
            enemy_type = EnemyType(min(self.wave // 3, len(EnemyType)))
            
        enemy = Enemy(0, 300, enemy_type, self.stage_level)
        self.enemies.append(enemy)
        
    def spawn_boss(self):
        boss_type = BossType(min(self.stage_level, len(BossType)))
        self.current_boss = Boss(0, 300, boss_type, self.stage_level)
        self.enemies.append(self.current_boss)
        
    def update(self):
        # Wave management
        if not self.enemies and not self.wave_started:
            self.wave_started = True
            self.enemies_in_wave = 0
            self.spawn_timer = 0
            
        # Spawn enemies
        if self.wave_started:
            self.spawn_timer += 1
            if self.spawn_timer >= self.get_current_spawn_delay():
                if self.wave in self.boss_waves and not self.current_boss:
                    self.spawn_boss()
                elif self.enemies_in_wave < self.get_current_wave_size():
                    self.spawn_enemy()
                    self.enemies_in_wave += 1
                    self.spawn_timer = 0
                elif not self.enemies:
                    # Wave completed
                    self.wave_started = False
                    self.wave += 1
                    self.money += 100 * self.wave
                    self.current_boss = None
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.update():  # Returns True if enemy reached the end
                self.lives -= 1
                self.enemies.remove(enemy)
            elif enemy.health <= 0:
                self.money += enemy.reward
                self.score += enemy.reward
                self.enemies.remove(enemy)
        
        # Update towers
        for tower in self.towers:
            tower.update(self.enemies)
            
    def add_tower(self, tower_type, x, y):
        if tower_type.value <= self.stage_level:  # Can only build towers up to current stage
            tower = Tower(tower_type, x, y)
            if tower.properties["cost"] <= self.money:
                self.towers.append(tower)
                self.money -= tower.properties["cost"]
                return True
        return False
        
    def draw(self, screen):
        # Draw all game objects
        for tower in self.towers:
            tower.draw(screen)
            
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Draw UI elements
        self.draw_ui(screen)
        
    def draw_ui(self, screen):
        font = pygame.font.Font(None, 36)
        
        # Draw money
        money_text = font.render(f"Money: {self.money}", True, (255, 255, 255))
        screen.blit(money_text, (10, 10))
        
        # Draw wave
        wave_text = font.render(f"Wave: {self.wave}", True, (255, 255, 255))
        screen.blit(wave_text, (200, 10))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (400, 10))
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (600, 10))
        
        # Draw selected tower info
        tower_text = font.render(f"Selected: {self.selected_tower_type.name}", True, (255, 255, 255))
        screen.blit(tower_text, (10, 550))
