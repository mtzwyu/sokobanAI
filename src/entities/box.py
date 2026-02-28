import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class Box:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visual_x = float(x)
        self.visual_y = float(y)
        self.is_on_target = False
        self.move_speed = 10.0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def update_target_state(self, is_on_target):
        self.is_on_target = is_on_target

    def update(self, dt):
        self.visual_x += (self.x - self.visual_x) * self.move_speed * dt
        self.visual_y += (self.y - self.visual_y) * self.move_speed * dt

    def draw(self, surface, asset_loader, offset_x=0, offset_y=0, tile_size=64):
        sprite_name = "box_on_target" if self.is_on_target else "box"
        sprite = asset_loader.get_sprite(sprite_name)
        pixel_x = self.visual_x * tile_size + offset_x
        pixel_y = self.visual_y * tile_size + offset_y
        surface.blit(sprite, (pixel_x, pixel_y))
