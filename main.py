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
        
        # Load background
        try:
            self.background = pygame.image.load(os.path.join('assets', 'game_bg.png'))
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
        except:
            self.background = pygame.Surface((screen.get_width(), screen.get_height()))
            self.background.fill((20, 20, 40))
        
        # Stage configurations
        self.stage_paths = {
            1: [  # Basic path (Foundation Stage)
                (-50, 360), (150, 360), (150, 150), (450, 150),
                (450, 570), (750, 570), (750, 360), (900, 360)
            ],
            2: [  # Zigzag path (Core Formation Stage)
                (-50, 150), (200, 150), (200, 570), (400, 570),
                (400, 150), (600, 150), (600, 570), (900, 570)
            ],
            3: [  # Spiral path (Nascent Soul Stage)
                (-50, 360), (200, 360), (200, 150), (700, 150),
                (700, 570), (150, 570), (150, 250), (900, 250)
            ],
            4: [  # Double loop (Soul Formation Stage)
                (-50, 250), (200, 250), (200, 150), (400, 150),
                (400, 350), (200, 350), (200, 550), (400, 550),
                (400, 350), (600, 350), (600, 250), (900, 250)
            ],
            5: [  # Cross path (Golden Core Stage)
                (-50, 150), (900, 150),  # Top horizontal
                (-50, 570), (900, 570),  # Bottom horizontal
                (425, 50), (425, 670)    # Vertical middle
            ],
            6: [  # Diamond path (Void Stage)
                (-50, 360), (200, 150), (425, 50), (650, 150),
                (800, 360), (650, 570), (425, 670), (200, 570),
                (-50, 360)
            ],
            7: [  # Figure 8 (Immortal Stage)
                (-50, 360), (150, 150), (425, 360), (700, 150),
                (900, 360), (700, 570), (425, 360), (150, 570),
                (-50, 360)
            ],
            8: [  # Final challenge (Heaven Stage)
                (-50, 50), (900, 50),    # Top
                (900, 670), (-50, 670),  # Bottom
                (-50, 360), (900, 360),  # Middle
                (425, 50), (425, 670)    # Vertical
            ]
        }
        
        # Stage configurations with cultivation themes
        self.stage_configs = {
            1: {  # Foundation Stage
                "name": "Qi Gathering Grounds",
                "waves": [
                    {"num_enemies": 8, "enemy_level": 1},   # Basic enemies
                    {"num_enemies": 10, "enemy_level": 1},
                    {"num_enemies": 12, "enemy_level": 2},
                    {"num_enemies": 15, "enemy_level": 2},
                    {"num_enemies": 1, "enemy_level": 3}    # Boss wave
                ],
                "path": self.stage_paths[1]
            },
            2: {  # Core Formation Stage
                "name": "Spirit Realm Trials",
                "waves": [
                    {"num_enemies": 12, "enemy_level": 2},
                    {"num_enemies": 15, "enemy_level": 2},
                    {"num_enemies": 18, "enemy_level": 3},
                    {"num_enemies": 20, "enemy_level": 3},
                    {"num_enemies": 1, "enemy_level": 4}    # Boss wave
                ],
                "path": self.stage_paths[2]
            },
            3: {  # Nascent Soul Stage
                "name": "Soul Formation Path",
                "waves": [
                    {"num_enemies": 15, "enemy_level": 3},
                    {"num_enemies": 18, "enemy_level": 3},
                    {"num_enemies": 20, "enemy_level": 4},
                    {"num_enemies": 25, "enemy_level": 4},
                    {"num_enemies": 2, "enemy_level": 5}    # Dual boss wave
                ],
                "path": self.stage_paths[3]
            },
            4: {  # Soul Severing Stage
                "name": "Mortal Severance Realm",
                "waves": [
                    {"num_enemies": 20, "enemy_level": 4},
                    {"num_enemies": 25, "enemy_level": 4},
                    {"num_enemies": 25, "enemy_level": 5},
                    {"num_enemies": 30, "enemy_level": 5},
                    {"num_enemies": 2, "enemy_level": 6}    # Dual boss wave
                ],
                "path": self.stage_paths[4]
            },
            5: {  # Golden Core Stage
                "name": "Core Ascension Path",
                "waves": [
                    {"num_enemies": 25, "enemy_level": 5},
                    {"num_enemies": 30, "enemy_level": 5},
                    {"num_enemies": 30, "enemy_level": 6},
                    {"num_enemies": 35, "enemy_level": 6},
                    {"num_enemies": 3, "enemy_level": 7}    # Triple boss wave
                ],
                "path": self.stage_paths[5]
            },
            6: {  # Void Stage
                "name": "Void Transcendence",
                "waves": [
                    {"num_enemies": 30, "enemy_level": 6},
                    {"num_enemies": 35, "enemy_level": 6},
                    {"num_enemies": 35, "enemy_level": 7},
                    {"num_enemies": 40, "enemy_level": 7},
                    {"num_enemies": 3, "enemy_level": 8}    # Triple boss wave
                ],
                "path": self.stage_paths[6]
            },
            7: {  # Immortal Stage
                "name": "Immortal Ascension",
                "waves": [
                    {"num_enemies": 35, "enemy_level": 7},
                    {"num_enemies": 40, "enemy_level": 7},
                    {"num_enemies": 40, "enemy_level": 8},
                    {"num_enemies": 45, "enemy_level": 8},
                    {"num_enemies": 4, "enemy_level": 9}    # Quad boss wave
                ],
                "path": self.stage_paths[7]
            },
            8: {  # Heaven Stage
                "name": "Heaven Tribulation",
                "waves": [
                    {"num_enemies": 40, "enemy_level": 8},
                    {"num_enemies": 45, "enemy_level": 8},
                    {"num_enemies": 45, "enemy_level": 9},
                    {"num_enemies": 50, "enemy_level": 9},
                    {"num_enemies": 5, "enemy_level": 10}   # Final boss wave
                ],
                "path": self.stage_paths[8]
            }
        }
        
        # Set current stage configuration
        stage_config = self.stage_configs.get(stage_level, self.stage_configs[1])
        self.waves = stage_config["waves"]
        self.enemy_path = stage_config["path"]
        self.stage_name = stage_config["name"]
        
        # Wave management
        self.wave_timer = 0
        self.wave_cooldown = 1000  # Time between waves in milliseconds
        self.enemies_spawned_this_wave = 0
        self.wave_completed = False
        self.current_wave_data = self.waves[0]
        
        # Enemy wave management
        self.paused = True
        
        # Spawn timer
        self.spawn_timer = 0
        self.spawn_cooldown = 1500  # Time between enemy spawns in milliseconds
        
        self.tower_menu_active = False
        self.tower_buttons = {}
        self.tower_menu_pos = (0, 0)
        self.selected_tower = None
        
    def draw_tower_menu(self, x, y):
        """Draw the tower selection menu at the given position"""
        menu_width = 300
        menu_height = 400
        padding = 10
        
        # Adjust menu position to stay within screen bounds
        menu_x = min(max(x, 0), self.screen.get_width() - menu_width)
        menu_y = min(max(y, 0), self.screen.get_height() - menu_height)
        
        # Draw menu background
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill((50, 50, 50))
        menu_surface.set_alpha(230)  # Slight transparency
        
        # Draw tower options
        font = pygame.font.Font(None, 24)
        y_offset = padding
        button_height = 45
        
        tower_options = [
            ("Qi Condensation", "Basic tower - Cost: 100 Qi Pills"),
            ("Foundation", "Medium range - Cost: 200 Qi Pills"),
            ("Core Formation", "High damage - Cost: 300 Qi Pills"),
            ("Nascent Soul", "Fast attack - Cost: 400 Qi Pills"),
            ("Soul Severing", "Area damage - Cost: 500 Qi Pills"),
            ("Earth Immortal", "Stunning attacks - Cost: 600 Qi Pills"),
            ("Sky Immortal", "Ultimate range - Cost: 800 Qi Pills"),
            ("Heaven Immortal", "Divine power - Cost: 1000 Qi Pills")
        ]
        
        self.tower_buttons = {}  # Store button rectangles
        
        for name, desc in tower_options:
            # Draw button background
            button_rect = pygame.Rect(padding, y_offset, menu_width - 2*padding, button_height)
            pygame.draw.rect(menu_surface, (70, 70, 70), button_rect)
            
            # Draw tower name
            name_text = font.render(name, True, (255, 215, 0))
            menu_surface.blit(name_text, (button_rect.x + 5, y_offset + 5))
            
            # Draw description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(desc, True, (200, 200, 200))
            menu_surface.blit(desc_text, (button_rect.x + 5, y_offset + 25))
            
            # Store button position relative to menu
            self.tower_buttons[name] = button_rect.move(menu_x, menu_y)
            
            y_offset += button_height + 5
        
        # Draw close button
        close_rect = pygame.Rect(menu_width - 30, 5, 25, 25)
        pygame.draw.rect(menu_surface, (150, 50, 50), close_rect)
        close_text = font.render("×", True, (255, 255, 255))
        menu_surface.blit(close_text, (menu_width - 25, 5))
        self.tower_buttons["close"] = close_rect.move(menu_x, menu_y)
        
        # Draw menu on screen
        self.screen.blit(menu_surface, (menu_x, menu_y))
        self.tower_menu_active = True
        self.tower_menu_pos = (menu_x, menu_y)

    def handle_tower_menu_click(self, pos):
        """Handle clicks on the tower selection menu"""
        if not self.tower_menu_active:
            return False
            
        for tower_name, button_rect in self.tower_buttons.items():
            if button_rect.collidepoint(pos):
                if tower_name == "close":
                    self.tower_menu_active = False
                else:
                    # Get tower cost
                    tower_costs = {
                        "Qi Condensation": 100,
                        "Foundation": 200,
                        "Core Formation": 300,
                        "Nascent Soul": 400,
                        "Soul Severing": 500,
                        "Earth Immortal": 600,
                        "Sky Immortal": 800,
                        "Heaven Immortal": 1000
                    }
                    
                    cost = tower_costs[tower_name]
                    
                    # Check if player can afford tower
                    if self.currency >= cost:
                        self.currency -= cost
                        self.selected_tower = tower_name
                        self.tower_menu_active = False
                        return True
                    else:
                        # Show insufficient funds message
                        print("Insufficient Qi Pills!")
                return True
        return False

    def handle_click(self, pos):
        """Handle mouse clicks"""
        if self.tower_menu_active:
            # Handle tower menu clicks
            if self.handle_tower_menu_click(pos):
                return
            
        # Check if click is on a valid tower placement spot
        if self.is_valid_placement(pos):
            if self.selected_tower:
                # Place selected tower
                self.place_tower(pos[0], pos[1], self.selected_tower)
                self.selected_tower = None
            else:
                # Show tower menu
                self.draw_tower_menu(pos[0], pos[1])

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
                dist = self.point_to_line_distance((x, y), (x1, y1), (x2, y2))
                if dist < 30:  # Minimum distance from path
                    can_place = False
                    break
                    
            if can_place:
                tower = Tower(self.selected_tower_type, x, y)
                self.towers.append(tower)
                self.currency -= cost
                return True
        return False
        
    def place_tower(self, x, y, tower_name):
        """Add a tower at the specified position if there's enough currency"""
        # Get tower cost
        tower_costs = {
            "Qi Condensation": 100,
            "Foundation": 200,
            "Core Formation": 300,
            "Nascent Soul": 400,
            "Soul Severing": 500,
            "Earth Immortal": 600,
            "Sky Immortal": 800,
            "Heaven Immortal": 1000
        }
        
        cost = tower_costs[tower_name]
        
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
                dist = self.point_to_line_distance((x, y), (x1, y1), (x2, y2))
                if dist < 30:  # Minimum distance from path
                    can_place = False
                    break
                    
            if can_place:
                tower = Tower(tower_name, x, y)
                self.towers.append(tower)
                self.currency -= cost
                return True
        return False
        
    def is_valid_placement(self, pos):
        """Check if a tower can be placed at the given position"""
        x, y = pos
        
        # Check if position is within screen bounds
        if x < 0 or x > self.screen.get_width() or y < 0 or y > self.screen.get_height():
            return False
            
        # Check distance from other towers
        for tower in self.towers:
            dx = tower.x - x
            dy = tower.y - y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 50:  # Minimum distance between towers
                return False
                
        # Check distance from path
        for i in range(len(self.enemy_path) - 1):
            x1, y1 = self.enemy_path[i]
            x2, y2 = self.enemy_path[i + 1]
            # Calculate distance from point to line segment
            dist = self.point_to_line_distance((x, y), (x1, y1), (x2, y2))
            if dist < 30:  # Minimum distance from path
                return False
                
        return True
        
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate the distance from a point to a line segment"""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate the length of the line segment
        line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_length == 0:
            return math.sqrt((x - x1)**2 + (y - y1)**2)
            
        # Calculate the distance from point to line
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length**2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return math.sqrt((x - proj_x)**2 + (y - proj_y)**2)
        
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
                
    def draw(self, screen):
        """Draw all game elements"""
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw enemy path
        for i in range(len(self.enemy_path) - 1):
            pygame.draw.line(screen, (100, 100, 100), 
                           self.enemy_path[i], self.enemy_path[i + 1], 2)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Draw HUD
        self.draw_hud(screen)
        
        if self.tower_menu_active:
            self.draw_tower_menu(self.tower_menu_pos[0], self.tower_menu_pos[1])
        
    def draw_hud(self, screen):
        """Draw heads-up display with game information"""
        # Setup font
        font = pygame.font.Font(None, 32)
        padding = 10
        line_height = 30
        y_pos = padding
        
        # Draw currency with gold color for spirit stones
        qi_text = font.render(f"Qi Pills: {self.currency}", True, (200, 255, 200))
        spirit_text = font.render(f"Spirit Stones: {self.spirit_stones}", True, (255, 215, 0))
        screen.blit(qi_text, (padding, y_pos))
        y_pos += line_height
        screen.blit(spirit_text, (padding, y_pos))
        
        # Draw lives with red color
        y_pos += line_height
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 100, 100))
        screen.blit(lives_text, (padding, y_pos))
        
        # Draw wave progress with cyan color
        y_pos += line_height
        wave_text = font.render(f"Wave: {self.wave + 1}/{len(self.waves)}", True, (100, 255, 255))
        screen.blit(wave_text, (padding, y_pos))
        
        # Draw selected tower info at bottom
        if self.selected_tower:
            tower_cost = 0
            tower_costs = {
                "Qi Condensation": 100,
                "Foundation": 200,
                "Core Formation": 300,
                "Nascent Soul": 400,
                "Soul Severing": 500,
                "Earth Immortal": 600,
                "Sky Immortal": 800,
                "Heaven Immortal": 1000
            }
            tower_cost = tower_costs[self.selected_tower]
            tower_text = font.render(f"Selected: {self.selected_tower} ({tower_cost} Qi)", True, (200, 200, 255))
            screen.blit(tower_text, (padding, screen.get_height() - 40))

class Game:
    def __init__(self, screen, selected_stage):
        self.screen = screen
        self.selected_stage = selected_stage
        
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
                        self.game_manager.handle_click(mouse_pos)
            
            # Update game state
            self.game_manager.update()
            
            # Draw everything
            self.screen.fill((0, 0, 0))
            self.game_manager.draw(self.screen)
            
            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), self.back_btn)
            self.screen.blit(self.back_text, self.back_text_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        return self.game_state
        
    def draw(self):
        # Draw background
        self.screen.blit(self.game_manager.background, (0, 0))
        
        # Draw back button
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_btn)
        self.screen.blit(self.back_text, self.back_text_rect)
        
        # Draw game objects through game manager
        self.game_manager.draw(self.screen)

if __name__ == "__main__":
    # If run directly, start with stage 1
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Cultivation Tower Defense - Stage 1")
    game = Game(screen, 1)
    game.run()
