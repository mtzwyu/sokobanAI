import pygame

class HUD:
    def __init__(self, asset_loader, screen_width, screen_height=600):
        self.asset_loader = asset_loader
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_expanded = False
        self.is_muted = False

        # Lưu scale cho từng nút
        self.icon_scales = {'menu': 1.0, 'home': 1.0, 'reset': 1.0, 'sound': 1.0}

        self._rebuild_rects()

    def _rebuild_rects(self):
        """Tính lại icon_size và vị trí tất cả nút theo screen_width/height hiện tại."""
        # icon_size = 3.5% chiều cao cửa sổ, giới hạn [20, 60]
        self.icon_size = max(20, min(60, int(self.screen_height * 0.035)))
        self.padding   = max(6,  min(16, int(self.screen_height * 0.012)))
        sz = self.icon_size
        pad = self.padding
        w = self.screen_width

        self.menu_rect  = pygame.Rect(w - (sz       + pad),      pad, sz, sz)
        self.home_rect  = pygame.Rect(w - (sz * 2   + pad * 2),  pad, sz, sz)
        self.reset_rect = pygame.Rect(w - (sz * 3   + pad * 3),  pad, sz, sz)
        self.sound_rect = pygame.Rect(w - (sz * 4   + pad * 4),  pad, sz, sz)

    def draw(self, screen, dt):
        pos = pygame.mouse.get_pos()
        
        def animate_and_draw(img_name, rect, key):
            target_scale = 1.3 if rect.collidepoint(pos) else 1.0
            self.icon_scales[key] += (target_scale - self.icon_scales[key]) * 15.0 * dt
            
            img = self.asset_loader.get_icon(img_name, self.icon_size)
            if img:
                scaled_img = pygame.transform.rotozoom(img, 0, self.icon_scales[key])
                scaled_rect = scaled_img.get_rect(center=rect.center)
                screen.blit(scaled_img, scaled_rect)
        
        # Vẽ nút Menu chính
        animate_and_draw('Menu', self.menu_rect, 'menu')
        
        # Vẽ các nút con nếu đang mở rộng
        if self.is_expanded:
            animate_and_draw('home', self.home_rect, 'home')
            animate_and_draw('reset', self.reset_rect, 'reset')
            sound_img_name = 'mute' if self.is_muted else 'volume'
            animate_and_draw(sound_img_name, self.sound_rect, 'sound')

    def handle_click(self, pos):
        """
        Kiểm tra xem người dùng click vào nút nào.
        Trả về 'HOME', 'RESET' hoặc None.
        Tự động đóng/mở menu khi click vào nút Menu.
        """
        if self.menu_rect.collidepoint(pos):
            self.is_expanded = not self.is_expanded
            return None
            
        if self.is_expanded:
            if self.home_rect.collidepoint(pos):
                self.is_expanded = False
                return 'HOME'
            elif self.reset_rect.collidepoint(pos):
                self.is_expanded = False
                return 'RESET'
            elif self.sound_rect.collidepoint(pos):
                self.is_muted = not self.is_muted
                return 'TOGGLE_SOUND'
                
        # Click ra ngoài thì đóng menu
        self.is_expanded = False
        return None

    def update_screen_width(self, new_width, new_height=None):
        """Cập nhật vị trí & kích thước các nút HUD khi cửa sổ thay đổi kích thước."""
        self.screen_width  = new_width
        if new_height is not None:
            self.screen_height = new_height
        self._rebuild_rects()
