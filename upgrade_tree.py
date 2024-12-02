import pygame
import os
from enum import Enum

class Currency(Enum):
    QI_PILLS = "qi pills"
    SPIRIT_STONES = "spirit stones"
    IMMORTAL_ESSENCE = "immortal essence"
    DAO_MARKS = "dao marks"

class UpgradeNode:
    
    def __init__(self, name, max_level, cost_type, base_cost, effect_description, prerequisites=None):
        self.name = name
        self.max_level = max_level
        self.current_level = 0
        self.cost_type = cost_type
        self.base_cost = base_cost
        self.effect_description = effect_description
        self.prerequisites = prerequisites if prerequisites is not None else []
        self.unlocked = len(self.prerequisites) == 0
        
        # Load node sprite
        try:
            self.sprite = pygame.image.load(os.path.join('assets', 'upgrade_node.png'))
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except:
            self.sprite = pygame.Surface((40, 40))
            self.sprite.fill((100, 100, 100))
            
        # Position will be set when adding to tree
        self.x = 0
        self.y = 0
        
    def get_cost(self):
        return self.base_cost * (self.current_level + 1)
        
    def can_upgrade(self, currencies):
        if self.current_level >= self.max_level:
            return False
        return currencies[self.cost_type] >= self.get_cost()
        
    def upgrade(self, currencies):
        cost = self.get_cost()
        if self.can_upgrade(currencies):
            currencies[self.cost_type] -= cost
            self.current_level += 1
            return True
        return False

class UpgradeTree:
    def __init__(self):
        self.nodes = [
            UpgradeNode("Basic Qi", 5, Currency.QI_PILLS, 100, "Increase base qi generation"),
            UpgradeNode("Tower Range", 3, Currency.QI_PILLS, 200, "Increase tower range"),
            UpgradeNode("Tower Damage", 3, Currency.QI_PILLS, 200, "Increase tower damage"),
            UpgradeNode("Spirit Enhancement", 3, Currency.SPIRIT_STONES, 50, "Enhance spirit power"),
            UpgradeNode("Qi Mastery", 5, Currency.QI_PILLS, 500, "Master qi control"),
            UpgradeNode("Tower Speed", 3, Currency.QI_PILLS, 300, "Increase tower attack speed")
        ]
        
        # Set node positions
        positions = [
            (0, 0),   # Basic Qi
            (-1, 1),  # Tower Range
            (0, 1),   # Tower Damage
            (1, 1),   # Spirit Enhancement
            (-1, 2),  # Qi Mastery
            (1, 2),   # Tower Speed
        ]
        
        # Set positions for each node
        base_x = 400
        base_y = 200
        spacing_x = 200
        spacing_y = 150
        
        for node, (rel_x, rel_y) in zip(self.nodes, positions):
            node.x = base_x + (rel_x * spacing_x)
            node.y = base_y + (rel_y * spacing_y)
            
    def draw(self, screen, x_offset=0, width=None):
        if width is None:
            width = screen.get_width()
            
        # Draw connections first
        connections = [
            (0, 1),  # Basic Qi -> Tower Range
            (0, 2),  # Basic Qi -> Tower Damage
            (0, 3),  # Basic Qi -> Spirit Enhancement
            (1, 4),  # Tower Range -> Qi Mastery
            (2, 4),  # Tower Damage -> Qi Mastery
            (3, 5),  # Spirit Enhancement -> Tower Speed
        ]
        
        for start_idx, end_idx in connections:
            start_node = self.nodes[start_idx]
            end_node = self.nodes[end_idx]
            pygame.draw.line(screen, (100, 100, 150), 
                           (start_node.x + x_offset, start_node.y),
                           (end_node.x + x_offset, end_node.y), 2)
        
        # Draw nodes
        font = pygame.font.Font(None, 24)
        for node in self.nodes:
            # Draw node circle
            x = node.x + x_offset
            pygame.draw.circle(screen, (100, 100, 150), (x, node.y), 20)
            
            # Draw node name
            text = font.render(node.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, node.y + 30))
            screen.blit(text, text_rect)
            
            # Draw level
            level_text = font.render(f"Level {node.current_level}/{node.max_level}", True, (200, 200, 200))
            level_rect = level_text.get_rect(center=(x, node.y - 30))
            screen.blit(level_text, level_rect)
            
    def handle_click(self, mouse_pos, x_offset=0):
        # Adjust mouse position for offset
        adjusted_x = mouse_pos[0] - x_offset
        
        # Check if any node was clicked
        for node in self.nodes:
            # Simple circle collision check
            dx = adjusted_x - node.x
            dy = mouse_pos[1] - node.y
            if (dx * dx + dy * dy) <= 400:  # 20 * 20 radius
                print(f"Clicked {node.name}")
                return True
        return False
