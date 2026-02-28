import pygame

class HUD:
    def __init__(self, asset_loader, screen_width):
        self.asset_loader = asset_loader
        self.icon_size = 25
        self.padding = 10
        self.screen_width = screen_width
        
        self.is_expanded = False
        self.is_muted = False
        
        # Lưu scale cho từng nút
        self.icon_scales = {'menu': 1.0, 'home': 1.0, 'reset': 1.0, 'sound': 1.0}
        
        # Nút Menu gốc ở góc trên bên phải
        self.menu_rect = pygame.Rect(
            screen_width - (self.icon_size + self.padding), 
            self.padding, 
            self.icon_size, 
            self.icon_size
        )
        # Khởi tạo kích thước và vị trí của các nút con (Home, Reset)
        # Vị trí sẽ dịch sang trái dần
        self.home_rect = pygame.Rect(
            screen_width - (self.icon_size * 2 + self.padding * 2), 
            self.padding, 
            self.icon_size, 
            self.icon_size
        )
        self.reset_rect = pygame.Rect(
            screen_width - (self.icon_size * 3 + self.padding * 3), 
            self.padding, 
            self.icon_size, 
            self.icon_size
        )
        self.sound_rect = pygame.Rect(
            screen_width - (self.icon_size * 4 + self.padding * 4), 
            self.padding, 
            self.icon_size, 
            self.icon_size
        )

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
