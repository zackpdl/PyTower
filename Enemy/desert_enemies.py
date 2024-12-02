from Enemy.enemies import Enemy
import pygame
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

class HammerGoblin(Enemy):
    # Using Character sprite from Character-and-Zombie
    images = load_sprite_sheet("Character-and-Zombie.png", 32, 32, 3)[:8]  # Use first 8 frames (character frames)

    def __init__(self):
        super().__init__()
        self.name = "HammerGoblin"
        self.imgs = self.images[:]
        self.full_health = 50
        self.curr_health = self.full_health
        self.vel = 5
        self.if_killed_money_earned = 50
