import pygame
import os
import sys
from game_objects import TowerType, Tower, Enemy, Currency
from game_objects.save_manager import SaveManager
import math

from enum import Enum
class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    QUIT = 3
    RETURN_TO_MENU = 4
class GameManager:
    def __init__(self, stage_level, screen):
        self.stage_level = stage_level
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.selected_tower_type = TowerType.QI_CONDENSATION  # Default selected tower
        
        # Load saved currency
        save_data = SaveManager.load_game()
        self.currency = save_data["qi_pills"]
        self.spirit_stones = save_data["spirit_stones"]
        
        self.wave = 0
        self.lives = 20
        self.screen = screen
        
        # Wave management
        self.wave_timer = 0
        self.wave_cooldown = 1000  # Time between waves in milliseconds
        self.enemies_per_wave = 10
        self.enemies_spawned_this_wave = 0
        self.wave_completed = False
        self.waves = [
            {"num_enemies": 10, "enemy_level": 1},  # Wave 1
            {"num_enemies": 15, "enemy_level": 2},  # Wave 2
            {"num_enemies": 20, "enemy_level": 3},  # Wave 3
            # Add more waves as needed
        ]
        self.current_wave_data = self.waves[0]
        
        # Enemy wave management
        self.paused = True
        
        # Enemy path (you can modify this based on your map)
        self.enemy_path = [
            (0, 300),      # Start from left
            (200, 300),    # First turn
            (200, 100),    # Go up
            (400, 100),    # Go right
            (400, 500),    # Go down
            (600, 500),    # Go right
            (600, 300),    # Go up
            (800, 300)     # Exit point
        ]
        
        # Spawn timer
        self.spawn_timer = 0
        self.spawn_cooldown = 1500  # Time between enemy spawns in milliseconds
        
    def add_tower(self, x, y):
        """Add a tower at the specified position if there's enough currency"""
        cost = 100  # Base tower cost
        if self.currency >= cost:
            # Check if tower can be placed (not too close to path or other towers)
            can_place = True
            # Check distance from other towers
            for tower in self.towers:
                dx = tower.x - x
                dy = tower.y - y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 50:  # Minimum distance between towers
                    can_place = False
                    break
                    
            # Check distance from path
            for i in range(len(self.enemy_path) - 1):
                x1, y1 = self.enemy_path[i]
                x2, y2 = self.enemy_path[i + 1]
                # Calculate distance from point to line segment
                dist = point_to_line_distance((x, y), (x1, y1), (x2, y2))
                if dist < 30:  # Minimum distance from path
                    can_place = False
                    break
                    
            if can_place:
                tower = Tower(self.selected_tower_type, x, y)
                self.towers.append(tower)
                self.currency -= cost
                return True
        return False
        
    def spawn_enemy(self):
        # Create enemy at the start of the path
        start_x, start_y = self.enemy_path[0]
        enemy = Enemy(start_x, start_y, self.enemy_path, self.stage_level)
        self.enemies.append(enemy)
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Check if wave is complete
        if len(self.enemies) == 0 and self.enemies_spawned_this_wave >= self.current_wave_data["num_enemies"]:
            if self.wave < len(self.waves) - 1:  # If there are more waves
                self.wave += 1
                self.current_wave_data = self.waves[self.wave]
                self.enemies_spawned_this_wave = 0
                print(f"Starting Wave {self.wave + 1}")
        
        # Spawn enemies for current wave
        if (current_time - self.spawn_timer > self.spawn_cooldown and 
            self.enemies_spawned_this_wave < self.current_wave_data["num_enemies"]):
            self.spawn_enemy()
            self.enemies_spawned_this_wave += 1
            self.spawn_timer = current_time
            
        # Update all game objects
        for tower in self.towers:
            tower.update(self.enemies)
        
        # Update enemies and handle drops
        for enemy in self.enemies[:]:
            enemy.move()
            if enemy.health <= 0:
                # Get drops before removing enemy
                drops = enemy.get_drops()
                for drop in drops:
                    if drop.currency_type == Currency.QI_PILLS:
                        self.currency += drop.amount
                        print(f"Gained {drop.amount} Qi Pills. Total: {self.currency}")
                    elif drop.currency_type == Currency.SPIRIT_STONES:
                        self.spirit_stones += drop.amount
                        print(f"Gained {drop.amount} Spirit Stones. Total: {self.spirit_stones}")
                # Save after gaining currency
                SaveManager.save_game(self.currency, self.spirit_stones)
                self.enemies.remove(enemy)
            elif enemy.reached_end:
                self.enemies.remove(enemy)
                self.lives -= 1  # Decrease lives when enemy reaches end
        
        # Update projectiles and check for hits
        for projectile in self.projectiles[:]:  # Create copy of list for safe removal
            projectile.update()
            # Check for collision with enemies
            for enemy in self.enemies:
                if projectile.check_collision(enemy):
                    enemy.take_damage(projectile.damage)
                    self.projectiles.remove(projectile)
                    break
            # Remove projectiles that are off screen
            if not projectile.is_on_screen():
                self.projectiles.remove(projectile)
                
        # Draw currency info
        font = pygame.font.Font(None, 36)
        qi_text = font.render(f"Qi Pills: {self.currency}", True, (255, 255, 255))
        spirit_text = font.render(f"Spirit Stones: {self.spirit_stones}", True, (255, 215, 0))
        self.screen.blit(qi_text, (10, 50))
        self.screen.blit(spirit_text, (10, 90))
            
    def draw(self, screen):
        # Draw all game objects
        for tower in self.towers:
            tower.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for projectile in self.projectiles:
            projectile.draw(screen)

