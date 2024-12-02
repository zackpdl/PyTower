import pygame
import os
from enum import Enum
from .enemy import Enemy, EnemyType

class BossType(Enum):
    ELDER = 1
    SECT_LEADER = 2
    DEMON_LORD = 3
    ANCIENT_IMMORTAL = 4
    HEAVENLY_EMPEROR = 5

class Boss(Enemy):
    def __init__(self, x, y, boss_type, stage_level):
        super().__init__(x, y, EnemyType.IMMORTAL, stage_level)
        self.boss_type = boss_type
        self.special_ability_cooldown = 0
        self.ability_active = False
        
        # Override stats with boss multipliers
        self.apply_boss_multipliers()
        
        # Load boss-specific sprite (you can add different sprites for different bosses)
        self.sprite = pygame.image.load(os.path.join('assets', 'Character-and-Zombie.png'))
        self.sprite = pygame.transform.scale(self.sprite, (75, 75))  # Bigger than regular enemies
        
    def apply_boss_multipliers(self):
        # Boss-specific multipliers
        boss_multipliers = {
            BossType.ELDER: {
                "health": 5,
                "damage": 3,
                "speed": 0.8,
                "reward": 5,
                "ability": self.healing_ability
            },
            BossType.SECT_LEADER: {
                "health": 7,
                "damage": 4,
                "speed": 1,
                "reward": 7,
                "ability": self.speed_burst_ability
            },
            BossType.DEMON_LORD: {
                "health": 10,
                "damage": 5,
                "speed": 1.2,
                "reward": 10,
                "ability": self.damage_reflection_ability
            },
            BossType.ANCIENT_IMMORTAL: {
                "health": 15,
                "damage": 7,
                "speed": 1.5,
                "reward": 15,
                "ability": self.summon_minions_ability
            },
            BossType.HEAVENLY_EMPEROR: {
                "health": 20,
                "damage": 10,
                "speed": 2,
                "reward": 20,
                "ability": self.ultimate_ability
            }
        }
        
        multiplier = boss_multipliers[self.boss_type]
        self.max_health *= multiplier["health"]
        self.health = self.max_health
        self.damage *= multiplier["damage"]
        self.speed *= multiplier["speed"]
        self.reward *= multiplier["reward"]
        self.special_ability = multiplier["ability"]
        
    def update(self):
        super().update()
        
        # Update special ability
        if self.special_ability_cooldown > 0:
            self.special_ability_cooldown -= 1
        elif not self.ability_active and self.health < self.max_health * 0.5:
            # Activate ability when below 50% health
            self.special_ability()
            self.special_ability_cooldown = 300  # 5 seconds at 60 FPS
            
    def draw(self, screen):
        super().draw(screen)
        # Add visual effects for active abilities
        if self.ability_active:
            pygame.draw.circle(screen, (255, 215, 0), 
                             (int(self.x + 37), int(self.y + 37)), 
                             40, 2)
    
    # Special abilities
    def healing_ability(self):
        self.health = min(self.max_health, self.health * 1.5)
        self.ability_active = True
        
    def speed_burst_ability(self):
        self.speed *= 2
        self.ability_active = True
        
    def damage_reflection_ability(self):
        # Implementation would need game logic to reflect damage back to towers
        self.ability_active = True
        
    def summon_minions_ability(self):
        # Implementation would need game logic to spawn additional enemies
        self.ability_active = True
        
    def ultimate_ability(self):
        # Combine multiple effects
        self.healing_ability()
        self.speed_burst_ability()
        self.damage_reflection_ability()
