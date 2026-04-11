from collections import deque
import math
import numpy as np
from scipy.optimize import linear_sum_assignment
from src.algorithms.deadlock import check_global_deadlock

# ==============================================================================
# HEURISTIC TỐI ƯU - SOKOBAN AI
#
# H(S) = Wt * Σ dist(Bi, T_σ(i))   [Chi phí Vận chuyển - BFS + Hungarian]
#       + Wa * min_j(dist(P, Bj)-1) [Chi phí Tiếp cận  - Khoảng cách đến chỗ đẩy]
#       + Wp * Σ Penalty(k)          [Điểm phạt Rủi ro  - Tổng hợp các thế nguy hiểm]
#
# Bộ tham số khuyến nghị:
#   Wt = 1.0     → Yếu tố chính: đưa thùng về đích.
#   Wa = 0.1     → Yếu tố phụ: định hướng người chơi, không lấn át H1.
#   Wp = 1000.0  → Yếu tố sống còn: phạt cực nặng để AI sợ deadlock.
#
# Penalty(k) per box:
#   ∞    → Kẹt góc chết (Deadlock toàn cục)
#   100  → Dính chùm 2x2 (Frozen)
#   10   → Sát tường mà không ở đích
#   0    → An toàn
# ==============================================================================

Wt    = 1.0
Wa    = 0.5   # Tăng từ 0.1 lên 0.5 → H2 tạo chênh lệch rõ hơn giữa các hướng
Wp    = 1000.0
W_done = 1000.0  # Phạt mỗi thùng CHƯA vào đích → ngăn AI đẩy thùng ra khỏi đích
Wb    = 0.05  # H5 = Euclidean + wrong-side penalty: tạo gradient rõ ràng theo hướng push
              # 0.05 × (dist≈2 + wrong_side≈1×0.5) → chênh lệch 0.025+ giữa PHẢI vs XUỐNG

W_push = 0.5  # Bonus ưu tiên nước đẩy hộp — phá vỡ tie khi H bằng nhau

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ------------------------------------------------------------------------------
# BƯỚC 1: Xây dựng "Bản đồ khoảng cách" (Distance Map) - Tính 1 lần mỗi màn
# BFS multi-source từ tất cả Đích → dist_map[(x,y)] = khoảng cách đến đích gần nhất
# ------------------------------------------------------------------------------

def build_dist_maps(grid, targets):
    """
    BFS từ TỪNG đích. dist_maps[g][pos] = số bước thực tế (né tường) 
    để đưa thùng tại pos về đích g.
    """
    dist_maps = {}
    for t in targets:
        dist_map = {}
        queue = deque()
        dist_map[t] = 0
        queue.append(t)

        while queue:
            x, y = queue.popleft()
            cur_d = dist_map[(x, y)]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in dist_map:
                    if not grid.is_wall(nx, ny) and not grid.is_outside(nx, ny):
                        dist_map[(nx, ny)] = cur_d + 1
                        queue.append((nx, ny))
        dist_maps[t] = dist_map
    return dist_maps

def build_player_dist_map(grid, start, boxes=None):
    """
    BFS từ vị trí người chơi.
    boxes: tập hợp các vị trí hộp hiện tại — được coi là VT CHỌ CẢN (không đi xuyên qua được).
    Không truyền boxes → chỉ kiểm tra tường (dùng cho dist_maps của hộp).
    """
    blocked = set(boxes) if boxes else set()
    dist = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in dist:
                if not grid.is_wall(nx, ny) and not grid.is_outside(nx, ny) and (nx, ny) not in blocked:
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    queue.append((nx, ny))
    return dist

# ------------------------------------------------------------------------------
# BƯỚC 2: H1 - Chi phí Vận chuyển (Transport Cost) - Hungarian Algorithm
# Σ dist(Bi, T_σ(i)) — Phân công tối ưu Thùng → Đích bằng Hungarian
# ------------------------------------------------------------------------------

def calc_h1(unplaced_boxes, unmatched_goals, dist_maps):
    if not unplaced_boxes or not unmatched_goals:
        return 0.0, []

    n, m = len(unplaced_boxes), len(unmatched_goals)
    # Khởi tạo ma trận chi phí
    cost_matrix = np.zeros((n, m))
    for i, b in enumerate(unplaced_boxes):
        for j, g in enumerate(unmatched_goals):
            # Dùng dist_maps (BFS thực tế), fallback về Manhattan nếu ô không đến được
            if g in dist_maps and b in dist_maps[g]:
                cost_matrix[i][j] = dist_maps[g][b]
            else:
                cost_matrix[i][j] = manhattan_distance(b, g)

    # Phân công công việc bằng Hungarian Algorithm
    box_idx, goal_idx = linear_sum_assignment(cost_matrix)
    
    assignments = []
    for i, j in zip(box_idx, goal_idx):
        assignments.append((unplaced_boxes[i], unmatched_goals[j]))
        
    return float(cost_matrix[box_idx, goal_idx].sum()), assignments

