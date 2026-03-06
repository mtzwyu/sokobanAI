# src/algorithms/deadlock.py

def build_dead_zones(grid, targets):
    """
    Quy tắc 1: "Góc Chết" (Corner Deadlock) và "Cạnh Chết" (Edge Deadlock) - Tính 1 lần dùng mãi mãi.
    Tìm tất cả các Ô Tử Thần ngay từ đầu game.
    Nếu một ô trống nằm ở góc (có tường chắn 2 bên vuông góc) và ô đó không phải là đích -> Dead Zone.
    Kết hợp Reverse BFS để lấy luôn các ô Cạnh Chết tĩnh.
    """
    dead_zones = set()
    
    # 1. Quét Góc Chết (Corner Deadlock) cơ bản
    for y in range(grid.height):
        for x in range(grid.width):
            if grid.is_wall(x, y) or grid.is_outside(x, y):
                continue
            if (x, y) in targets:
                continue
                
            # Kiểm tra xem có phải là góc không (chặn 2 bên vuông góc)
            up = grid.is_wall(x, y-1) or grid.is_outside(x, y-1)
            down = grid.is_wall(x, y+1) or grid.is_outside(x, y+1)
            left = grid.is_wall(x-1, y) or grid.is_outside(x-1, y)
            right = grid.is_wall(x+1, y) or grid.is_outside(x+1, y)
            
            if (up and left) or (up and right) or (down and left) or (down and right):
                dead_zones.add((x, y))

    # 2. Reverse BFS chạy một lần từ đích để bao trọn nốt các Cạnh Chết tĩnh (Edge Deadlocks)
    # Giúp AI thông minh hơn gấp bội mà không tốn chi phí tính toán khi chạy (vẫn là tính 1 lần).
    valid_cells = set(targets)
    queue = list(targets)
    
    while queue:
        c, r = queue.pop(0)
        
        for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            prev_c, prev_r = c - dc, r - dr
            player_c, player_r = c - 2 * dc, r - 2 * dr
            
            if not grid.is_wall(prev_c, prev_r) and not grid.is_outside(prev_c, prev_r):
                if not grid.is_wall(player_c, player_r) and not grid.is_outside(player_c, player_r):
                    if (prev_c, prev_r) not in valid_cells:
                        valid_cells.add((prev_c, prev_r))
                        queue.append((prev_c, prev_r))
                        
    for y in range(grid.height):
        for x in range(grid.width):
            if not grid.is_wall(x, y) and not grid.is_outside(x, y):
                if (x, y) not in valid_cells:
                    dead_zones.add((x, y))
                    
    return dead_zones

def is_2x2_square_deadlock(state, grid, targets):
    """
    Quy tắc 2: "Khối 2x2" (Square Deadlock) - Diệt tận gốc vụ Thùng dính nhau.
    Nếu một khối 2x2 (4 ô liền kề tạo thành hình vuông) đặc khít (toàn Tường hoặc Thùng), 
    và trong 4 ô đó KHÔNG có ô nào là Đích -> DEADLOCK (Không thể nào phá vỡ/kéo thùng ra được).
    """
    boxes_set = set(state.boxes)
    # Dùng set lưu top-left corner (tx, ty) để tránh check trùng lặp cấu trúc 4 ô
    checked_top_lefts = set()
    
    for bx, by in state.boxes:
        # Một thùng (bx, by) có thể là 1 trong 4 góc của 4 hình vuông 2x2 xung quanh nó
        top_left_candidates = [
            (bx, by),       # Thùng ở góc trên-trái
            (bx-1, by),     # Thùng ở góc trên-phải
            (bx, by-1),     # Thùng ở góc dưới-trái
            (bx-1, by-1)    # Thùng ở góc dưới-phải
        ]
        
        for tx, ty in top_left_candidates:
            if (tx, ty) in checked_top_lefts:
                continue
            checked_top_lefts.add((tx, ty))
            
            # Khởi tạo 4 tọa độ của khối vuông 2x2 này
            square_cells = [
                (tx, ty),     (tx+1, ty),
                (tx, ty+1),   (tx+1, ty+1)
            ]
            
            # Kiểm tra xem có Đích nào nằm trong 4 ô này không
            has_target = False
            for cx, cy in square_cells:
                if (cx, cy) in targets:
                    has_target = True
                    break
                    
            if has_target:
                continue # Nếu có đích thì an toàn, bỏ qua khối này
                
            # Nếu KHÔNG CÓ ĐÍCH, kiểm tra xem cả 4 ô có ĐẶC (Tường hoặc Thùng) không
            is_solid = True
            for cx, cy in square_cells:
                if not (grid.is_wall(cx, cy) or grid.is_outside(cx, cy) or (cx, cy) in boxes_set):
                    is_solid = False
                    break # Có lỗ hổng trống -> chưa phải Deadlock khép kín 2x2
                    
            if is_solid:
                return True # Phát hiện Khối 2x2 Đặc không chứa đích -> Deadlock!
                
    return False

def check_global_deadlock(state, grid, targets, dead_zones=None):
    """
    Trình kiểm tra Deadlock tối giản và siêu tốc độ dựa trên đúng 2 Quy tắc:
    1. "Góc Chết" (Ô Tử Thần tính 1 lần từ đầu game).
    2. "Khối 2x2" (Phát hiện thùng dính nhau hoặc cọ tường tạo khối).
    """
    if dead_zones is None:
        dead_zones = set()
        
    for box in state.boxes:
        # Miễn kiểm tra những thùng đã nằm trên Đích
        if box in targets:
            continue
            
        # QUY TẮC 1: Nếu lọt vào "Ô Tử Thần" tĩnh (Dead Zones tính sẵn) -> DEADLOCK ngay lập tức O(1)
        if box in dead_zones:
            return True
            
    # QUY TẮC 2: Kiểm tra vụ Thùng dính nhau theo "Khối vuông 2x2"
    if is_2x2_square_deadlock(state, grid, targets):
        return True
        
    return False
