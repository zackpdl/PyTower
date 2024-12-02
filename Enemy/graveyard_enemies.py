import pygame
from Enemy.enemies import Enemy
import os

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

class Bat(Enemy):
    # Using zombie frames from Character-and-Zombie, scaled down and tinted for bat-like appearance
    base_frames = load_sprite_sheet("Character-and-Zombie.png", 32, 32, 0.8)[-8:]  # Use zombie frames
    images = []
    for frame in base_frames:
        # Add dark purple tint to make it look more bat-like
        tinted = frame.copy()
        tinted.fill((100, 0, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
        images.append(tinted)

    def __init__(self):
        super().__init__()
        self.name = "Bat"
        self.imgs = self.images[:]
        self.full_health = 20
        self.curr_health = self.full_health
        self.vel = 7
        self.if_killed_money_earned = 25