# ------------------------------------------------------------------------------
# BƯỚC 3: H2 - Chi phí Tiếp cận (Accessibility Cost)
# min_j( dist(P, Bj) - 1 ) — Khoảng cách từ Player đến vị trí đẩy của thùng gần nhất
# (Trừ 1 vì người chơi cần đứng CẠNH thùng, không đứng TRÙNG thùng)
# ------------------------------------------------------------------------------

def calc_h2(player_pos, unplaced_boxes, dist_maps, assignments, grid, player_dist=None):
    """
    Chi phí Tiếp cận: BFS distance + Euclidean tie-breaker.
    player_dist: BFS map từ player — truyền vào để tránh tính lại.
    """
    if not unplaced_boxes:
        return 0
    
    if player_dist is None:
        player_dist = build_player_dist_map(grid, player_pos)
    
    best_bfs = float('inf')
    best_euc = float('inf')
    
    for b, g in assignments:
        bx, by = b
        g_dist_map = dist_maps.get(g, {})
        cur_d = g_dist_map.get(b, float('inf'))
        
        if cur_d == float('inf'):
            continue
        
        valid_push_found = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_b = (bx + dx, by + dy)
            push_pos = (bx - dx, by - dy)
            
            if grid.is_wall(push_pos[0], push_pos[1]) or grid.is_outside(push_pos[0], push_pos[1]):
                continue
            if grid.is_wall(next_b[0], next_b[1]) or grid.is_outside(next_b[0], next_b[1]):
                continue
            
            if g_dist_map.get(next_b, float('inf')) < cur_d:
                d_bfs = player_dist.get(push_pos, float('inf'))
                d_euc = math.sqrt((player_pos[0] - push_pos[0])**2 + (player_pos[1] - push_pos[1])**2)
                
                # So sánh: BFS chấm điểm chính, Euclidean phá vỡ tie
                if d_bfs < best_bfs or (d_bfs == best_bfs and d_euc < best_euc):
                    best_bfs = d_bfs
                    best_euc = d_euc
                valid_push_found = True
        
        if not valid_push_found:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adj = (bx + dx, by + dy)
                if not grid.is_wall(adj[0], adj[1]) and not grid.is_outside(adj[0], adj[1]):
                    d_bfs = player_dist.get(adj, float('inf'))
                    d_euc = math.sqrt((player_pos[0] - adj[0])**2 + (player_pos[1] - adj[1])**2)
                    if d_bfs < best_bfs or (d_bfs == best_bfs and d_euc < best_euc):
                        best_bfs = d_bfs
                        best_euc = d_euc
    
    if best_bfs == float('inf'):
        return max(0, min(manhattan_distance(player_pos, b) - 1 for b in unplaced_boxes))
    
    # H2 = BFS (chủ đạo, chính xác, tránh tường) + 0.001*Euclidean (phá tie mức 1)
    # 0.001 an toàn: max Euclidean ≈70 →0.07 < 1 BFS step → không ânh hưởng thứ tự BFS thật
    return float(best_bfs) + 0.001 * best_euc

# ------------------------------------------------------------------------------
# BƯỚC 4: H3 - Điểm phạt Rủi ro (Penalty Score)
# Penalty(k) per box (chưa ở đích):
#   ∞   → Kẹt góc chết (2 hướng vuông góc bị tường chặn)
#   100 → Dính khối 2×2 (2 thùng cạnh nhau tạo cụm nguy hiểm)
#   10  → Sát tường đơn thuần
# ------------------------------------------------------------------------------

def calc_h3(state, grid, targets):
    penalty = 0.0
    boxes = state.boxes

    for box in boxes:
        if box in targets:
            continue  # An toàn, bỏ qua
        
        x, y = box

        up    = grid.is_wall(x, y-1) or grid.is_outside(x, y-1)
        down  = grid.is_wall(x, y+1) or grid.is_outside(x, y+1)
        left  = grid.is_wall(x-1, y) or grid.is_outside(x-1, y)
        right = grid.is_wall(x+1, y) or grid.is_outside(x+1, y)

        # Góc chết (∞ → trả infinity, hàm cha sẽ bắt)
        if (up and left) or (up and right) or (down and left) or (down and right):
            return float('inf')

        # Dính chùm 2x2 (+100)
        has_cluster = False
        for other in boxes:
            if other != box and other not in targets:
                if abs(other[0] - x) + abs(other[1] - y) == 1:
                    has_cluster = True
                    break
        if has_cluster:
            penalty += 100
            continue  # Đã phạt 100, bỏ qua kiểm tra sát tường

        # Sát tường đơn thuần (+10)
        if up or down or left or right:
            penalty += 10

    return penalty

# ==============================================================================
# HÀM TỔNG HỢP CHÍNH
# ==============================================================================

