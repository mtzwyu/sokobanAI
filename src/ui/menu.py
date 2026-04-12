import pygame
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.constants import BACKGROUND_COLOR

class MainMenu:
    def __init__(self, screen, asset_loader):
        self.screen = screen
        self.asset_loader = asset_loader
        self.modes = ["Ngẫu Nhiên", "Mặc Định"]
        self.current_mode_index = 0
        self.num_boxes = 3
        
        self.selected_index = 0
        self.time_passed = 0.0

        # Chỉ số của các thành phần
        # 0: Bắt Đầu
        # 1: Chế Độ
        # 2: Số Hộp
        # 3: Thoát
        self.options_count = 4
        self.scale_values = [1.0] * self.options_count

    def _get_fonts(self, sw, sh):
        """Tạo font scale theo kích thước cửa sổ."""
        title_size = max(40, min(110, int(sh * 0.12)))
        menu_size  = max(16, min(42, int(sh * 0.045)))
        return (
            pygame.font.SysFont('tahoma', title_size, bold=True),
            pygame.font.SysFont('tahoma', menu_size,  bold=True),
        )

    def _get_current_options(self):
        return [
            "Bắt Đầu",
            f"Chế độ: < {self.modes[self.current_mode_index]} >",
            f"Số hộp: < {self.num_boxes} >",
            "Thoát"
        ]

    def handle_events(self, events):
        for event in events:
            sw, sh = self.screen.get_size()
            rects = self._get_option_rects(sw, sh)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (self.selected_index - 1) % self.options_count
                    if self.selected_index == 2 and self.current_mode_index == 1: # Default mode skips boxes
                        self.selected_index = 1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (self.selected_index + 1) % self.options_count
                    if self.selected_index == 2 and self.current_mode_index == 1:
                        self.selected_index = 3
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.selected_index == 1:
                        self.current_mode_index = (self.current_mode_index - 1) % len(self.modes)
                    elif self.selected_index == 2 and self.current_mode_index == 0 and self.num_boxes > 1:
                        self.num_boxes -= 1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.selected_index == 1:
                        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
                    elif self.selected_index == 2 and self.current_mode_index == 0 and self.num_boxes < 30:
                        self.num_boxes += 1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self._handle_activation()

            elif event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        # Bỏ qua dòng số hộp nếu đang ở chế độ Mặc Định
                        if i == 2 and self.current_mode_index == 1:
                            continue
                        self.selected_index = i

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Nếu click đúng vị trí đang chọn thì kích hoạt luôn để logic xử lý (hoặc đổi option với left/right)
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        self.selected_index = i
                        
                        # Xử lý mũi tên trái/phải trên dòng chế độ / số hộp bằng cách tính tọa độ click
                        if self.selected_index == 1:
                            if event.pos[0] < sw // 2:
                                self.current_mode_index = (self.current_mode_index - 1) % len(self.modes)
                            else:
                                self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
                        elif self.selected_index == 2 and self.current_mode_index == 0:
                            if event.pos[0] < sw // 2 and self.num_boxes > 1:
                                self.num_boxes -= 1
                            elif event.pos[0] >= sw // 2 and self.num_boxes < 30:
                                self.num_boxes += 1
                        else:
                            return self._handle_activation()

        return None

    def _handle_activation(self):
        if self.selected_index == 0:
            mode_en = "Default" if self.current_mode_index == 1 else "Random"
            return ("PLAY", mode_en, self.num_boxes)
        elif self.selected_index == 1:
            self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
        elif self.selected_index == 2 and self.current_mode_index == 0:
            if self.num_boxes < 30:
                self.num_boxes += 1
            else:
                self.num_boxes = 1
        elif self.selected_index == 3:
            return "QUIT"
        return None

    def _get_option_rects(self, sw, sh):
        """Bounding box ảo để bắt chuột"""
        item_spacing = max(45, int(sh * 0.085))
        base_y = (sh // 2) + int(sh * 0.05)
        rects = []
        for i in range(self.options_count):
            cy = base_y + i * item_spacing
            rects.append(pygame.Rect(sw // 2 - sw // 3, cy - item_spacing // 2, sw * 2 // 3, item_spacing))
        return rects

    def render(self, dt):
        self.time_passed += dt
        sw, sh = self.screen.get_size()


        self.screen.fill((0, 0, 0))
        bg_image = self.asset_loader.get_image('Anh Home Menu', (sw, sh))
        if bg_image:
            self.screen.blit(bg_image, (0, 0))
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 10, 25, 170)) # Ám xanh tối cho bầu không khí premium
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill(BACKGROUND_COLOR)

        font_title, font_menu = self._get_fonts(sw, sh)


        box_w = min(sw - 40, max(450, int(sw * 0.55)))
        box_h = min(sh - 40, max(500, int(sh * 0.75)))
        box_x = (sw - box_w) // 2
        box_y = (sh - box_h) // 2

        # Shadow
        shadow = pygame.Surface((box_w + 10, box_h + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 120))
        self.screen.blit(shadow, (box_x + 5, box_y + 5))

        # Card
        card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        card.fill((30, 35, 45, 230))
        self.screen.blit(card, (box_x, box_y))

        # Viền card nhấp nháy phát sáng
        glow = abs(math.sin(self.time_passed * 2))
        border_color = (
            int(100 + 50 * glow),
            int(150 + 105 * glow),
            int(200 + 55 * glow),
        )
        pygame.draw.rect(self.screen, border_color, (box_x, box_y, box_w, box_h), 3, border_radius=12)


        title_scale = 1.0 + math.sin(self.time_passed * 4) * 0.04
        title = font_title.render("SOKOBAN", True, (255, 255, 255))
        title_scaled = pygame.transform.rotozoom(title, 0, title_scale)
        title_rect = title_scaled.get_rect(center=(sw // 2, box_y + int(box_h * 0.20)))
        
        # Thêm bóng cho Text tiêu đề
        shadow_ti = font_title.render("SOKOBAN", True, (0, 0, 0))
        shadow_sc = pygame.transform.rotozoom(shadow_ti, 0, title_scale)
        shadow_rect = shadow_sc.get_rect(center=(sw // 2 + 4, box_y + int(box_h * 0.20) + 4))
        self.screen.blit(shadow_sc, shadow_rect)
        self.screen.blit(title_scaled, title_rect)


        opts = self._get_current_options()
        item_spacing = max(45, int(sh * 0.085))
        base_y = box_y + int(box_h * 0.45)

        for i, option_text in enumerate(opts):
            is_sel = (i == self.selected_index)
            target_scale = 1.15 if is_sel else 1.0
            
            # Làm mờ nếu dòng box trong chế độ mặc định
            is_disabled = (i == 2 and self.current_mode_index == 1)
            if is_disabled:
                target_scale = 1.0
                if is_sel: self.selected_index = 3 # Tránh để selected dính ở đây
                
            self.scale_values[i] += (target_scale - self.scale_values[i]) * 15.0 * dt
            current_scale = self.scale_values[i]

            if is_sel and not is_disabled:
                current_scale += math.sin(self.time_passed * 10) * 0.02
                color = (255, 200, 50)  # Vàng nổi bật
            elif is_disabled:
                color = (100, 100, 100) # Xám mờ
            else:
                color = (220, 220, 220) # Trắng xám

            # Nút "Bắt Đầu" và "Thoát" thêm viền giả gradient nếu là hover
            if is_sel and i in [0, 3]:
                color = (50, 255, 100) if i == 0 else (255, 100, 100)

            text_surf = font_menu.render(option_text, True, color)
            scaled_text = pygame.transform.rotozoom(text_surf, 0, current_scale)
            
            cy = base_y + (i * item_spacing)
            rect = scaled_text.get_rect(center=(sw // 2, cy))
            self.screen.blit(scaled_text, rect)
            
            if is_sel and not is_disabled:
                # Gạch chân highlight
                hw = int(rect.width * 0.8)
                hx = rect.centerx - hw // 2
                pygame.draw.line(self.screen, color, (hx, rect.bottom + 2), (hx + hw, rect.bottom + 2), 2)
                # Dấu tam giác 2 bên
                ptr = font_menu.render("►", True, color)
                ptl = font_menu.render("◄", True, color)
                ptr_sc = pygame.transform.rotozoom(ptr, 0, current_scale * 0.8)
                ptl_sc = pygame.transform.rotozoom(ptl, 0, current_scale * 0.8)
                self.screen.blit(ptr_sc, ptr_sc.get_rect(midright=(rect.left - 10, cy)))
                self.screen.blit(ptl_sc, ptl_sc.get_rect(midleft=(rect.right + 10, cy)))

        pygame.display.flip()
