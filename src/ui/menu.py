import pygame
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.constants import BACKGROUND_COLOR, WHITE, RED

class MainMenu:
    def __init__(self, screen, asset_loader):
        self.screen = screen
        self.asset_loader = asset_loader
        self.font_title = pygame.font.SysFont('tahoma', 60, bold=True)
        self.font_menu = pygame.font.SysFont('tahoma', 32, bold=True)
        self.modes = ["Random", "Default"]
        self.current_mode_index = 0
        self.options = ["Start Game", f"Mode: < {self.modes[self.current_mode_index]} >", "Boxes: < 3 >", "Quit"]
        self.selected_index = 0
        self.num_boxes = 3
        # Hiệu ứng mượt mà (scale của mỗi nút)
        self.scale_values = [1.0 for _ in self.options]
        self.time_passed = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    # Nhảy qua Boxes nếu đang ở Default
                    if self.selected_index == 2 and self.modes[self.current_mode_index] == "Default":
                        self.selected_index = 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    # Nhảy qua Boxes nếu đang ở Default
                    if self.selected_index == 2 and self.modes[self.current_mode_index] == "Default":
                        self.selected_index = 3
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if self.selected_index == 1:
                        self.current_mode_index = (self.current_mode_index - 1) % len(self.modes)
                        self.options[1] = f"Mode: < {self.modes[self.current_mode_index]} >"
                    elif self.selected_index == 2 and self.modes[self.current_mode_index] != "Default" and self.num_boxes > 1:
                        self.num_boxes -= 1
                        self.options[2] = f"Boxes: < {self.num_boxes} >"
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if self.selected_index == 1:
                        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
                        self.options[1] = f"Mode: < {self.modes[self.current_mode_index]} >"
                    elif self.selected_index == 2 and self.modes[self.current_mode_index] != "Default" and self.num_boxes < 30:
                        self.num_boxes += 1
                        self.options[2] = f"Boxes: < {self.num_boxes} >"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_index == 0:
                        return ("PLAY", self.modes[self.current_mode_index], self.num_boxes)
                    elif self.selected_index == 1:
                        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
                        self.options[1] = f"Mode: < {self.modes[self.current_mode_index]} >"
                    elif self.selected_index == 2 and self.modes[self.current_mode_index] != "Default":
                        # Thay đổi số lượng box khi nhấn enter (chỉ ở Random mode)
                        if self.num_boxes < 30:
                            self.num_boxes += 1
                        else:
                            self.num_boxes = 1
                        self.options[2] = f"Boxes: < {self.num_boxes} >"
                    elif self.selected_index == 3:
                        return "QUIT"
                        
        return None

    def render(self, dt):
        self.time_passed += dt
        
        # Xóa sạch màn hình trước (tránh chồng lên game level)
        self.screen.fill((0, 0, 0))
        
        # Vẽ nền
        bg_image = self.asset_loader.get_image('Anh Home Menu', (SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg_image:
            self.screen.blit(bg_image, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill(BACKGROUND_COLOR)
            
        # Hiệu ứng nảy (pulse) cho tiêu đề
        title_scale = 1.0 + math.sin(self.time_passed * 3) * 0.05
        title = self.font_title.render("SOKOBAN", True, WHITE)
        title_scaled = pygame.transform.rotozoom(title, 0, title_scale)
        title_rect = title_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_scaled, title_rect)
        
        # Vẽ các lựa chọn
        for i, option in enumerate(self.options):
            # Cập nhật chữ trong trường hợp box thay đổi
            if i == 1:
                option = f"Mode: < {self.modes[self.current_mode_index]} >"
            elif i == 2:
                option = f"Boxes: < {self.num_boxes} >"
                
            color = RED if i == self.selected_index else WHITE
            if i == 2 and self.modes[self.current_mode_index] == "Default":
                color = (100, 100, 100) # Làm mờ nếu chọn Default
                
            text = self.font_menu.render(option, True, color)
            
            # Nội suy scale
            target_scale = 1.3 if i == self.selected_index else 1.0
            self.scale_values[i] += (target_scale - self.scale_values[i]) * 15.0 * dt
            
            # Nếu đang được chọn thì thêm hiệu ứng pulse nhẹ
            current_scale = self.scale_values[i]
            if i == self.selected_index:
                current_scale += math.sin(self.time_passed * 10) * 0.03
                
            scaled_text = pygame.transform.rotozoom(text, 0, current_scale)
            
            y_pos = (SCREEN_HEIGHT // 2) + 20 + (i * 65)
            rect = scaled_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(scaled_text, rect)
            
        pygame.display.flip()
