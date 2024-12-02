import pygame
import math

class CurrencyDrop:
    def __init__(self, x, y, currency_type, amount):
        self.x = x
        self.y = y
        self.currency_type = currency_type
        self.amount = amount
        
        # Animation properties
        self.float_height = 20
        self.float_speed = 2
        self.time_alive = 0
        self.lifetime = 3  # Seconds before disappearing
        self.collected = False
        
        # Load currency images based on type
        try:
            if currency_type.name == "QI_PILLS":
                self.image = pygame.image.load("assets/qi_pill.png")
            elif currency_type.name == "SPIRIT_STONES":
                self.image = pygame.image.load("assets/spirit_stone.png")
            elif currency_type.name == "IMMORTAL_ESSENCE":
                self.image = pygame.image.load("assets/immortal_essence.png")
            else:
                # Fallback colored circle if image not found
                self.image = None
        except:
            self.image = None
            
    def update(self, dt):
        if self.collected:
            return True
            
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            return True
            
        # Float up and down animation
        self.y += math.sin(self.time_alive * self.float_speed) * 0.5
        
        return False
        
    def draw(self, screen):
        if self.collected:
            return
            
        if self.image:
            screen.blit(self.image, (self.x - 15, self.y - 15))
        else:
            # Fallback colored circles for different currency types
            if self.currency_type.name == "QI_PILLS":
                color = (0, 255, 0)  # Green for qi pills
            elif self.currency_type.name == "SPIRIT_STONES":
                color = (0, 191, 255)  # Deep sky blue for spirit stones
            elif self.currency_type.name == "IMMORTAL_ESSENCE":
                color = (255, 215, 0)  # Gold for immortal essence
            else:
                color = (255, 255, 255)  # White for unknown
                
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 8)
            
        # Draw amount text
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(self.amount), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - 20))
        screen.blit(text, text_rect)
        
    def collect(self):
        self.collected = True
