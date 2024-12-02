import pygame
import os
import math
from enum import Enum

class TowerType(Enum):
    QI_CONDENSATION = 1
    FOUNDATION = 2
    CORE_FORMATION = 3
    NASCENT_SOUL = 4
    SOUL_SEVERING = 5
    EARTH_IMMORTAL = 6
    SKY_IMMORTAL = 7
    HEAVEN_IMMORTAL = 8

# Tower properties with cultivation-themed attributes
TOWER_PROPERTIES = {
    TowerType.QI_CONDENSATION: {
        "damage": 10,
        "range": 150,
        "cost": 100,
        "color": (0, 255, 0),
        "description": "Gathers Qi from surroundings"
    },
    TowerType.FOUNDATION: {
        "damage": 20,
        "range": 180,
        "cost": 200,
        "color": (0, 200, 50),
        "description": "Establishes spiritual foundation"
    },
    TowerType.CORE_FORMATION: {
        "damage": 35,
        "range": 200,
        "cost": 350,
        "color": (0, 150, 100),
        "description": "Forms spiritual core"
    },
    TowerType.NASCENT_SOUL: {
        "damage": 50,
        "range": 220,
        "cost": 500,
        "color": (0, 100, 150),
        "description": "Manifests nascent soul"
    },
    TowerType.SOUL_SEVERING: {
        "damage": 75,
        "range": 250,
        "cost": 750,
        "color": (0, 50, 200),
        "description": "Severs mortal ties"
    },
    TowerType.EARTH_IMMORTAL: {
        "damage": 100,
        "range": 280,
        "cost": 1000,
        "color": (0, 0, 255),
        "description": "Commands earthly laws"
    },
    TowerType.SKY_IMMORTAL: {
        "damage": 150,
        "range": 320,
        "cost": 1500,
        "color": (100, 0, 255),
        "description": "Controls heavenly essence"
    },
    TowerType.HEAVEN_IMMORTAL: {
        "damage": 200,
        "range": 400,
        "cost": 2000,
        "color": (200, 0, 255),
        "description": "Transcends mortal realm"
    }
}

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
        self.type = tower_type
        self.x = x
        self.y = y
        self.properties = TOWER_PROPERTIES[tower_type]
        self.level = 1
        self.target = None
        self.attack_cooldown = 0
        self.projectiles = []
        
        try:
            self.sprite = pygame.image.load(os.path.join('assets', 'wuxia.png'))
            self.sprite = pygame.transform.scale(self.sprite, (50, 50))
        except:
            self.sprite = pygame.Surface((50, 50))
            self.sprite.fill(self.properties["color"])
            
    @staticmethod
    def get_cost(tower_type):
        """Get the cost of a tower type"""
        return TOWER_PROPERTIES[tower_type]["cost"]
        
    def draw(self, screen):
        """Draw the tower and its range circle"""
        # Draw range circle
        pygame.draw.circle(screen, (100, 100, 100, 50), 
                         (int(self.x + 25), int(self.y + 25)), 
                         self.properties["range"], 1)
        
        # Draw tower
        screen.blit(self.sprite, (self.x, self.y))
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
    def update(self, enemies):
        """Update tower state and attack enemies"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
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
        if closest_enemy and self.attack_cooldown <= 0:
            # Deal damage
            damage = self.properties["damage"]
            closest_enemy.health -= damage
            
            # Reset cooldown
            self.attack_cooldown = 30  # Adjust this value to change attack speed
            
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
        if self.level < 3:  # Max level 3
            self.level += 1
            self.properties["damage"] *= 1.5
            self.properties["range"] *= 1.2
            return True
        return False
