import pygame
import os
import math
from enum import Enum

# Tower properties for each cultivation stage
TOWER_PROPERTIES = {
    "Qi Condensation": {
        "damage": 10,
        "range": 100,
        "attack_speed": 1.0,
        "cost": 100,
        "color": (100, 200, 255),  # Light blue
        "max_level": 3
    },
    "Foundation": {
        "damage": 15,
        "range": 120,
        "attack_speed": 1.2,
        "cost": 200,
        "color": (150, 150, 255),  # Blue-purple
        "max_level": 3
    },
    "Core Formation": {
        "damage": 25,
        "range": 130,
        "attack_speed": 1.3,
        "cost": 300,
        "color": (200, 100, 255),  # Purple
        "max_level": 3
    },
    "Nascent Soul": {
        "damage": 20,
        "range": 140,
        "attack_speed": 2.0,
        "cost": 400,
        "color": (255, 100, 200),  # Pink
        "max_level": 3
    },
    "Soul Severing": {
        "damage": 40,
        "range": 110,
        "attack_speed": 0.8,
        "cost": 500,
        "color": (255, 50, 50),    # Red
        "max_level": 3
    },
    "Earth Immortal": {
        "damage": 50,
        "range": 150,
        "attack_speed": 1.0,
        "cost": 600,
        "color": (50, 255, 50),    # Green
        "max_level": 3
    },
    "Sky Immortal": {
        "damage": 45,
        "range": 200,
        "attack_speed": 1.5,
        "cost": 800,
        "color": (255, 255, 100),  # Yellow
        "max_level": 3
    },
    "Heaven Immortal": {
        "damage": 100,
        "range": 180,
        "attack_speed": 1.8,
        "cost": 1000,
        "color": (255, 215, 0),    # Gold
        "max_level": 3
    }
}

class TowerType(Enum):
    QI_CONDENSATION = 1
    FOUNDATION = 2
    CORE_FORMATION = 3
    NASCENT_SOUL = 4
    SOUL_SEVERING = 5
    EARTH_IMMORTAL = 6
    SKY_IMMORTAL = 7
    HEAVEN_IMMORTAL = 8

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, speed=10):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.active = True
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0
        
        # Load and setup animation
        try:
            self.sprite = pygame.image.load(os.path.join('assets', 'qi shot.png'))
            self.sprite = pygame.transform.scale(self.sprite, (30, 15))  # Adjusted size for better visibility
        except:
            self.sprite = pygame.Surface((15, 7))
            self.sprite.fill((200, 255, 100))  # Light green fallback
            
        # Calculate rotation angle (point towards movement direction)
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.sprite = pygame.transform.rotate(self.sprite, self.angle)
        
    def update(self):
        if self.active:
            self.x += self.dx
            self.y += self.dy
            
            # Check if projectile has reached target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.active = False
                
    def draw(self, screen):
        if self.active:
            # Get the rect for proper centering
            sprite_rect = self.sprite.get_rect()
            sprite_rect.center = (int(self.x), int(self.y))
            screen.blit(self.sprite, sprite_rect)

class Tower:
    def __init__(self, tower_type, x, y):
        self.tower_type = tower_type
        self.x = x
        self.y = y
        self.level = 1
        self.target = None
        self.attack_timer = 0
        self.properties = TOWER_PROPERTIES[tower_type]
        
        # Initialize base stats
        self.damage = self.properties["damage"]
        self.range = self.properties["range"]
        self.attack_speed = self.properties["attack_speed"]
        self.max_level = self.properties["max_level"]
        
        try:
            self.sprite = pygame.image.load(os.path.join('assets', 'wuxia.png'))
            self.sprite = pygame.transform.scale(self.sprite, (50, 50))
        except:
            self.sprite = pygame.Surface((50, 50))
            self.sprite.fill(self.properties["color"])
            
        self.projectiles = []
        
    def draw(self, screen):
        # Draw tower base
        pygame.draw.circle(screen, self.properties["color"], (int(self.x), int(self.y)), 15)
        
        # Draw range circle (semi-transparent)
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.properties["color"], 30), (self.range, self.range), self.range)
        screen.blit(range_surface, (self.x - self.range, self.y - self.range))
        
        # Draw level indicator
        if self.level > 1:
            font = pygame.font.Font(None, 20)
            level_text = font.render(str(self.level), True, (255, 255, 255))
            level_rect = level_text.get_rect(center=(self.x, self.y))
            screen.blit(level_text, level_rect)
        
        # Draw tower
        screen.blit(self.sprite, (self.x, self.y))
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
    def update(self, enemies):
        """Update tower state and attack enemies"""
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        # Update existing projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
            
        # Find closest enemy in range
        closest_enemy = None
        closest_dist = float('inf')
        
        for enemy in enemies:
            dx = enemy.x - (self.x + 25)
            dy = enemy.y - (self.y + 25)
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < self.properties["range"] and dist < closest_dist:
                closest_enemy = enemy
                closest_dist = dist
        
        # Attack if we have a target and cooldown is ready
        if closest_enemy and self.attack_timer <= 0:
            # Deal damage
            damage = self.properties["damage"]
            closest_enemy.health -= damage
            
            # Reset cooldown
            self.attack_timer = 30  # Adjust this value to change attack speed
            
            # Create new projectile
            new_projectile = Projectile(
                self.x + 25,  # Center of tower
                self.y + 25,
                closest_enemy.x,
                closest_enemy.y,
                speed=15
            )
            self.projectiles.append(new_projectile)
            
    def upgrade(self):
        if self.level < self.max_level:  # Max level
            self.level += 1
            self.damage *= 1.5
            self.range *= 1.2
            return True
        return False

    @staticmethod
    def get_cost(tower_type):
        """Get the cost of a tower type"""
        return TOWER_PROPERTIES[tower_type]["cost"]
