import pygame
import os
from enum import Enum
import random
import math
from .currency import Currency
from .currency_drop import CurrencyDrop

class EnemyType(Enum):
    MINION = 1
    WARRIOR = 2
    BOSS = 3

class Enemy:
    def __init__(self, x, y, path, level=1):
        self.x = x
        self.y = y
        self.path = path
        self.path_index = 0
        self.move_count = 0
        self.level = level
        
        # Load and setup sprite animation
        try:
            sprite_sheet = pygame.image.load(os.path.join('assets', 'monster.gif'))
            # If it's a GIF, convert it for better performance
            sprite_sheet = sprite_sheet.convert_alpha()
            
            # Setup animation frames
            self.frames = []
            frame_width = sprite_sheet.get_width()
            frame_height = sprite_sheet.get_height()
            self.frames.append(sprite_sheet)  # For GIF, we use the whole image
            
            # Scale the sprite (adjust size as needed)
            scale = 0.25  # Reduced from 0.5 to 0.25 to make monster 50% smaller
            self.frame_width = int(frame_width * scale)
            self.frame_height = int(frame_height * scale)
            self.frames = [pygame.transform.scale(frame, (self.frame_width, self.frame_height)) 
                         for frame in self.frames]
            
            # Animation variables
            self.current_frame = 0
            self.animation_speed = 0.2  # Adjust this to change animation speed
            self.animation_time = 0
            
        except Exception as e:
            print(f"Error loading enemy sprite: {e}")
            # Fallback to a simple shape if sprite loading fails
            self.frames = None
            self.frame_width = 30
            self.frame_height = 30
        
        # Enemy types and their base stats
        self.enemy_types = {
            "MINION": {"health": 100, "speed": 2, "damage": 10},
            "WARRIOR": {"health": 150, "speed": 1.5, "damage": 15},
            "BOSS": {"health": 300, "speed": 1, "damage": 25}
        }
        
        # Set enemy type based on level
        if level <= 3:
            self.type = "MINION"
        elif level <= 6:
            self.type = "WARRIOR"
        else:
            self.type = "BOSS"
            
        self.setup_stats()
        self.reached_end = False

    def setup_stats(self):
        """Set up enemy stats based on type and level"""
        base_stats = self.enemy_types[self.type]
        level_multiplier = 1 + (self.level - 1) * 0.2  # 20% increase per level
        
        self.max_health = int(base_stats["health"] * level_multiplier)
        self.health = self.max_health
        self.speed = base_stats["speed"]
        self.damage = int(base_stats["damage"] * level_multiplier)
        
    def move(self):
        if self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            
            if distance < self.speed:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.reached_end = True
            else:
                # Normalize direction and multiply by speed
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                self.x += dx
                self.y += dy
                
                # Update sprite direction (flip if moving left)
                if self.frames and dx < 0:  # Moving left
                    self.frames = [pygame.transform.flip(frame, True, False) 
                                 for frame in self.frames]
                elif self.frames and dx > 0:  # Moving right
                    self.frames = [pygame.transform.flip(frame, False, False) 
                                 for frame in self.frames]
        
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
        
    def draw(self, screen):
        # Draw the enemy sprite
        if self.frames:
            # Calculate the position to center the sprite
            sprite_x = self.x - self.frame_width // 2
            sprite_y = self.y - self.frame_height // 2
            
            # Update animation
            self.animation_time += self.animation_speed
            self.current_frame = int(self.animation_time) % len(self.frames)
            
            # Draw the current frame
            screen.blit(self.frames[self.current_frame], (sprite_x, sprite_y))
        else:
            # Fallback to drawing a circle if sprite loading failed
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 15)
        
        # Draw health bar
        health_bar_width = 40
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x - health_bar_width/2, 
                         self.y - self.frame_height/2 - 10, 
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x - health_bar_width/2, 
                         self.y - self.frame_height/2 - 10, 
                         health_bar_width * health_ratio, health_bar_height))
        
    def get_drops(self):
        """Get currency drops when enemy is defeated"""
        drops = []
        base_drops = {
            "MINION": {Currency.QI_PILLS: 50, Currency.SPIRIT_STONES: 10},
            "WARRIOR": {Currency.QI_PILLS: 100, Currency.SPIRIT_STONES: 25},
            "BOSS": {Currency.QI_PILLS: 300, Currency.SPIRIT_STONES: 100}
        }
        
        # Get base drops for enemy type
        type_drops = base_drops[self.type]
        
        # Add level bonus (20% more per level)
        level_multiplier = 1 + (self.level - 1) * 0.2
        
        # Create currency drops with scaled amounts
        for currency_type, amount in type_drops.items():
            drops.append(CurrencyDrop(self.x, self.y, currency_type, int(amount * level_multiplier)))
        
        # Chance for immortal essence (only from higher level enemies)
        if self.level >= 5 and random.random() < 0.05:  # Increased chance to 5%
            drops.append(CurrencyDrop(self.x, self.y, Currency.IMMORTAL_ESSENCE, 1))
            
        return drops
