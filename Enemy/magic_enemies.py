import pygame
import os
from Enemy.enemies import Enemy

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

class MaskedMan(Enemy):
    # Using necromancer sprite sheet with different scale and tint for magical appearance
    base_frames = load_sprite_sheet("Necromancer_creativekind-Sheet.png", 160, 128, 0.9)
    images = []
    for frame in base_frames[24:32]:  # Use different set of frames
        # Add cyan tint to make it look more magical
        tinted = frame.copy()
        tinted.fill((0, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
        images.append(tinted)

    def __init__(self):
        super().__init__()
        self.name = "MaskedMan"
        self.imgs = self.images[:]
        self.full_health = 40
        self.curr_health = self.full_health
        self.vel = 5
        self.if_killed_money_earned = 45
