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

class Skeleton(Enemy):
    # Using necromancer sprite sheet with different scale and tint for variation
    base_frames = load_sprite_sheet("Necromancer_creativekind-Sheet.png", 160, 128, 0.8)
    images = []
    for frame in base_frames[16:24]:  # Use different set of frames
        # Add bluish tint to make it look more skeletal
        tinted = frame.copy()
        tinted.fill((100, 100, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
        images.append(tinted)

    def __init__(self):
        super().__init__()
        self.name = "Skeleton"
        self.imgs = self.images[:]
        self.full_health = 30
        self.curr_health = self.full_health
        self.vel = 6
        self.if_killed_money_earned = 30
