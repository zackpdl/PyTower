import pygame
from Enemy.enemies import Enemy
import os

pygame.init()
pygame.display.set_mode((1350, 700))

# Get the absolute path to the assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

def load_sprite_sheet(filename, width, height, scale=1):
    image = pygame.image.load(os.path.join(ASSETS_DIR, filename)).convert_alpha()
    sheet_width = image.get_width()
    sheet_height = image.get_height()
    rows = sheet_height // height
    cols = sheet_width // width
    frames = []
    
    for row in range(rows):
        for col in range(cols):
            x = col * width
            y = row * height
            frame = image.subsurface((x, y, width, height))
            if scale != 1:
                frame = pygame.transform.scale(frame, 
                    (int(width * scale), int(height * scale)))
            frames.append(frame)
    return frames

class Golem(Enemy):
    # Using Necromancer sprite sheet
    images = load_sprite_sheet("Necromancer_creativekind-Sheet.png", 160, 128, 1.2)[:8]  # Use first 8 frames

    def __init__(self):
        super().__init__()
        self.name = "Golem"
        self.imgs = self.images[:]
        self.full_health = 100
        self.curr_health = self.full_health
        self.vel = 3
        self.if_killed_money_earned = 120

class Guard(Enemy):
    # Using zombie from Character-and-Zombie
    images = load_sprite_sheet("Character-and-Zombie.png", 32, 32, 4)[-8:]  # Use last 8 frames (zombie frames)

    def __init__(self):
        super().__init__()
        self.name = "Guard"
        self.imgs = self.images[:]
        self.full_health = 80
        self.curr_health = self.full_health
        self.vel = 4
        self.if_killed_money_earned = 90

class Tree(Enemy):
    # Using tower sprite as a stationary enemy
    images = []
    base_img = pygame.image.load(os.path.join(ASSETS_DIR, "RedMoonTower_free_idle_animation..png")).convert_alpha()
    # Create simple animation by scaling slightly
    for scale in range(95, 105, 5):
        scaled_img = pygame.transform.scale(base_img, 
            (int(base_img.get_width() * scale/100), 
             int(base_img.get_height() * scale/100)))
        images.append(scaled_img)

    def __init__(self):
        super().__init__()
        self.name = "Tree"
        self.imgs = self.images[:]
        self.full_health = 70
        self.curr_health = self.full_health
        self.vel = 2
        self.if_killed_money_earned = 100

class Yeti(Enemy):
    # Using flipped necromancer frames for variation
    images = [pygame.transform.flip(img, True, False) 
              for img in load_sprite_sheet("Necromancer_creativekind-Sheet.png", 160, 128, 1.2)[8:16]]

    def __init__(self):
        super().__init__()
        self.name = "Yeti"
        self.imgs = self.images[:]
        self.full_health = 90
        self.curr_health = self.full_health
        self.vel = 4
        self.if_killed_money_earned = 90

class SuperBoss(Enemy):
    # Using larger scaled necromancer with color tint for final boss
    base_frames = load_sprite_sheet("Necromancer_creativekind-Sheet.png", 160, 128, 1.5)
    images = []
    for frame in base_frames[:8]:
        # Add reddish tint to make it look more menacing
        tinted = frame.copy()
        tinted.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)
        images.append(tinted)

    def __init__(self):
        super().__init__()
        self.name = "superboss"
        self.imgs = self.images[:]
        self.full_health = 500
        self.curr_health = self.full_health
        self.vel = 3
        self.if_killed_money_earned = 1000
