import pygame
import math

class AIMenu:
    """
    Menu AI cho game Sokoban, hiển thị khi nhấn Space.
    Thay thế cho cách render text cơ bản trước đây.
    """
    TOGGLE_HEURISTIC  = "TOGGLE_HEURISTIC"
    RUN_AUTO_DRIVE    = "RUN_AUTO_DRIVE"
    CANCEL_AUTO_DRIVE = "CANCEL_AUTO_DRIVE"
    CLOSE             = "CLOSE"

    OPTIONS = [
        ("Phân tích Heuristic (Simple Hill Climbing)", TOGGLE_HEURISTIC,  (80, 255, 100)),
        ("Chạy 7 Thuật toán & Tự Lái (Auto Drive)",    RUN_AUTO_DRIVE,    (255, 230, 50)),
        ("Hủy Tự Lái & Tắt tia Laser",                 CANCEL_AUTO_DRIVE, (255, 100, 100)),
        ("Đóng Menu",                                  CLOSE,             (180, 180, 180)),
    ]

    def __init__(self):
        self.time      = 0.0
        self.sel_index = 0
        self._scales   = [1.0] * len(self.OPTIONS)

    def reset(self):
        """Khởi tạo lại trạng thái menu mỗi lần mở."""
        self.time      = 0.0
        self.sel_index = 0
        self._scales   = [1.0] * len(self.OPTIONS)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.sel_index = (self.sel_index - 1) % len(self.OPTIONS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel_index = (self.sel_index + 1) % len(self.OPTIONS)
                elif event.key == pygame.K_RETURN:
                    return self.OPTIONS[self.sel_index][1]
                
                elif event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                    return self.CLOSE

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                sw, sh = pygame.display.get_surface().get_size()
                rects  = self._get_option_rects(sw, sh)
                for i, r in enumerate(rects):
                    if r.collidepoint(pos):
                        self.sel_index = i

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                sw, sh = pygame.display.get_surface().get_size()
                rects  = self._get_option_rects(sw, sh)
                for i, r in enumerate(rects):
                    if r.collidepoint(pos):
                        return self.OPTIONS[i][1]

        return None

    def _get_option_rects(self, sw, sh):
        item_h   = max(32, int(sh * 0.06))
        item_gap = max(45, int(sh * 0.08))
        base_y   = sh // 2 - int(sh * 0.02)
        rects = []
        for i in range(len(self.OPTIONS)):
            cy = base_y + i * item_gap
            rect = pygame.Rect(sw // 2 - sw // 3, cy - item_h // 2, sw * 2 // 3, item_h)
            rects.append(rect)
        return rects

    def draw(self, screen, dt):
        self.time += dt
        sw, sh = screen.get_size()

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 5, 20, 200)) # Sắc xanh xám đậm
        screen.blit(overlay, (0, 0))

        box_w = min(sw - 40, max(500, int(sw * 0.45)))
        box_h = min(sh - 60, max(420, int(sh * 0.70)))
        box_x = (sw - box_w) // 2
        box_y = (sh - box_h) // 2

        # Shadow
        shadow = pygame.Surface((box_w + 10, box_h + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        screen.blit(shadow, (box_x - 5 + 8, box_y - 5 + 8))

        # Card nền
        card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        card.fill((25, 30, 45, 240))
        screen.blit(card, (box_x, box_y))

        # Viền màu cyan/neon
        glow = abs(math.sin(self.time * 2))
        border_color = (
            int(20 + 30 * glow),
            int(150 + 80 * glow),
            int(200 + 55 * glow),
        )
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_w, box_h), 4, border_radius=15)

        icon_cx = box_x + box_w // 2
        icon_cy = box_y + int(box_h * 0.12)
        self._draw_ai_icon(screen, icon_cx, icon_cy, int(sh * 0.04), border_color)

        title_size = max(24, min(64, int(sh * 0.06)))
        font_title = pygame.font.SysFont("segoeui", title_size, bold=True)

        pulse = 1.0 + math.sin(self.time * 3) * 0.03
        title_surf = font_title.render("HỆ THỐNG AI CHO SOKOBAN", True, (255, 255, 255))
        title_scaled = pygame.transform.rotozoom(title_surf, 0, pulse)
        title_rect = title_scaled.get_rect(center=(sw // 2, box_y + int(box_h * 0.28)))
        
        # Thêm bóng cho Text tiêu đề giống ngoài menu
        shadow_ti = font_title.render("HỆ THỐNG AI CHO SOKOBAN", True, (0, 0, 0))
        shadow_sc = pygame.transform.rotozoom(shadow_ti, 0, pulse)
        shadow_rect = shadow_sc.get_rect(center=(sw // 2 + 3, box_y + int(box_h * 0.28) + 3))
        screen.blit(shadow_sc, shadow_rect)
        screen.blit(title_scaled, title_rect)

        opt_size  = max(16, min(42, int(sh * 0.035)))
        font_opt  = pygame.font.SysFont("segoeui", opt_size, bold=True)

        item_gap = max(45, int(sh * 0.085))
        base_y   = box_y + int(box_h * 0.48)

        for i, (label, _, base_color) in enumerate(self.OPTIONS):
            is_sel  = (i == self.sel_index)
            target  = 1.15 if is_sel else 1.0
            self._scales[i] += (target - self._scales[i]) * 15.0 * dt
            
            current_scale = self._scales[i]
            if is_sel:
                current_scale += math.sin(self.time * 10) * 0.02
                color = base_color
            else:
                color = (220, 220, 220)

            text_surf   = font_opt.render(label, True, color)
            text_scaled = pygame.transform.rotozoom(text_surf, 0, current_scale)
            cy = base_y + i * item_gap
            rect = text_scaled.get_rect(center=(sw // 2, cy))
            screen.blit(text_scaled, rect)

            # Gạch chân + viền highlight phụ khi đang chọn
            if is_sel:
                hw = int(rect.width * 0.8)
                hx = rect.centerx - hw // 2
                pygame.draw.line(screen, color, (hx, rect.bottom + 2), (hx + hw, rect.bottom + 2), 2)
                
                # Thêm con trỏ con 2 bên
                ptr_surf = font_opt.render("►", True, color)
                ptl_surf = font_opt.render("◄", True, color)
                ptr_sc = pygame.transform.rotozoom(ptr_surf, 0, current_scale * 0.8)
                ptl_sc = pygame.transform.rotozoom(ptl_surf, 0, current_scale * 0.8)
                screen.blit(ptr_sc, ptr_sc.get_rect(midright=(rect.left - 10, cy)))
                screen.blit(ptl_sc, ptl_sc.get_rect(midleft=(rect.right + 10, cy)))

        hint_size = max(14, int(sh * 0.02))
        font_hint = pygame.font.SysFont("segoeui", hint_size)
        hint_surf = font_hint.render("Sử dụng chuột, phím mũi tên (↑↓), hoặc Enter để chọn", True, (150, 150, 160))
        hint_rect = hint_surf.get_rect(center=(sw // 2, box_y + box_h - int(sh * 0.035)))
        screen.blit(hint_surf, hint_rect)

    @staticmethod
    def _draw_ai_icon(surface, cx, cy, sz, color):
        """Vẽ biểu tượng bộ não/mạch điện tử đơn giản."""
        # Vòng tròn trung tâm
        pygame.draw.circle(surface, color, (cx, cy), sz // 2, 2)
        # Điểm giữa
        pygame.draw.circle(surface, color, (cx, cy), sz // 5)
        # Các đường mút (node)
        lines = [
            (-sz, -sz//2), (sz, -sz//2),
            (-sz, sz//2),  (sz, sz//2),
            (0, -sz),      (0, sz)
        ]
        for dx, dy in lines:
            end_x = cx + dx
            end_y = cy + dy
            # Line
            pygame.draw.line(surface, color, (cx, cy), (end_x, end_y), 2)
            # Node tròn
            pygame.draw.circle(surface, color, (end_x, end_y), sz // 6)