class Game:
    def __init__(self, screen, selected_stage):
        self.screen = screen
        self.selected_stage = selected_stage
        
        # Load background
        try:
            self.background = pygame.image.load(os.path.join('assets', 'game_bg.png'))
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
        except:
            self.background = pygame.Surface((screen.get_width(), screen.get_height()))
            self.background.fill((20, 20, 40))
        
        # Initialize game state and manager
        self.game_state = GameState.PLAYING
        self.game_manager = GameManager(selected_stage, screen)
        
        # Create back button in top right corner
        self.back_btn = pygame.Rect(screen.get_width() - 220, 20, 200, 50)
        self.back_font = pygame.font.SysFont(None, 32)
        self.back_text = self.back_font.render("Back to Menu", True, (255, 255, 255))
        self.back_text_rect = self.back_text.get_rect(center=self.back_btn.center)
        
    def run(self):
        clock = pygame.time.Clock()
        self.game_state = GameState.PLAYING
        
        while self.game_state == GameState.PLAYING:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return self.game_state
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.RETURN_TO_MENU
                        return self.game_state
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        # Tower selection
                        tower_num = event.key - pygame.K_1
                        self.game_manager.selected_tower_type = list(TowerType)[tower_num]
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check back button
                    if self.back_btn.collidepoint(mouse_pos):
                        self.game_state = GameState.RETURN_TO_MENU
                        return self.game_state
                    
                    # Handle tower placement
                    if event.button == 1:  # Left click
                        cost = 100  # Base tower cost
                        if self.game_manager.currency >= cost:
                            if self.game_manager.add_tower(mouse_pos[0], mouse_pos[1]):
                                self.game_manager.currency -= cost
                                print(f"Placed tower. Remaining Qi Pills: {self.game_manager.currency}")
                        else:
                            print("Not enough Qi Pills!")
            
            # Update game state
            self.game_manager.update()
            
            # Draw everything
            self.screen.fill((0, 0, 0))
            self.game_manager.draw(self.screen)
            
            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), self.back_btn)
            self.screen.blit(self.back_text, self.back_text_rect)
            
            # Draw tower selection info
            font = pygame.font.Font(None, 36)
            tower_text = font.render(f"Selected Tower: {self.game_manager.selected_tower_type.name}", True, (255, 255, 255))
            self.screen.blit(tower_text, (10, self.screen.get_height() - 40))
            
            pygame.display.flip()
            clock.tick(60)
        
        return self.game_state
        
    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw back button
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_btn)
        self.screen.blit(self.back_text, self.back_text_rect)
        
        # Draw game objects through game manager
        self.game_manager.draw(self.screen)
        
        # Draw UI elements
        font = pygame.font.SysFont(None, 32)
        wave_text = font.render(f"Wave: {self.game_manager.wave + 1}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {self.game_manager.lives}", True, (255, 255, 255))
        
        self.screen.blit(wave_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))

def point_to_line_distance(point, line_start, line_end):
    """Calculate distance from point to line segment"""
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Vector from line start to end
    line_vec = (x2 - x1, y2 - y1)
    # Vector from line start to point
    point_vec = (x - x1, y - y1)
    # Length of line
    line_len = math.sqrt(line_vec[0] ** 2 + line_vec[1] ** 2)
    
    if line_len == 0:
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        
    # Project point_vec onto line_vec
    t = max(0, min(1, (point_vec[0] * line_vec[0] + point_vec[1] * line_vec[1]) / (line_len * line_len)))
    
    # Get closest point on line segment
    proj_x = x1 + t * line_vec[0]
    proj_y = y1 + t * line_vec[1]
    
    return math.sqrt((x - proj_x) ** 2 + (y - proj_y) ** 2)

if __name__ == "__main__":
    # If run directly, start with stage 1
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Cultivation Tower Defense - Stage 1")
    game = Game(screen, 1)
    game.run()
