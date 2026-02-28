import os
import pygame
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import TILE_SIZE

class AssetLoader:
    def __init__(self, base_path="assets"):
        self.base_path = base_path
        self.original_sprites = {}
        self.scaled_sprites = {}
        self.sounds = {}
        self.current_tile_size = 64
        
        # Thiết lập pygame mixer nếu chưa khởi tạo
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def load_sprites(self):
        sprites_path = os.path.join(self.base_path, "sprites")
        if not os.path.exists(sprites_path):
            os.makedirs(sprites_path, exist_ok=True)
            print(f"Created directory: {sprites_path}. Please add .png here.")
            return
        
        for root, dirs, files in os.walk(sprites_path):
            for filename in files:
                if filename.endswith(".png"):
                    name = filename[:-4]
                    path = os.path.join(root, filename)
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.original_sprites[name] = img
                    except pygame.error as e:
                        print(f"Cannot load image {path}: {e}")
                        
                        
        self.scale_sprites(self.current_tile_size)
        self.load_sounds()

    def load_sounds(self):
        sounds_path = os.path.join(self.base_path, "sounds")
        if not os.path.exists(sounds_path):
            os.makedirs(sounds_path, exist_ok=True)
            print(f"Created directory: {sounds_path}. Please add .wav/.mp3 here.")
            return

        for root, dirs, files in os.walk(sounds_path):
            for filename in files:
                if filename.endswith((".wav", ".mp3", ".ogg")):
                    name = filename.rsplit(".", 1)[0]
                    if name.lower() == "soundtrack":
                        continue # BGM được stream trực tiếp qua mixer.music
                    path = os.path.join(root, filename)
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                    except pygame.error as e:
                        print(f"Cannot load sound {path}: {e}")

    def get_sound(self, name):
        return self.sounds.get(name)

    def scale_sprites(self, tile_size):
        if not self.original_sprites:
            self.current_tile_size = tile_size
            return
            
        if self.current_tile_size == tile_size and self.scaled_sprites:
            return
            
        self.current_tile_size = tile_size
        self.scaled_sprites = {}
        for name, img in self.original_sprites.items():
            self.scaled_sprites[name] = pygame.transform.scale(img, (tile_size, tile_size))

    def get_sprite(self, name):
        if name not in self.scaled_sprites:
            # Dùng ảnh chữ nhật màu đơn giản nếu sprite chưa tồn tại
            surf = pygame.Surface((self.current_tile_size, self.current_tile_size))
            if name == 'wall':
                surf.fill((100, 100, 100))
            elif name == 'target':
                surf.fill((200, 200, 0))
            elif name == 'box':
                surf.fill((150, 100, 50))
            elif name == 'box_on_target':
                surf.fill((0, 255, 0))
            elif name == 'player':
                surf.fill((255, 0, 0))
            else:
                surf.fill((255, 0, 255))
            return surf
        return self.scaled_sprites[name]

    def get_icon(self, name, size):
        if name in self.original_sprites:
            img = pygame.transform.scale(self.original_sprites[name], (size, size))
            return img.convert_alpha()
        
        # Trả về ô vuông tạm nếu không có hình
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((200, 200, 200, 128))
        return surf

    def get_image(self, name, size=None):
        if name in self.original_sprites:
            img = self.original_sprites[name]
            if size:
                img = pygame.transform.scale(img, size)
            return img.convert_alpha()
        return None
