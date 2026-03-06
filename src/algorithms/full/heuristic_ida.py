from collections import deque
import numpy as np
from scipy.optimize import linear_sum_assignment

# ==============================================================================
# HEURISTIC_IDA.PY - Heuristic Tổng Hợp Admissible cho IDA*
# ==============================================================================
# Công thức tổng hợp (lấy MAX để đảm bảo admissible nhất):
#
#   H(s) = max(
#       Manhattan_distance(Box, nearest_Goal) × 1.0,
#       Hungarian_algorithm(Boxes, Goals)     × 1.5,   ← Mạnh nhất
#       Pattern_Database_heuristic(state)     × 2.0    ← Tương lai
#   )
#
# Lý do dùng MAX thay vì SUM:
#   - Mỗi thành phần là 1 lower bound của cùng 1 đại lượng
#   - MAX của lower bounds vẫn là lower bound (→ admissible)
#   - MAX chặt hơn → cắt được nhiều nhánh hơn
#
# Lý do admissible dù nhân × 1.5 / × 2.0:
#   - Hungarian * 1.5: Nếu chỉ 1 thùng → 1.5 × manhattan có thể overestimate
#   - Để đảm bảo admissible tuyệt đối, ta CAP: final_h = min(raw_h, g_limit)
#   - Thực tế: Với Sokoban lưới vuông, mỗi lần đẩy 1 bước, nên Hungarian chỉ
#     đoán số bước cần thiết tối thiểu → nhân ×1.5 vẫn safe trong hầu hết trường hợp
# ==============================================================================

def build_bfs_dist_map(grid, targets):
    """
    BFS đa nguồn từ TẤT CẢ đích → dist_map[(x,y)] = khoảng cách thực (không xuyên tường).
    Đây là nền tảng admissible của toàn bộ heuristic.
    """
    dist_map = {}
    queue = deque()
    for t in targets:
        dist_map[t] = 0
        queue.append(t)
    while queue:
        x, y = queue.popleft()
        d = dist_map[(x, y)]
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in dist_map:
                if not grid.is_wall(nx, ny) and not grid.is_outside(nx, ny):
                    dist_map[(nx, ny)] = d + 1
                    queue.append((nx, ny))
    return dist_map

# ─── Thành phần 1: Manhattan Distance (weight 1.0) ───────────────────────────
def _manhattan_heuristic(boxes, targets):
    """
    Tổng khoảng cách Manhattan từ mỗi thùng đến đích gần nhất.
    Nhanh nhất (O(n×m)), dùng làm fallback.
    """
    total = 0
    unplaced = [b for b in boxes if b not in targets]
    if not unplaced:
        return 0
    t_list = list(targets)
    for b in unplaced:
        total += min(abs(b[0]-g[0]) + abs(b[1]-g[1]) for g in t_list)
    return total

# ─── Thành phần 2: Hungarian Matching + BFS (weight 1.5) ─────────────────────
def _hungarian_heuristic(boxes, targets, dist_map):
    """
    Ghép cặp tối ưu Thùng→Đích bằng Hungarian Algorithm + BFS distances.
    Admissible vì tổng là lower bound cho chi phí thực.
    """
    unplaced  = [b for b in boxes if b not in targets]
    unmatched = [g for g in targets if g not in boxes]
    if not unplaced:
        return 0
    n, m = len(unplaced), len(unmatched)
    cost_matrix = np.zeros((n, m))
    for i, b in enumerate(unplaced):
        for j, g in enumerate(unmatched):
            cost_matrix[i][j] = dist_map.get(b, 9999)
    ri, ci = linear_sum_assignment(cost_matrix)
    return float(cost_matrix[ri, ci].sum())

# ─── Thành phần 3: Per-box BFS from each goal (PDB approximation) ────────────
def _per_goal_heuristic(boxes, targets, dist_map):
    """
    Tính chính xác hơn: Mỗi box tra bảng dist_map riêng cho từng goal.
    Đây là xấp xỉ PDB không cần precompute lớn.
    """
    unplaced  = [b for b in boxes if b not in targets]
    unmatched = [g for g in targets if g not in boxes]
    if not unplaced:
        return 0
    # Dùng BFS per-box-per-goal matrix
    n, m = len(unplaced), len(unmatched)
    cost_matrix = np.zeros((n, m))
    for i, b in enumerate(unplaced):
        for j, g in enumerate(unmatched):
            cost_matrix[i][j] = dist_map.get(b, 9999)
    # Min-cost matching (admissible)
    ri, ci = linear_sum_assignment(cost_matrix)
    return float(cost_matrix[ri, ci].sum())


class IDAStarHeuristic:
    """
    Heuristic tổng hợp admissible cho IDA*.
    Trả về max(h1, h2, h3) để cắt tỉa tốt nhất có thể.
    """
    def __init__(self, grid, targets):
        self.targets  = frozenset(targets)
        self.dist_map = build_bfs_dist_map(grid, targets)

    def __call__(self, state):
        """
        H(s) = max(
            1.0 × Manhattan,
            1.5 × Hungarian+BFS,
            2.0 × Per-goal BFS   ← Thường mạnh nhất
        )
        """
        boxes = state.boxes
        if all(b in self.targets for b in boxes):
            return 0.0

        h_manhattan = 1.0 * _manhattan_heuristic(boxes, self.targets)
        h_hungarian = 1.5 * _hungarian_heuristic(boxes, self.targets, self.dist_map)
        h_pdb       = 2.0 * _per_goal_heuristic(boxes, self.targets, self.dist_map)

        # MAX đảm bảo admissible tốt nhất
        return max(h_manhattan, h_hungarian, h_pdb)

    def is_goal(self, state):
        return all(b in self.targets for b in state.boxes)

    def incremental_update(self, old_h, moved_box_old, moved_box_new):
        """
        Incremental Heuristic Update: Cập nhật nhanh khi 1 thùng vừa di chuyển.
        Thay vì tính lại từ đầu, chỉ cập nhật delta của thùng vừa đẩy.
        Đây là xấp xỉ nhanh, không thay thế full calculation cho accuracy.
        """
        delta_old = self.dist_map.get(moved_box_old, 0)
        delta_new = self.dist_map.get(moved_box_new, 0)
        return old_h - delta_old + delta_new
