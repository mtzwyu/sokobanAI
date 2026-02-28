import pygame
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.constants import BACKGROUND_COLOR, UP, DOWN, LEFT, RIGHT, BLACK
from src.utils.loader import AssetLoader
from src.core.level import Level
from src.core.level_generator import LevelGenerator
from src.systems.movement import MovementSystem
from src.systems.undo import UndoSystem
from src.systems.reverse_move import ReverseMove
from src.systems.win_condition import WinCondition
from src.ui.menu import MainMenu
from src.ui.hud import HUD
from src.map.load_map import MapExporter
from src.algorithms.solver_adapter import SolverAdapter

from src.algorithms.simple_hill_climbing import simple_hill_climbing
from src.algorithms.steepest_ascent import steepest_ascent_hill_climbing
from src.algorithms.stochastic_hill_climbing import stochastic_hill_climbing
from src.algorithms.random_restart import random_restart_hill_climbing
from src.algorithms.simulated_annealing import simulated_annealing
from src.algorithms.tabu_search import tabu_search
from src.algorithms.local_beam_search import local_beam_search
from src.algorithms.stochastic_beam_search import stochastic_beam_search
from src.algorithms.gradient_descent import gradient_descent
from src.algorithms.nangcao.asao import a_star_search

import time

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sokoban")
        self.clock = pygame.time.Clock()
        
        self.asset_loader = AssetLoader()
        self.asset_loader.load_sprites()
        
        self.level = Level()
        self.undo_system = UndoSystem()
        self.reverse_move = ReverseMove()
        self.movement_system = None
        self.win_condition = None
        self.won = False
        self.num_boxes = 3
        self.tile_size = 64
        self.state = "MENU"
        self.sound_muted = False
        self.time_passed = 0.0
        
        # Biến phục vụ AI Auto Replay
        self.auto_actions = []
        self.replay_step_index = 0
        self.current_level_path = None
        self.menu = MainMenu(self.screen, self.asset_loader)
        self.hud = HUD(self.asset_loader, SCREEN_WIDTH)
        
        # Phát nhạc nền
        bgm_path = os.path.join(self.asset_loader.base_path, "sounds", "Soundtrack.wav")
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(loops=-1)
            except pygame.error as e:
                print(f"Cannot play BGM: {e}")
  
    def load_level(self, filepath=None, is_reset=False):
        if is_reset:
            filepath = getattr(self, "current_level_path", None)
        else:
            self.current_level_path = filepath
            
        if filepath is None:
            generator = LevelGenerator(num_boxes=self.num_boxes, steps=100)
            lines = generator.generate()
            self.level.load_from_lines(lines)
        else:
            self.level.load_from_file(filepath)
            
        self.undo_system = UndoSystem()
        self.reverse_move = ReverseMove()
        if self.level.player:
            self.movement_system = MovementSystem(self.level.grid, self.level.player, self.level.boxes, self.undo_system)
            self.win_condition = WinCondition(self.level.grid, self.level.boxes)
        self.won = False
        
        if self.level.width > 0 and self.level.height > 0:
            max_w = SCREEN_WIDTH // self.level.width
            max_h = SCREEN_HEIGHT // self.level.height
            self.tile_size = min(max_w, max_h)
        else:
            self.tile_size = 64
            
        self.asset_loader.scale_sprites(self.tile_size)
        MapExporter.export(self.level)

    def run_algorithm(self, key_code):
        print("\n" + "="*80)
        print("ĐANG TÍNH TOÁN AI... Vui lòng chờ...")
        print("="*80)
        self.auto_actions = []
        self.replay_step_index = 0
        
        adapter = SolverAdapter(self.level)
        initial_state = adapter.get_initial_state()
        get_neighbors = adapter.get_neighbors
        get_heuristic = adapter.get_heuristic_func()
        
        status = ""
        path_actions = []
        
        if key_code == pygame.K_1:
            print("[AI INFO] Kích hoạt Simple Hill Climbing")
            _, path_actions, _, _, _, status = simple_hill_climbing(initial_state, get_neighbors, get_heuristic, max_steps=10000)
        elif key_code == pygame.K_2:
            print("[AI INFO] Kích hoạt Steepest-Ascent Hill Climbing")
            _, path_actions, _, _, _, status = steepest_ascent_hill_climbing(initial_state, get_neighbors, get_heuristic, max_steps=10000)
        elif key_code == pygame.K_3:
            print("[AI INFO] Kích hoạt Stochastic Hill Climbing")
            _, path_actions, _, _, _, status = stochastic_hill_climbing(initial_state, get_neighbors, get_heuristic, max_steps=10000)
        elif key_code == pygame.K_4:
            print("[AI INFO] Kích hoạt Random-Restart Hill Climbing (Tối đa 10 mạng)")
            _, path_actions, _, _, _, status = random_restart_hill_climbing(initial_state, get_neighbors, get_heuristic, max_restarts=50, max_steps_per_restart=2000)
        elif key_code == pygame.K_5:
            print("[AI INFO] Kích hoạt Simulated Annealing (Nhiệt 100, Nguội 0.995)")
            _, path_actions, _, _, _, status = simulated_annealing(initial_state, get_neighbors, get_heuristic, initial_temp=100.0, cooling_rate=0.995, max_steps=5000)
        elif key_code == pygame.K_6:
            print("[AI INFO] Kích hoạt Tabu Search (50 lịch sử)")
            _, path_actions, _, _, _, status = tabu_search(initial_state, get_neighbors, get_heuristic, max_steps=5000, tabu_tenure=50)
        elif key_code == pygame.K_7:
            print("[AI INFO] Kích hoạt Local Beam Search (K=10)")
            _, path_actions, _, _, _, status = local_beam_search(initial_state, get_neighbors, get_heuristic, k_beam=10, max_steps=1000)
        elif key_code == pygame.K_8:
            print("[AI INFO] Kích hoạt Stochastic Beam Search (K=10)")
            _, path_actions, _, _, _, status = stochastic_beam_search(initial_state, get_neighbors, get_heuristic, k_beam=10, max_steps=1000)
        elif key_code == pygame.K_9:
            print("[AI INFO] Kích hoạt Gradient Descent")
            _, path_actions, _, _, _, status = gradient_descent(initial_state, get_neighbors, get_heuristic, max_steps=2000)
        elif key_code == pygame.K_0:
            print("[AI INFO] Kích hoạt A* Search (Global)")
            _, path_actions, _, _, status = a_star_search(initial_state, get_neighbors, get_heuristic, max_nodes=100000)
        
        if "THÀNH CÔNG" in status and len(path_actions) > 0:
            print(f"\n✅ [AI REPLAY] Vừa thi triển thành công! Đã lưu lại {len(path_actions)} Bước Đi.")
            print(">>> Màn hình chuyển qua chế độ Replay <<<")
            self.auto_actions = path_actions
            self.state = "REPLAY_STEP"
        else:
            print(f"\n❌ [AI REPLAY] Thuật toán KHÔNG tìm được đích: {status}")
            self.state = "PLAYING"

    def handle_events(self):
        if self.state == "MENU":
            action = self.menu.handle_events()
            if action == "QUIT":
                return False
            elif isinstance(action, tuple) and action[0] == "PLAY":
                mode = action[1]
                self.num_boxes = action[2]
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    
                if mode == "Default":
                    self.load_level("src/map/map_default.txt")
                else:
                    self.load_level()
                    
                self.state = "PLAYING"
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.state == "ALGO_MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        print("\nĐã thoát Menu Thuật Toán.")
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        self.run_algorithm(event.key)
                continue
                
            if self.state == "REPLAY_STEP":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        print("\nĐã hủy quá trình xem Replay.")
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.auto_actions and not self.won:
                            action = self.auto_actions.pop(0)
                            self.replay_step_index += 1
                            
                            dx, dy = 0, 0
                            if "LÊN" in action: dy = -1
                            elif "XUỐNG" in action: dy = 1
                            elif "TRÁI" in action: dx = -1
                            elif "PHẢI" in action: dx = 1
                                
                            moved, pushed = self.movement_system.move(dx, dy)
                            if moved:
                                # Ghi lại bước replay cho Reverse Move
                                pushed_box = None
                                if pushed:
                                    bx = self.level.player.x + dx
                                    by = self.level.player.y + dy
                                    for box in self.level.boxes:
                                        if box.x == bx and box.y == by:
                                            pushed_box = box
                                            break
                                self.reverse_move.record_move(self.level.player, self.level.boxes, dx, dy, pushed_box)
                                MapExporter.export(self.level)
                                if not self.sound_muted:
                                    snd = self.asset_loader.get_sound("push" if pushed else "move")
                                    if snd: snd.play()
                                
                                adapter = SolverAdapter(self.level)
                                current_state = adapter.get_initial_state()
                                get_heuristic = adapter.get_heuristic_func()
                                score, box_w, player_w = get_heuristic(current_state)
                                score_str = f"{score:.1f} ({box_w:.1f}+{player_w:.1f})" if score != float('inf') else "inf"
                                print(f"| GHI HÌNH REPLAY BƯỚC {self.replay_step_index:<3} | Heuristic: {score_str:<15} | Hành động: {action:<22} |")
                                
                                if self.win_condition.check_win():
                                    self.won = True
                                    print("\n✅ AUTO-REPLAY ĐÃ CHẠM ĐÍCH THÀNH CÔNG!")
                                    self.state = "PLAYING"
                                    if not self.sound_muted:
                                        snd = self.asset_loader.get_sound("win")
                                        if snd: snd.play()
                        
                        if not self.auto_actions and not self.won:
                            print("\nPhát Hết Băng Ghi Hình. Trở về Chơi Từ Do.")
                            self.state = "PLAYING"
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == "PLAYING":
                action = self.hud.handle_click(event.pos)
                if action == 'HOME':
                    self.state = "MENU"
                    bgm_path = os.path.join(self.asset_loader.base_path, "sounds", "Soundtrack.wav")
                    if os.path.exists(bgm_path):
                        try:
                            pygame.mixer.music.load(bgm_path)
                            pygame.mixer.music.set_volume(0.0 if self.sound_muted else 0.5)
                            pygame.mixer.music.play(loops=-1)
                        except pygame.error:
                            pass
                elif action == 'RESET':
                    self.load_level(is_reset=True)
                elif action == 'TOGGLE_SOUND':
                    self.sound_muted = self.hud.is_muted
                    pygame.mixer.music.set_volume(0.0 if self.sound_muted else 0.5)
            
            if event.type == pygame.KEYDOWN and not self.won and self.level.player and self.state == "PLAYING":
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dx, dy = UP
                elif event.key == pygame.K_DOWN:
                    dx, dy = DOWN
                elif event.key == pygame.K_LEFT:
                    dx, dy = LEFT
                elif event.key == pygame.K_RIGHT:
                    dx, dy = RIGHT
                elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.undo_system.undo(self.level.player, self.level.boxes)
                    MapExporter.export(self.level)
                elif event.key == pygame.K_r:
                    self.load_level(is_reset=True)
                elif event.key == pygame.K_BACKSPACE:
                    # Túa ngược 1 bước (Reverse Move - kéo hộp ngược lại)
                    if self.reverse_move.reverse(self.level.player, self.level.boxes, self.level.grid):
                        MapExporter.export(self.level)
                        if not self.sound_muted:
                            snd = self.asset_loader.get_sound("move")
                            if snd: snd.play()
                elif event.key == pygame.K_SPACE:
                    self.state = "ALGO_MENU"
                    self.auto_actions = []
                    
                if dx != 0 or dy != 0:
                    moved, pushed = self.movement_system.move(dx, dy)
                    if moved:
                        # Ghi lại bước đi cho Reverse Move
                        pushed_box = None
                        if pushed:
                            # Tìm hộp vừa bị đẩy (nằm tại vị trí mới: player + 2*d)
                            bx = self.level.player.x + dx
                            by = self.level.player.y + dy
                            for box in self.level.boxes:
                                if box.x == bx and box.y == by:
                                    pushed_box = box
                                    break
                        self.reverse_move.record_move(self.level.player, self.level.boxes, dx, dy, pushed_box)
                        MapExporter.export(self.level)
                        if not self.sound_muted:
                            snd = self.asset_loader.get_sound("push" if pushed else "move")
                            if snd: snd.play()
                                
                        if self.win_condition.check_win():
                            self.won = True
                            print("You Win!")
                            if not self.sound_muted:
                                win_sound = self.asset_loader.get_sound("win")
                                if win_sound: win_sound.play()
                                
            elif event.type == pygame.KEYDOWN and self.won:
                if event.key == pygame.K_r:
                    self.load_level(is_reset=True)
                    
        return True

    def calculate_offsets(self):
        level_pixel_width = self.level.width * self.tile_size
        level_pixel_height = self.level.height * self.tile_size
        offset_x = (SCREEN_WIDTH - level_pixel_width) // 2
        offset_y = (SCREEN_HEIGHT - level_pixel_height) // 2
        return offset_x, offset_y

    def render(self, dt):
        if self.state == "MENU":
            self.menu.render(dt)
            return
            
        self.screen.fill(BACKGROUND_COLOR)
        
        if not self.level.player:
            pygame.display.flip()
            return
            
        offset_x, offset_y = self.calculate_offsets()
        
        for y in range(self.level.height):
            for x in range(self.level.width):
                pixel_x = x * self.tile_size + offset_x
                pixel_y = y * self.tile_size + offset_y

                # Vẽ sàn
                if not self.level.grid.is_wall(x, y) and not self.level.grid.is_outside(x, y):
                    floor_sprite = self.asset_loader.get_sprite("floor")
                    self.screen.blit(floor_sprite, (pixel_x, pixel_y))

                sprite_name = None
                if self.level.grid.is_wall(x, y):
                    sprite_name = "wall"
                elif self.level.grid.is_target(x, y):
                    sprite_name = "target"
                    
                if sprite_name:
                    sprite = self.asset_loader.get_sprite(sprite_name)
                    self.screen.blit(sprite, (pixel_x, pixel_y))

        for box in self.level.boxes:
            box.update(dt)
            box.draw(self.screen, self.asset_loader, offset_x, offset_y, self.tile_size)
            
        self.level.player.update(dt)
        self.level.player.draw(self.screen, self.asset_loader, offset_x, offset_y, self.tile_size)
        
        self.time_passed += dt
        
        if self.won:
            font = pygame.font.Font(None, 74)
            text = font.render("You Win! Press 'R' to restart", True, (255, 255, 255))
            
            pulse_scale = 1.0 + math.sin(self.time_passed * 5) * 0.1
            scaled_text = pygame.transform.rotozoom(text, 0, pulse_scale)
            
            text_rect = scaled_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
            self.screen.blit(scaled_text, text_rect)
            
        self.hud.draw(self.screen, dt)
        
        if self.state == "ALGO_MENU":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(240)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Tìm font hỗ trợ tiếng Việt từ Windows Fonts
            viet_font_candidates = [
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\verdana.ttf",
                r"C:\Windows\Fonts\tahoma.ttf",
                r"C:\Windows\Fonts\segoeui.ttf",
            ]
            font_path = next((p for p in viet_font_candidates if os.path.exists(p)), None)
            if font_path:
                font_title = pygame.font.Font(font_path, 40)
                font_item = pygame.font.Font(font_path, 26)
            else:
                font_title = pygame.font.Font(None, 48)
                font_item = pygame.font.Font(None, 36)
            
            title = font_title.render("DANH SÁCH THUẬT TOÁN AI", True, (255, 255, 0))
            self.screen.blit(title, (50, 40))
            
            algos = [
                "1. Simple Hill Climbing",
                "2. Steepest-Ascent Hill Climbing",
                "3. Stochastic Hill Climbing",
                "4. Random-Restart Hill Climbing",
                "5. Simulated Annealing",
                "6. Tabu Search",
                "7. Local Beam Search",
                "8. Stochastic Beam Search",
                "9. Gradient Descent",
                "0. A* Search (Global - Shortest Path)",
                " ",
                "[ESC] Rời khỏi Menu AI"
            ]
            for i, text_m in enumerate(algos):
                color = (255, 255, 255) if "ESC" not in text_m else (150, 255, 150)
                surf = font_item.render(text_m, True, color)
                self.screen.blit(surf, (50, 100 + i * 35))
                
        elif self.state == "REPLAY_STEP":
            viet_font_candidates = [
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\verdana.ttf",
                r"C:\Windows\Fonts\tahoma.ttf",
            ]
            fp = next((p for p in viet_font_candidates if os.path.exists(p)), None)
            font_item = pygame.font.Font(fp, 26) if fp else pygame.font.Font(None, 32)
            text_m = font_item.render(f">>> REPLAY TUNG BUOC: Bam ENTER cho Buoc {self.replay_step_index+1} <<< (ESC: Huy)", True, (255, 255, 0))
            
            # Khung text
            text_rect = text_m.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 30))
            bg_rect = pygame.Rect(text_rect.left - 10, text_rect.top - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            self.screen.blit(text_m, text_rect)

        pygame.display.flip()

    def run(self):
        running = True
        dt = 0.0
        while running:
            running = self.handle_events()
            self.render(dt)
            dt = self.clock.tick(FPS) / 1000.0
            
        pygame.quit()
        sys.exit()
