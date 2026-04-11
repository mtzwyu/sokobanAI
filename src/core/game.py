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
import time
import tracemalloc
import threading
import tkinter as tk

class DebugHUDWindow(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.info_data = []
        self.current_h = None      # H của vị trí hiện tại (gửi từ game.py)
        self.root = None
        self.title_label = None
        self.current_h_label = None
        self.dir_labels = []
        self.is_ready = False

    def run(self):
        self.root = tk.Tk()
        self.root.title("Phân tích Heuristic - Simple Hill Climbing")
        self.root.geometry("440x590")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1E1E1E")

        self.title_label = tk.Label(self.root,
            text="PHÂN TÍCH HÀM HEURISTIC",
            fg="#00FFFF", bg="#1E1E1E", font=("Segoe UI", 15, "bold"))
        self.title_label.pack(pady=(12, 0))

        # Dòng phụ 1: thuật toán tham chiếu
        self.algo_label = tk.Label(self.root,
            text="Theo thuật toán: Simple Hill Climbing",
            fg="#00CFFF", bg="#1E1E1E", font=("Segoe UI", 11, "italic"))
        self.algo_label.pack(pady=(2, 0))

        # Dòng phụ 2: mô tả logic chọn hướng
        self.sub_label = tk.Label(self.root,
            text="◀ TỐI ƯU = hàng xóm ĐẦU TIÊN có H < H hiện tại",
            fg="#888888", bg="#1E1E1E", font=("Segoe UI", 10))
        self.sub_label.pack(pady=(2, 4))

        # H hiện tại
        self.current_h_label = tk.Label(self.root,
            text="H hiện tại: ...",
            fg="#FFD700", bg="#1E1E1E", font=("Segoe UI", 13, "bold"))
        self.current_h_label.pack(pady=(0, 8))

        # Tạo sắn 4 group cho 4 hướng
        for _ in range(4):
            frame = tk.Frame(self.root, bg="#1E1E1E")
            frame.pack(fill=tk.X, padx=15, pady=5)
            
            lbl_main = tk.Label(frame, text="", fg="white", bg="#1E1E1E", font=("Segoe UI", 14, "bold"), anchor="w")
            lbl_main.pack(fill=tk.X)
            
            lbl_detail = tk.Label(frame, text="", justify=tk.LEFT, fg="gray", bg="#1E1E1E", font=("Segoe UI", 12), anchor="w")
            lbl_detail.pack(fill=tk.X, padx=15)
            
            self.dir_labels.append((lbl_main, lbl_detail))
            
        self.is_ready = True
        self.update_loop()
        self.root.mainloop()

    def update_loop(self):
        if getattr(self, 'title_label', None):
            # Cập nhật dòng H hiện tại
            cur_h = getattr(self, 'current_h', None)
            if self.current_h_label is not None:
                if cur_h is not None:
                    self.current_h_label.config(text=f"H hiện tại: {cur_h}")
                else:
                    self.current_h_label.config(text="H hiện tại: ...")

            data = getattr(self, 'info_data', [])
            for i in range(4):
                lbl_main, lbl_detail = self.dir_labels[i]
                if i < len(data):
                    item = data[i]
                    is_min = item["is_min"]
                    
                    color_main = "#00FF00" if is_min else "#FFFFFF"
                    marker = " ◀ TỐI ƯU" if is_min else ""
                    lbl_main.config(text=f" - [{item['action']}]: H = {item['score']}{marker}", fg=color_main)
                    
                    detail_text = (
                        f"      - Di chuyển (T): {item['h1']}\n"
                        f"      - Tiếp cận (A) : {item['h2']}\n"
                        f"      - Phạt (P)     : {item['h3']}"
                    )
                    
                    detail_color = "#55FF55" if is_min else "#AAAAAA"
                    if item["h3"] > 0:
                        detail_color = "#FF5555"
                        
                    lbl_detail.config(text=detail_text, fg=detail_color)
                else:
                    lbl_main.config(text="")
                    lbl_detail.config(text="")
                    
            self.root.after(50, self.update_loop)

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
        self.ai_menu_active = False
        self.ai_debug_mode = False
        self.debug_window = None
        self.current_level_path = None
        self.auto_play_queue = []
        self.last_auto_move_time = 0.0
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
                    self.load_level("src/map/map_default.xlsx")
                else:
                    self.load_level()
                    
                self.state = "PLAYING"
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.ai_menu_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.ai_debug_mode = not self.ai_debug_mode
                        if self.ai_debug_mode:
                            if self.debug_window is None or not self.debug_window.is_alive():
                                self.debug_window = DebugHUDWindow()
                                self.debug_window.start()
                        self.ai_menu_active = False
                    elif event.key == pygame.K_2:
                        self.ai_menu_active = False
                        self.ai_debug_mode = False
                        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                        from evaluate_algorithms import run_evaluation
                        print("\n[AI] Bắt đầu quá trình đánh giá và xuất Excel theo Map hiện tại...")
                        
                        # AI Run và lấy về kết quả xịn nhất
                        best_path = run_evaluation(self.level)
                        if best_path:
                            self.auto_play_queue = best_path
                            self.last_auto_move_time = self.time_passed
                        else:
                            print("[AI] Thuật toán không tìm thấy nước đi nào!")
                    elif event.key == pygame.K_3:
                        self.ai_menu_active = False
                        self.ai_debug_mode = False
                        if getattr(self, 'auto_play_queue', []):
                            print("\n[AI] HỦY BỎ: Đã dừng lệnh Tự Lái của AI.")
                            self.auto_play_queue = []
                    elif event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                        self.ai_menu_active = False
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
                elif event.key == pygame.K_SPACE:
                    self.ai_menu_active = True
                elif event.key == pygame.K_3:
                    if getattr(self, 'auto_play_queue', []):
                        print("\n[AI] HỦY BỎ: Đã dừng lệnh Tự Lái của AI & Tắt Radar.")
                        self.auto_play_queue = []
                    self.ai_debug_mode = False
                elif event.key == pygame.K_r:
                    self.load_level(is_reset=True)
                elif event.key == pygame.K_BACKSPACE:
                    # Túa ngược 1 bước (Reverse Move - kéo hộp ngược lại)
                    if self.reverse_move.reverse(self.level.player, self.level.boxes, self.level.grid):
                        MapExporter.export(self.level)
                        if not self.sound_muted:
                            snd = self.asset_loader.get_sound("move")
                            if snd: snd.play()
                    
                if dx != 0 or dy != 0:
                    # Người chơi can thiệp bằng tay -> Dừng Tự Lái chặn luôn
                    if getattr(self, 'auto_play_queue', []):
                        print("\n[AI] KIỂM SOÁT BẰNG TAY: Đã hủy lệnh Tự Lái của AI.")
                        self.auto_play_queue = []
                        
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
        
        # Hàm con hỗ trợ Render Debug — mô phỏng Simple Hill Climbing
        def render_ai_debug_lines():
            import math
            from src.algorithms.solver_adapter import SolverAdapter
            try:
                adapter = SolverAdapter(self.level)
                initial_state = adapter.get_initial_state()
                neighbors = adapter.get_neighbors(initial_state)
                detail_h = adapter.get_detailed_heuristic_func()

                if not neighbors:
                    return

                # Baseline: H không prev_boxes (giống Simple HC: current_h = get_heuristic(state))
                current_score, _, _, _ = detail_h(initial_state)

                # Bước 1: Tìm hàng xóm ĐẦU TIÊN tốt hơn (Simple HC logic)
                simple_hc_choice = None
                raw_results = []
                for action, state in neighbors:
                    # decision_score: dùng prev_boxes (Simple HC so sánh thế này)
                    # = get_heuristic(next_state, current_state.boxes) trong Simple HC
                    decision_score, h1, h2, h3 = detail_h(state, initial_state.boxes)

                    # display_score: KHÔNG prev_boxes = H thật của state (khớp Excel)
                    # = get_heuristic(current_state) sau khi HC chuyển sang state mới
                    display_score, d_h1, d_h2, d_h3 = detail_h(state)

                    pushed = set(state.boxes) != set(initial_state.boxes)

                    # Euclidean từ vị trí player tiếp theo đến thùng gần nhất (tiebreaker)
                    nx_p, ny_p = state.player_pos
                    if initial_state.boxes:
                        euclid = min(
                            math.sqrt((nx_p - bx) ** 2 + (ny_p - by) ** 2)
                            for bx, by in initial_state.boxes
                        )
                    else:
                        euclid = 0.0

                    raw_results.append({
                        "action": action,
                        "decision_score": decision_score,   # dùng để quyết định TỐI ƯU
                        "display_score": display_score,     # dùng để hiển thị (khớp Excel)
                        "h1": d_h1, "h2": d_h2, "h3": d_h3,
                        "euclid": euclid, "state": state, "pushed": pushed
                    })

                    # Simple HC: first better (so sánh decision_score với current_score)
                    if simple_hc_choice is None and decision_score < current_score:
                        simple_hc_choice = action

                # Sắp xếp: cấp 1 = decision_score (gồm push bonus → đúng HC)
                #           cấp 2 = Euclidean (tiebreaker khi bằng nhau)
                raw_results.sort(key=lambda e: (e["decision_score"], e["euclid"]))

                # Đóng gói: hiển thị display_score nhưng sort/quyết định theo decision_score
                evaluated = [
                    (r["display_score"], r["decision_score"], r["euclid"],
                     r["h1"], r["h2"], r["h3"], r["action"], r["state"], r["pushed"])

                    for r in raw_results
                ]

                px = initial_state.player_pos[0] * self.tile_size + offset_x + self.tile_size // 2
                py = initial_state.player_pos[1] * self.tile_size + offset_y + self.tile_size // 2
                
                # --- Đẩy dữ liệu ra Tkinter Window ---
                info_data = []
                for idx, (display_score, decision_score, euclid, h1, h2, h3, action, state, pushed) in enumerate(evaluated):
                    # TỐI ƯU = Simple HC chọn: first neighbor có decision_score < current_score
                    if simple_hc_choice is not None:
                        is_min = (action == simple_hc_choice)
                    else:
                        is_min = (idx == 0)
                    push_label = " ★PUSH" if pushed else ""
                    info_data.append({
                        "action": action + push_label,
                        # Hiển thị display_score (không push bonus) = khớp Excel
                        "score": round(display_score, 4) if isinstance(display_score, float) else display_score,
                        "h1": round(h1, 1) if isinstance(h1, float) else h1,
                        "h2": round(h2, 1) if isinstance(h2, float) else h2,
                        "h3": round(h3, 1) if isinstance(h3, float) else h3,
                        "is_min": is_min
                    })
                    
                if self.debug_window and getattr(self.debug_window, 'is_ready', False):
                    self.debug_window.info_data = info_data
                    self.debug_window.current_h = round(current_score, 4) if isinstance(current_score, float) else current_score

                for idx, (display_score, decision_score, euclid, h1, h2, h3, action, state, pushed) in enumerate(evaluated):
                    if simple_hc_choice is not None:
                        is_min = (action == simple_hc_choice)
                    else:
                        is_min = (idx == 0)

                    dx, dy = 0, 0
                    if action == "LÊN": dy = -1
                    elif action == "XUỐNG": dy = 1
                    elif action == "TRÁI": dx = -1
                    elif action == "PHẢI": dx = 1
                    
                    nx = px + dx * self.tile_size
                    ny = py + dy * self.tile_size
                    
                    moved_boxes = set(state.boxes) - set(initial_state.boxes)
                    if moved_boxes:
                        new_box_pos = moved_boxes.pop()
                        old_bx = (new_box_pos[0] - dx) * self.tile_size + offset_x + self.tile_size // 2
                        old_by = (new_box_pos[1] - dy) * self.tile_size + offset_y + self.tile_size // 2
                        new_bx = new_box_pos[0] * self.tile_size + offset_x + self.tile_size // 2
                        new_by = new_box_pos[1] * self.tile_size + offset_y + self.tile_size // 2
                        start_pt, end_pt = (old_bx, old_by), (new_bx, new_by)
                    else:
                        start_pt, end_pt = (px, py), (nx, ny)
                        
                    line_color = (0, 255, 0) if is_min else (255, 0, 0)
                    thickness = 2
                    pygame.draw.line(self.screen, line_color, start_pt, end_pt, thickness)
                    # Vẽ đầu mũi tên (arrowhead) bằng 2 đoạn ngắn
                    import math as _m
                    ex, ey = end_pt
                    sx, sy = start_pt
                    angle = _m.atan2(ey - sy, ex - sx)
                    arr_len = 10
                    arr_angle = 0.5
                    for sign in (1, -1):
                        ax = ex - arr_len * _m.cos(angle - sign * arr_angle)
                        ay = ey - arr_len * _m.sin(angle - sign * arr_angle)
                        pygame.draw.line(self.screen, line_color, end_pt, (int(ax), int(ay)), thickness)
                        
            except Exception as e:
                print(e)
                pass
        
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
        if self.ai_debug_mode and not self.won:
            render_ai_debug_lines()
            
        if self.ai_menu_active:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0,0))
            
            font_title = pygame.font.SysFont("tahoma", 42, bold=True)
            font_opt = pygame.font.SysFont("tahoma", 26, bold=True)
            
            title = font_title.render("HỆ THỐNG AI CHO SOKOBAN", True, (255, 255, 255))
            opt1 = font_opt.render("[1] Phân tích Heuristic theo Simple Hill Climbing", True, (0, 255, 0))
            opt2 = font_opt.render("[2] Chạy ngầm 8 Thuật toán và Tự Lái (Auto Drive)", True, (255, 255, 0))
            opt3 = font_opt.render("[3] Hủy Tự Lái & Tắt tia Laser", True, (255, 100, 100))
            opt4 = font_opt.render("[SPACE/ESC] Đóng menu", True, (150, 150, 150))
            
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
            self.screen.blit(opt1, (SCREEN_WIDTH//2 - opt1.get_width()//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(opt2, (SCREEN_WIDTH//2 - opt2.get_width()//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(opt3, (SCREEN_WIDTH//2 - opt3.get_width()//2, SCREEN_HEIGHT//2 + 90))
            self.screen.blit(opt4, (SCREEN_WIDTH//2 - opt4.get_width()//2, SCREEN_HEIGHT//2 + 150))
            
        pygame.display.flip()

    def run(self):
        running = True
        dt = 0.0
        while running:
            running = self.handle_events()
            
            # --- Tự động chơi (Auto-play AI) ---
            if getattr(self, 'auto_play_queue', []) and not self.won:
                if self.time_passed - self.last_auto_move_time > 0.15: # 150ms 1 bước chạy AI
                    self.last_auto_move_time = self.time_passed
                    action = self.auto_play_queue.pop(0)
                    
                    dx, dy = 0, 0
                    if action == "LÊN": dy = -1
                    elif action == "XUỐNG": dy = 1
                    elif action == "TRÁI": dx = -1
                    elif action == "PHẢI": dx = 1
                    
                    if dx != 0 or dy != 0:
                        moved, pushed = self.movement_system.move(dx, dy)
                        if moved:
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
                                
                            if self.win_condition.check_win():
                                self.won = True
                                print("You Win! (AI AUTO DRIVED)")
                                if not self.sound_muted:
                                    win_sound = self.asset_loader.get_sound("win")
                                    if win_sound: win_sound.play()
            
            self.render(dt)
            dt = self.clock.tick(FPS) / 1000.0
            
        pygame.quit()
        sys.exit()
