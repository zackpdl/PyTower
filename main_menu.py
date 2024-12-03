import pygame
import sys
import os
from game_objects import GameState
from game_objects.save_manager import SaveManager
from main import Game
from upgrade_tree import UpgradeTree

class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Set fixed window size
        self.screen_width = 1280
        self.screen_height = 720
        
        # Set up display with fixed resolution
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cultivation Path")
        
        # Load background
        try:
            self.background = pygame.image.load(os.path.join('assets', 'bg.jpg'))
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except:
            self.background = pygame.Surface((self.screen_width, self.screen_height))
            self.background.fill((20, 20, 40))
        
        # Calculate UI scale based on resolution
        self.ui_scale = min(self.screen_width / 1920, self.screen_height / 1080)
        self.font_size = int(36 * self.ui_scale)
        
        # Load saved currency
        save_data = SaveManager.load_game()
        self.qi_pills = save_data["qi_pills"]
        self.spirit_stones = save_data["spirit_stones"]
        
        # Initialize upgrade tree
        self.upgrade_tree = UpgradeTree()
        self.in_upgrade_view = False
        
        # Store button rectangles for click detection
        self.buttons = {}
        
    def draw_currency(self):
        font = pygame.font.Font(None, 36)
        qi_text = font.render(f"Qi Pills: {self.qi_pills}", True, (255, 255, 255))
        spirit_text = font.render(f"Spirit Stones: {self.spirit_stones}", True, (255, 215, 0))
        self.screen.blit(qi_text, (self.screen_width - 250, 20))
        self.screen.blit(spirit_text, (self.screen_width - 250, 60))
        
    def draw_main_menu(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        font = pygame.font.Font(None, self.font_size)
        
        # Draw title
        title = font.render("Cultivation Tower Defense", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width/2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw buttons and store their rects
        self.buttons.clear()
        button_y = 300
        for text in ["Start Game", "Quit", "Upgrade Tree"]:  
            button = pygame.Rect(self.screen_width/2 - 100, button_y, 200, 50)
            pygame.draw.rect(self.screen, (100, 100, 100), button)
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)
            self.buttons[text] = button
            button_y += 100
        
        # Draw currency
        self.draw_currency()
        
        pygame.display.flip()
        
    def draw_stage_select(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        font = pygame.font.Font(None, self.font_size)
        title = font.render("Select Cultivation Stage", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen_width/2, 50))
        self.screen.blit(title, title_rect)
        
        # Stage names and descriptions
        stage_info = {
            1: {"name": "Qi Gathering Grounds", "desc": "Begin your cultivation journey"},
            2: {"name": "Spirit Realm Trials", "desc": "Test your foundation"},
            3: {"name": "Soul Formation Path", "desc": "Form your nascent soul"},
            4: {"name": "Mortal Severance Realm", "desc": "Sever your mortal ties"},
            5: {"name": "Core Ascension Path", "desc": "Forge your golden core"},
            6: {"name": "Void Transcendence", "desc": "Transcend the void"},
            7: {"name": "Immortal Ascension", "desc": "Ascend to immortality"},
            8: {"name": "Heaven Tribulation", "desc": "Face the heavenly trial"}
        }
        
        # Calculate button layout
        buttons_per_row = 2
        button_width = 400
        button_height = 80
        margin = 50
        start_x = (self.screen_width - (buttons_per_row * button_width + (buttons_per_row - 1) * margin)) // 2
        start_y = 150
        
        small_font = pygame.font.Font(None, int(self.font_size * 0.7))
        
        for i in range(8):  # 8 stages
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)
            
            # Draw stage button
            button = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(self.screen, (100, 100, 100), button)
            
            # Draw stage name and description
            stage_num = i + 1
            info = stage_info[stage_num]
            
            # Stage name
            name_text = font.render(f"Stage {stage_num}: {info['name']}", True, (255, 255, 255))
            name_rect = name_text.get_rect(centerx=button.centerx, top=button.top + 10)
            self.screen.blit(name_text, name_rect)
            
            # Stage description
            desc_text = small_font.render(info['desc'], True, (200, 200, 200))
            desc_rect = desc_text.get_rect(centerx=button.centerx, top=name_rect.bottom + 5)
            self.screen.blit(desc_text, desc_rect)
            
            self.buttons[f"Stage {stage_num}"] = button
        
        # Draw back button
        back_button = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (100, 100, 100), back_button)
        back_text = font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)
        self.buttons["Back"] = back_button
        
        # Draw currency
        self.draw_currency()
        
        pygame.display.flip()
        
    def draw_upgrade_view(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        font = pygame.font.Font(None, self.font_size)
        title = font.render("Cultivation Tree", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen_width/2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw back button
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (100, 100, 100), back_btn)
        back_text = font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=back_btn.center)
        self.screen.blit(back_text, back_rect)
        self.buttons["Back"] = back_btn
        
        # Draw currency
        self.draw_currency()
        
        # Draw upgrade tree
        self.upgrade_tree.draw(self.screen, x_offset=0, width=self.screen_width)
        
        pygame.display.flip()

    def run(self):
        current_menu = "main"
        running = True
        
        while running:
            # Draw current menu
            if current_menu == "main":
                self.draw_main_menu()
            elif current_menu == "stages":
                self.draw_stage_select()
            elif current_menu == "upgrades":
                self.draw_upgrade_view()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return GameState.QUIT
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check button clicks
                    for text, button in self.buttons.items():
                        if button.collidepoint(mouse_pos):
                            if current_menu == "main":
                                if text == "Start Game":
                                    current_menu = "stages"
                                elif text == "Upgrade Tree":
                                    current_menu = "upgrades"
                                elif text == "Quit":
                                    return GameState.QUIT
                            elif current_menu == "stages":
                                if text == "Back":
                                    current_menu = "main"
                                elif text.startswith("Stage "):
                                    stage_num = int(text.split()[1])
                                    game = Game(self.screen, stage_num - 1)
                                    result = game.run()
                                    if result == GameState.QUIT:
                                        return GameState.QUIT
                                    current_menu = "main"
                                    # Refresh currency after game
                                    save_data = SaveManager.load_game()
                                    self.qi_pills = save_data["qi_pills"]
                                    self.spirit_stones = save_data["spirit_stones"]
                            elif current_menu == "upgrades":
                                if text == "Back":
                                    current_menu = "main"
                    
                    # Handle upgrade tree clicks when in upgrade view
                    if current_menu == "upgrades":
                        self.upgrade_tree.handle_click(mouse_pos)
            
            pygame.display.flip()
            
        return GameState.QUIT

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
