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
        
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
        
    def draw(self, screen):
        # Draw enemy
        color = (255, 0, 0)  # Red for enemy
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 15)
        
        # Draw health bar
        health_ratio = self.health / self.max_health
        bar_width = 30
        bar_height = 5
        green_width = int(bar_width * health_ratio)
        
        # Background (red) health bar
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x - bar_width//2, self.y - 25,
                         bar_width, bar_height))
        # Foreground (green) health bar
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.x - bar_width//2, self.y - 25,
                         green_width, bar_height))
        
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
