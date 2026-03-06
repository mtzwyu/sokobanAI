from collections import deque
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
Wa    = 0.1
Wp    = 1000.0
W_done = 1000.0  # Phạt mỗi thùng CHƯA vào đích → ngăn AI đẩy thùng ra khỏi đích

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ------------------------------------------------------------------------------
# BƯỚC 1: Xây dựng "Bản đồ khoảng cách" (Distance Map) - Tính 1 lần mỗi màn
# BFS multi-source từ tất cả Đích → dist_map[(x,y)] = khoảng cách đến đích gần nhất
# ------------------------------------------------------------------------------

def build_dist_map(grid, targets):
    """
    BFS đa nguồn từ các Đích. dist_map[pos] = số bước thực tế (né tường) 
    để đưa thùng tại pos về đích gần nhất.
    """
    dist_map = {}
    queue = deque()
    for t in targets:
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
    return dist_map

# ------------------------------------------------------------------------------
# BƯỚC 2: H1 - Chi phí Vận chuyển (Transport Cost) - Hungarian Algorithm
# Σ dist(Bi, T_σ(i)) — Phân công tối ưu Thùng → Đích bằng Hungarian
# ------------------------------------------------------------------------------

def calc_h1(unplaced_boxes, unmatched_goals, dist_map):
    if not unplaced_boxes or not unmatched_goals:
        return 0

    n, m = len(unplaced_boxes), len(unmatched_goals)
    cost_matrix = np.zeros((n, m))
    for i, b in enumerate(unplaced_boxes):
        for j, g in enumerate(unmatched_goals):
            # Dùng dist_map (BFS thực tế), fallback về Manhattan nếu ô không đến được
            cost_matrix[i][j] = dist_map.get(b, manhattan_distance(b, g))

    box_idx, goal_idx = linear_sum_assignment(cost_matrix)
    return float(cost_matrix[box_idx, goal_idx].sum())

# ------------------------------------------------------------------------------
# BƯỚC 3: H2 - Chi phí Tiếp cận (Accessibility Cost)
# min_j( dist(P, Bj) - 1 ) — Khoảng cách từ Player đến vị trí đẩy của thùng gần nhất
# (Trừ 1 vì người chơi cần đứng CẠNH thùng, không đứng TRÙNG thùng)
# ------------------------------------------------------------------------------

def calc_h2(player_pos, unplaced_boxes):
    if not unplaced_boxes:
        return 0
    # dist(P, Bj) - 1: khoảng cách đến ngay cạnh thùng (vị trí sẽ đứng để đẩy)
    return max(0, min(manhattan_distance(player_pos, b) - 1 for b in unplaced_boxes))

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

def calculate_heuristic(state, targets, grid, dead_zones=None, dist_map=None):
    """
    H(S) = Wt × H1  +  Wa × H2  +  Wp × H3

    Chiến thắng khi H(S) = 0 (tất cả thùng đã về đích, không còn rủi ro).
    """
    # --- Deadlock tuyệt đối (check_global_deadlock: góc chết tĩnh + 2x2 động) ---
    if check_global_deadlock(state, grid, targets, dead_zones):
        return float('inf'), float('inf'), float('inf')

    # --- Phân loại Thùng và Đích chưa khớp ---
    unplaced_boxes  = [b for b in state.boxes if b not in targets]
    unmatched_goals = [g for g in targets if g not in state.boxes]

    # --- BFS dist_map fallback nếu không được truyền vào ---
    if dist_map is None:
        dist_map = build_dist_map(grid, targets)

    # --- H1: Transport Cost (Hungarian + BFS) ---
    h1 = calc_h1(unplaced_boxes, unmatched_goals, dist_map)

    # --- H2: Accessibility Cost (Player → vị trí đẩy gần nhất) ---
    h2 = calc_h2(state.player_pos, unplaced_boxes)

    # --- H3: Penalty Score (Góc chết, Dính chùm, Sát tường) ---
    h3 = calc_h3(state, grid, targets)

    if h3 == float('inf'):
        return float('inf'), float('inf'), float('inf')

    # --- H4: Phạt thùng chưa vào đích (Bảo vệ thùng đã an toàn) ---
    # Mỗi thùng chưa ở đích bị phạt W_done.
    # → Nếu AI đẩy thùng ra khỏi đích, số unplaced_boxes tăng 1 → H tăng W_done ngay
    h4 = W_done * len(unplaced_boxes)

    # --- Tổng hợp theo công thức ---
    h_total = (Wt * h1) + (Wa * h2) + (Wp * h3) + h4

    return float(h_total), float(h1), float(h2)
