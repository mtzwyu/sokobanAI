import random
from src.utils.constants import WALL, TARGET, BOX, PLAYER, EMPTY, UP, DOWN, LEFT, RIGHT, OUTSIDE

import math

class LevelGenerator:
    def __init__(self, num_boxes: int = 3, steps: int = 100):
        # Chúng ta cần đủ diện tích bên trong cho hộp, mục tiêu, chướng ngại vật và người chơi.
        # Tạm tính cần khoảng 15 khoảng trống bên trong cho mỗi hộp để có không gian di chuyển.
        min_inner_area = num_boxes * 15
        
        # Tỷ lệ khung hình cơ sở cho màn hình 800x600
        target_width_ratio = 4
        target_height_ratio = 3
        
        multiplier = 4 # Bắt đầu ở bản đồ 16x12
        while True:
            width = target_width_ratio * multiplier
            height = target_height_ratio * multiplier
            
            # Tính diện tích bên trong hiện tại (bỏ qua 2 ô lề ở mỗi bên)
            current_inner = max(0, width - 4) * max(0, height - 4)
            if current_inner >= min_inner_area:
                break
            multiplier += 1
            
        self.width = width
        self.height = height
        self.num_boxes = num_boxes
        self.steps = steps
        
        self.grid = [[EMPTY for x in range(self.width)] for y in range(self.height)]
        self.targets = []
        self.boxes = []
        self.player = None

    def create_empty_room(self):
        for y in range(self.height):
            for x in range(self.width):
                # Tường bao ngoài bắt buộc
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.grid[y][x] = WALL
                else:
                    self.grid[y][x] = EMPTY
                    
        # Thêm các khối đá ngẫu nhiên ở phần viền bên trong để rìa bản đồ không vuông vắn
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Tính khoảng cách tới bờ gần nhất
                dist_x = min(x, self.width - 1 - x)
                dist_y = min(y, self.height - 1 - y)
                dist = min(dist_x, dist_y)
                
                # Càng gần biên, xác suất biến thành đá càng cao để tạo hình dáng tự nhiên
                if dist == 1:
                    if random.random() < 0.4:
                        self.grid[y][x] = WALL
                elif dist == 2:
                    if random.random() < 0.1:
                        self.grid[y][x] = WALL

    def generate(self):
        attempts = 0
        base_steps = max(self.steps, self.num_boxes * 400)
        
        while attempts < 1000:
            attempts += 1
            self.create_empty_room()
            
            # 0. Đặt một số bức tường chướng ngại vật ngẫu nhiên trong phòng
            # Đặt chúng trước mục tiêu/hộp để đảm bảo thuật toán đi lùi
            # vẫn giải được khi có những bức tường này.
            available_spots = [(x, y) for x in range(2, self.width - 2) for y in range(2, self.height - 2)]
            
            # Giảm bớt chướng ngại vật nếu gặp khó khăn khi tạo level hợp lệ, nhưng không bỏ hẳn
            obstacle_divisor = 15 if attempts < 100 else 30
            num_obstacles = random.randint(1, max(1, (self.width * self.height) // obstacle_divisor))
            obstacle_spots = random.sample(available_spots, min(num_obstacles, len(available_spots)))
            for ox, oy in obstacle_spots:
                self.grid[oy][ox] = WALL
                
            # Tính lại các khoảng trống khả dụng sau khi đặt tường
            available_spots = [(x, y) for x in range(2, self.width - 2) for y in range(2, self.height - 2) if self.grid[y][x] == EMPTY]
            
            if len(available_spots) < self.num_boxes + 1:
                continue # Không đủ không gian, thử lại
                
            random.shuffle(available_spots)
            
            self.targets = available_spots[:int(self.num_boxes)]
            
            # 2. Đặt các hộp bắt đầu ở vị trí mục tiêu
            self.boxes = list(self.targets)
            
            # 3. Đặt người chơi ở vị trí ngẫu nhiên
            player_spots = [s for s in available_spots[int(self.num_boxes):]]
            if not player_spots:
                player_spots = [(1, 1)] # dự phòng
            self.player = player_spots[0]
            
            # 4. Các bước đi lùi ngẫu nhiên (Tăng số bước khi quá trình tạo level gặp khó khăn)
            directions = [UP, DOWN, LEFT, RIGHT]
            current_steps = base_steps + (attempts * 100)
            
            for _ in range(current_steps):
                random.shuffle(directions)
                for dx, dy in directions:
                    if self.try_reverse_move(dx, dy):
                        break
                        
            # Bắt buộc kéo toàn bộ 100% số hộp ra khỏi điểm đích
            boxes_off_targets = sum(1 for box in self.boxes if box not in self.targets)
            if boxes_off_targets == self.num_boxes:
                self.shave_walls()
                return self.export_lines()
                
        # Phòng hờ: nếu không thể tìm thấy bản đồ hoàn hảo sau 200 lần thử, 
        # trả về bản đồ tốt nhất có thể để ngăn trò chơi bị treo vĩnh viễn.
        self.shave_walls()
        return self.export_lines()
        
    def try_reverse_move(self, dx, dy):
        px, py = self.player
        new_px, new_py = px - dx, py - dy
        
        if self.grid[new_py][new_px] == WALL:
            return False
            
        # Kiểm tra xem người chơi có đang kéo một cái hộp không
        box_pos = (px + dx, py + dy)
        if box_pos in self.boxes:
            # Chúng ta có thể kéo hộp về vị trí hiện tại của người chơi
            if (px, py) not in self.boxes and self.grid[py][px] != WALL:
                # Thực hiện kéo
                self.boxes.remove(box_pos)
                self.boxes.append((px, py))
                self.player = (new_px, new_py)
                return True
                
        # Ràng buộc đi bộ bình thường: đảm bảo người chơi không giẫm lên hộp khi đi lùi
        if (new_px, new_py) not in self.boxes:
            self.player = (new_px, new_py)
            return True
            
        return False
        
    def shave_walls(self):
        # 1. Tìm tất cả các ô có thể đi tới từ player (vùng có thể chơi được)
        inside_spaces = set()
        queue = [self.player]
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) not in inside_spaces:
                inside_spaces.add((cx, cy))
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.grid[ny][nx] != WALL and (nx, ny) not in inside_spaces:
                            queue.append((nx, ny))
                            
        # 2. Tìm tất cả các bức tường kề sát với vùng chơi (needed_walls)
        needed_walls = set()
        for cx, cy in inside_spaces:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.grid[ny][nx] == WALL:
                            needed_walls.add((nx, ny))
                            
        # 3. Biến đổi tất cả các ô không phải bên trong và không phải tường bao thành OUTSIDE
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in inside_spaces and (x, y) not in needed_walls:
                    self.grid[y][x] = OUTSIDE

    def export_lines(self):
        result = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if self.grid[y][x] == WALL:
                    line += WALL
                elif self.grid[y][x] == OUTSIDE:
                    line += OUTSIDE
                elif (x, y) in self.boxes and (x, y) in self.targets:
                    line += '*' # Về lý thuyết không gặp nữa, nhưng giữ để đề phòng rủi ro
                elif (x, y) in self.boxes:
                    line += BOX
                elif (x, y) == self.player:
                    if (x, y) in self.targets:
                        line += '+'
                    else:
                        line += PLAYER
                elif (x, y) in self.targets:
                    line += TARGET
                else:
                    line += EMPTY
            result.append(line)
        return result
