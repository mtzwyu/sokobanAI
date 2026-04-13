import pygame
import math

class WinScreen:
    """
    Màn hình hiển thị khi người chơi thắng.
    3 lựa chọn: Chơi Lại (R), Về Menu (M), Thoát (Q).
    Scale responsive theo kích thước cửa sổ.
    """
    PLAY_AGAIN = "PLAY_AGAIN"
    MAIN_MENU  = "MAIN_MENU"
    QUIT       = "QUIT"

    OPTIONS = [
        ("Chơi Lại",  PLAY_AGAIN,  (80,  220, 120)),
        ("Về Menu",   MAIN_MENU,   (80,  180, 255)),
        ("Thoát",     QUIT,        (255, 100, 100)),
    ]

    def __init__(self):
        self.time      = 0.0
        self.sel_index = 0          # Mục đang được hover/chọn bằng bàn phím
        self._scales   = [1.0] * len(self.OPTIONS)

    def reset(self):
        """Gọi mỗi lần win screen được hiển thị lại."""
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
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.OPTIONS[self.sel_index][1]
                # Phím tắt nhanh
                elif event.key == pygame.K_r:
                    return self.PLAY_AGAIN
                elif event.key == pygame.K_m:
                    return self.MAIN_MENU   
                elif event.key == pygame.K_q:
                    return self.QUIT

            elif event.type == pygame.MOUSEMOTION:
                # Highlight mục khi hover chuột
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
        """Trả về list Rect (bounding box) của từng mục option để hit-test."""
        item_h = max(36, int(sh * 0.07))
        base_y = sh // 2 + int(sh * 0.08)
        rects  = []
        for i in range(len(self.OPTIONS)):
            cy = base_y + i * item_h
            # Giả sử mỗi mục rộng 60% sw, cao item_h
            rect = pygame.Rect(sw // 2 - sw // 5, cy - item_h // 2, sw * 2 // 5, item_h)
            rects.append(rect)
        return rects


    def draw(self, screen, dt):
        self.time += dt
        sw, sh = screen.get_size()

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        # Gradient từ đen trong suốt ở đỉnh đến đen/vàng tối ở đáy
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        box_w = min(sw - 80, max(420, int(sw * 0.55)))
        box_h = min(sh - 80, max(320, int(sh * 0.60)))
        box_x = (sw - box_w) // 2
        box_y = (sh - box_h) // 2

        # Shadow
        shadow = pygame.Surface((box_w + 8, box_h + 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 90))
        screen.blit(shadow, (box_x - 4 + 6, box_y - 4 + 6))

        # Card nền với viền gradient vàng
        card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        card.fill((20, 20, 35, 230))
        screen.blit(card, (box_x, box_y))

        # Viền vàng phát sáng (pulse)
        glow = abs(math.sin(self.time * 2.5))
        border_color = (
            int(200 + 55 * glow),
            int(170 + 55 * glow),
            int(30 + 30 * glow),
        )
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_w, box_h), 3, border_radius=12)

        star_y  = box_y + int(box_h * 0.10)
        star_cx = sw // 2
        self._draw_star(screen, star_cx, star_y, int(sh * 0.045), border_color)

        title_size = max(30, min(72, int(sh * 0.080)))
        font_title = pygame.font.SysFont("tahoma", title_size, bold=True)

        pulse = 1.0 + math.sin(self.time * 3.5) * 0.04
        title_surf = font_title.render("CHIẾN THẮNG!", True, (255, 230, 60))
        title_scaled = pygame.transform.rotozoom(title_surf, 0, pulse)
        title_rect = title_scaled.get_rect(center=(sw // 2, box_y + int(box_h * 0.30)))
        screen.blit(title_scaled, title_rect)

        # Sub-title nhỏ
        sub_size = max(14, min(28, int(sh * 0.032)))
        font_sub  = pygame.font.SysFont("tahoma", sub_size)
        sub_surf  = font_sub.render("Tất cả hộp đã vào đúng vị trí!", True, (200, 200, 200))
        sub_rect  = sub_surf.get_rect(center=(sw // 2, box_y + int(box_h * 0.46)))
        screen.blit(sub_surf, sub_rect)

        opt_size = max(16, min(36, int(sh * 0.042)))
        font_opt  = pygame.font.SysFont("tahoma", opt_size, bold=True)

        item_gap = max(42, int(sh * 0.075))
        base_y   = box_y + int(box_h * 0.62)

        for i, (label, _, base_color) in enumerate(self.OPTIONS):
            is_sel  = (i == self.sel_index)
            target  = 1.15 if is_sel else 1.0
            self._scales[i] += (target - self._scales[i]) * 14.0 * dt
            if is_sel:
                self._scales[i] += math.sin(self.time * 9) * 0.018

            # Màu sáng hơn khi được chọn
            color = (
                min(255, int(base_color[0] * (1.4 if is_sel else 1.0))),
                min(255, int(base_color[1] * (1.4 if is_sel else 1.0))),
                min(255, int(base_color[2] * (1.4 if is_sel else 1.0))),
            )

            text_surf   = font_opt.render(label, True, color)
            text_scaled = pygame.transform.rotozoom(text_surf, 0, self._scales[i])
            cy = base_y + i * item_gap
            rect = text_scaled.get_rect(center=(sw // 2, cy))
            screen.blit(text_scaled, rect)

            # Gạch chân dưới mục đang chọn
            if is_sel:
                ul_w = int(rect.width * 0.7)
                ul_x = rect.centerx - ul_w // 2
                pygame.draw.line(screen, color, (ul_x, rect.bottom + 2), (ul_x + ul_w, rect.bottom + 2), 2)

        hint_size = max(11, min(20, int(sh * 0.022)))
        font_hint = pygame.font.SysFont("tahoma", hint_size)
        hint_surf = font_hint.render("↑↓ để di chuyển   •   Enter để chọn", True, (120, 120, 120))
        hint_rect = hint_surf.get_rect(center=(sw // 2, box_y + box_h - int(sh * 0.025)))
        screen.blit(hint_surf, hint_rect)


    @staticmethod
    def _draw_star(surface, cx, cy, r, color):
        import math
        points = []
        for k in range(10):
            angle = math.radians(-90 + k * 36)
            radius = r if k % 2 == 0 else r * 0.42
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)