def calculate_heuristic(state, targets, grid, dead_zones=None, dist_maps=None, prev_boxes=None):
    """
    H(S) = Wt×H1 + Wa×H2 + Wp×H3 + H4 + Wb×H5 − W_push×[push_bonus]

    prev_boxes: tuple vị trí các hộp ở trạng thái TRƯỚC đó.
                Nếu được truyền vào, hàm sẽ tự nhận ra nước đẩy hộp
                và trừ W_push (0.5) vào h_total để ưu tiên nước push.

    Chiến thắng khi H(S) = 0 (tất cả thùng đã về đích, không còn rủi ro).
    """
    # --- Deadlock tuyệt đối (check_global_deadlock: góc chết tĩnh + 2x2 động) ---
    if check_global_deadlock(state, grid, targets, dead_zones):
        return float('inf'), float('inf'), float('inf'), float('inf')

    # --- Phân loại Thùng và Đích chưa khớp ---
    unplaced_boxes  = [b for b in state.boxes if b not in targets]
    unmatched_goals = [g for g in targets if g not in state.boxes]

    # --- BFS dist_maps fallback nếu không được truyền vào ---
    if dist_maps is None:
        dist_maps = build_dist_maps(grid, targets)

    # --- H1: Transport Cost (Hungarian + BFS) ---
    h1, assignments = calc_h1(unplaced_boxes, unmatched_goals, dist_maps)

    # Tính player_dist MỘT LẦN, coi hộp hiện tại là VẬT CHẨN (không đi xuyên băng được)
    # FIX: trước đây không truyền boxes → BFS đi xuyên hộp → tạo local minimum giả
    player_dist = build_player_dist_map(grid, state.player_pos, state.boxes)

    # --- H2: Accessibility Cost (BFS từ player đến push_pos tốt nhất) ---
    h2 = calc_h2(state.player_pos, unplaced_boxes, dist_maps, assignments, grid, player_dist)

    # --- H3: Penalty Score (Góc chết, Dính chùm, Sát tường) ---
    h3 = calc_h3(state, grid, targets)

    if h3 == float('inf'):
        return float('inf'), float('inf'), float('inf'), float('inf')

    # --- H4: Phạt thùng chưa vào đích (Bảo vệ thùng đã an toàn) ---
    h4 = W_done * len(unplaced_boxes)

    # --- H5: BFS đến push_pos + Euclidean tie-breaker ---
    # Dùng BFS thật (không phải Euclidean thẳng) để tránh local minimum giả:
    # Khi player cần đi VÒNG quanh hộp để đến push_pos, Euclidean vẫn ngắn
    # nhưng BFS sẽ dài hơn → phản ánh đúng thực tế.
    # H5 = BFS_to_push_pos + 0.001 * Euclidean (phá tie mức 2).
    # Wb = 0.05: đủ rõ để hiện thị tại 1-2 số thập phân.
    h5 = 0.0
    if unplaced_boxes and assignments:
        px, py = state.player_pos
        best_bfs5 = float('inf')
        best_euc5 = float('inf')

        for b, g in assignments:
            bx, by = b
            g_dist_map = dist_maps.get(g, {})
            cur_d = g_dist_map.get(b, float('inf'))
            if cur_d == float('inf'):
                continue

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_b = (bx + dx, by + dy)
                push_pos = (bx - dx, by - dy)

                if grid.is_wall(push_pos[0], push_pos[1]) or grid.is_outside(push_pos[0], push_pos[1]):
                    continue
                if grid.is_wall(next_b[0], next_b[1]) or grid.is_outside(next_b[0], next_b[1]):
                    continue
                if g_dist_map.get(next_b, float('inf')) < cur_d:
                    # BFS thật — tránh local minimum khi cần đi vòng
                    d_bfs5 = player_dist.get(push_pos, float('inf'))
                    # Euclidean tiếp theo phá tie giữa các push_pos cùng BFS
                    d_euc5 = math.sqrt((px - push_pos[0])**2 + (py - push_pos[1])**2)
                    if d_bfs5 < best_bfs5 or (d_bfs5 == best_bfs5 and d_euc5 < best_euc5):
                        best_bfs5 = d_bfs5
                        best_euc5 = d_euc5

        if best_bfs5 == float('inf'):
            best_bfs5 = min(player_dist.get(b, float('inf')) for b in unplaced_boxes)
            best_euc5 = min(
                math.sqrt((px - b[0])**2 + (py - b[1])**2)
                for b in unplaced_boxes
            )
            if best_bfs5 == float('inf'):
                best_bfs5 = 0
                best_euc5 = 0

        h5 = float(best_bfs5) + 0.001 * best_euc5

    # --- Tổng hợp: H = Wt×H1 + Wa×H2 + Wp×H3 + H4 + Wb×H5 ---
    # Wb = 0.05 → H5 tạo gradient rõ ràng theo hướng tiếp cận push_pos đúng cạnh
    h_total = (Wt * h1) + (Wa * h2) + (Wp * h3) + h4 + (Wb * h5)


    # --- Push Bonus (nằm TRONG heuristic) ---
    if prev_boxes is not None:
        moved_boxes = set(state.boxes) - set(prev_boxes)
        if moved_boxes and 0 < h_total < float('inf'):
            h_total -= W_push

    return float(h_total), float(h1), float(h2), float(h3)

