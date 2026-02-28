from src.algorithms.deadlock import check_global_deadlock

# ==============================================================================
# CÔNG THỨC TỔ HỢP HEURISTIC 4 YẾU TỐ - SOKOBAN AI
# H_total = (W1 × H_Manhattan) + (W2 × H_Push) + (W3 × P_Deadlock) + (W4 × P_Goal)
# ==============================================================================

# Trọng số điều chỉnh (Tuning Weights)
W1 = 2.0    # Trọng số khoảng cách Manhattan (Hộp → Đích)
W2 = 0.5    # Trọng số vị trí đẩy tối ưu (Người → Push Pos)
W3 = 1000.0 # Hình phạt Deadlock (cực lớn để AI tránh xa)
W4 = -1.5   # Điểm thưởng (âm = tốt) khi đưa hộp vào đích ưu tiên/khó

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def compute_target_priority(target, grid):
    """Tính trọng số ưu tiên cho một đích.
    - Đích trong góc (2 tường kề vuông góc) → 2.0 (khó nhất, lấp trước).
    - Đích ở biên bản đồ → 1.5.
    - Đích bình thường → 1.0.
    """
    x, y = target
    walls = [grid.is_wall(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
    # Góc: 2 tường kề vuông góc nhau
    if (walls[0] and walls[2]) or (walls[0] and walls[3]) or (walls[1] and walls[2]) or (walls[1] and walls[3]):
        return 2.0
    # Biên bản đồ
    if x == 0 or y == 0 or x == grid.width - 1 or y == grid.height - 1:
        return 1.5
    return 1.0

def calculate_heuristic(state, targets, grid, dead_zones=None):
    """
    Công thức Tổ hợp 4 Yếu tố:
    H_total = (W1 × H_Manhattan) + (W2 × H_Push) + (W3 × P_Deadlock) + (W4 × P_Goal)

    1. H_Manhattan: Tổng khoảng cách các thùng chưa giải đến đích (Cơ bản).
    2. H_Push:      Khoảng cách người chơi đến vị trí đẩy tối ưu (Optimal Push Pos).
    3. P_Deadlock:  Điểm phạt cực lớn (∞) nếu rơi vào thế kẹt.
    4. P_Goal:      Điểm thưởng (âm) khi đưa hộp vào đích ưu tiên (góc/biên/khó).
    """

    # ===================== YẾU TỐ 3: P_Deadlock =====================
    # Nếu trạng thái bị kẹt cứng → trả về vô cực ngay
    if check_global_deadlock(state, grid, targets, dead_zones):
        return float('inf'), float('inf'), float('inf')

    # ===================== PHÂN LOẠI HỘP =====================
    box_positions = list(state.boxes)
    available_targets = targets.copy()
    unsolved_boxes = []
    solved_boxes = []  # Hộp đã nằm trên đích

    target_priorities = {t: compute_target_priority(t, grid) for t in available_targets}

    for box_pos in box_positions:
        if box_pos in available_targets:
            solved_boxes.append(box_pos)
            available_targets.remove(box_pos)
        else:
            unsolved_boxes.append(box_pos)

    # ===================== YẾU TỐ 1: H_Manhattan =====================
    # Tổng khoảng cách Manhattan từ mỗi hộp chưa giải đến đích tốt nhất
    # Dùng weighted matching: ưu tiên gán hộp vào đích khó (priority cao) trước
    h_manhattan = 0
    box_goal_pairs = []
    for box_pos in unsolved_boxes:
        if available_targets:
            best_target_idx = None
            best_weighted = None
            for i, tgt in enumerate(available_targets):
                dist = manhattan_distance(box_pos, tgt)
                priority = target_priorities.get(tgt, 1.0)
                weighted = dist / priority  # Ưu tiên đích có priority cao
                if best_weighted is None or weighted < best_weighted:
                    best_weighted = weighted
                    best_target_idx = i
            chosen_target = available_targets[best_target_idx]
            h_manhattan += manhattan_distance(box_pos, chosen_target)
            box_goal_pairs.append((box_pos, chosen_target))
            del target_priorities[chosen_target]
            available_targets.pop(best_target_idx)

    # ===================== YẾU TỐ 2: H_Push =====================
    # Khoảng cách người chơi đến vị trí đẩy tối ưu (Optimal_Push_Pos)
    # PushPos = (Box_x - dx, Box_y - dy) với (dx, dy) là hướng từ Box đến Goal
    h_push = 0
    if box_goal_pairs:
        min_push_dist = float('inf')
        for box_pos, goal_pos in box_goal_pairs:
            bx, by = box_pos
            gx, gy = goal_pos
            raw_dx = gx - bx
            raw_dy = gy - by
            # Chọn trục chính (delta lớn hơn) làm hướng đẩy ưu tiên
            if abs(raw_dx) >= abs(raw_dy):
                dx = 1 if raw_dx > 0 else (-1 if raw_dx < 0 else 0)
                dy = 0
            else:
                dx = 0
                dy = 1 if raw_dy > 0 else (-1 if raw_dy < 0 else 0)
            push_pos = (bx - dx, by - dy)
            dist = manhattan_distance(state.player_pos, push_pos)
            if dist < min_push_dist:
                min_push_dist = dist
        h_push = min_push_dist

    # ===================== YẾU TỐ 4: P_Goal =====================
    # Điểm thưởng cho mỗi hộp đã vào đúng đích (khuyến khích AI giữ hộp ở đích khó)
    # CHỈ dùng làm tiebreaker, KHÔNG cho phép triệt tiêu H_Manhattan
    p_goal = 0
    for box_pos in solved_boxes:
        priority = compute_target_priority(box_pos, grid)
        p_goal += priority

    # ===================== TỔNG HỢP =====================
    # Nếu KHÔNG còn hộp chưa giải → đích đã đạt (h = 0)
    if len(unsolved_boxes) == 0:
        return 0.0, 0.0, 0.0

    # H_total = (W1 × H_Manhattan) + (W2 × H_Push) + (W4 × P_Goal)
    # P_Goal chỉ là tiebreaker: giới hạn thưởng tối đa = 30% H_Manhattan
    manhattan_base = W1 * h_manhattan
    push_component = W2 * h_push
    goal_bonus = W4 * p_goal  # Giá trị âm (thưởng)
    
    # Giới hạn: thưởng không vượt quá 30% chi phí Manhattan
    max_bonus = -0.3 * manhattan_base
    if goal_bonus < max_bonus:
        goal_bonus = max_bonus

    h_total = manhattan_base + push_component + goal_bonus
    
    # An toàn: h_total phải > 0 khi còn hộp chưa giải
    if h_total <= 0:
        h_total = 0.1

    # Trả về: (tổng điểm, chi phí thùng, chi phí người)
    box_component = manhattan_base + goal_bonus
    player_component = push_component

    return h_total, box_component, player_component
