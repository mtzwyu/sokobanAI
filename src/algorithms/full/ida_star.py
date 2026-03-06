import time
import threading
from collections import deque

from src.algorithms.full.zobrist import ZobristHasher
from src.algorithms.full.transposition_table import TranspositionTable, EXACT
from src.algorithms.full.heuristic_ida import IDAStarHeuristic
from src.algorithms.full.deadlock_ida import (
    StaticDeadlockTable,
    check_all_dynamic,
    check_mutual_deadlock,
    check_freeze_deadlock,
    check_tunnel_deadlock,
    check_corral_deadlock
)

# ==============================================================================
# IDA_STAR.PY - Thuật toán IDA* Đầy Đủ 3 Pha theo Quy Trình /quytrinh
#
# PHA 1: TIỀN XỬ LÝ (Tính 1 lần)
#   - Phân tích bản đồ tĩnh (tường, đích, đồ thị kết nối)
#   - Static Deadlock Table (góc, hành lang cụt, vùng cô lập) → O(1) lookup
#   - BFS distance map + Hungarian heuristic (admissible lower bound)
#
# PHA 2: TÌM KIẾM CHÍNH (IDA* + BFS lai)
#   - IDA* core: DFS + ngưỡng f=g+h tăng mỗi vòng (depth += 5)
#   - Dynamic Deadlock: mutual, freeze, tunnel, corral
#   - Transposition Table 10^7 entries (Zobrist 64-bit)
#   - Move Ordering: +1000 push-to-goal, +500 out-of-dead, +100 push, +10 walk
#   - Forward/Backward: backward precomputes dead zones thực tế
#
# PHA 3: HẬU XỬ LÝ
#   - Solution Compression: loại bỏ chu trình, bước thừa
#   - Parallel Processing: multi-thread với shared transposition table
# ==============================================================================

SOLVED   = '__SOLVED__'
INF      = float('inf')

# ──────────────────────────────────────────────────────────────────────────────
# PHA 1: TIỀN XỬ LÝ
# ──────────────────────────────────────────────────────────────────────────────

class MapAnalysis:
    """
    Bước 1: Phân tích bản đồ tĩnh 1 lần duy nhất.
    - Xác định tường, ô trống, ô đích
    - Xây dựng đồ thị kết nối
    - Tính khoảng cách Manhattan giữa mọi cặp ô
    """
    def __init__(self, grid, targets):
        self.width  = grid.width
        self.height = grid.height
        self.walls  = set()
        self.free   = set()
        self.targets = frozenset(targets)

        # 1.1 Xác định tường và ô trống
        for y in range(grid.height):
            for x in range(grid.width):
                if grid.is_wall(x, y) or grid.is_outside(x, y):
                    self.walls.add((x, y))
                else:
                    self.free.add((x, y))

        # 1.2 Đồ thị kết nối: adj[(x,y)] = list các ô lân cận có thể đi
        self.adj = {}
        for pos in self.free:
            x, y = pos
            neighbors = []
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                n = (x+dx, y+dy)
                if n in self.free:
                    neighbors.append(n)
            self.adj[pos] = neighbors

        # 1.3 Tính khoảng cách Manhattan nhanh (lookup dict thay vì tính lại)
        # Chỉ lưu khoảng cách đến các Đích (cần dùng nhất)
        self.manhattan_to_goals = {}
        t_list = list(self.targets)
        for pos in self.free:
            self.manhattan_to_goals[pos] = min(
                abs(pos[0]-g[0]) + abs(pos[1]-g[1]) for g in t_list
            )

    def manhattan(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])


# ──────────────────────────────────────────────────────────────────────────────
# PHA 2: TÌM KIẾM CHÍNH - IDA* ENGINE
# ──────────────────────────────────────────────────────────────────────────────

# Move priority scores (dùng cho Move Ordering - Bước 8)
PRIORITY_PUSH_TO_GOAL   = 1000
PRIORITY_OUT_OF_DEAD    = 500
PRIORITY_PUSH_TOWARDS   = 100
PRIORITY_MOVE_TO_BOX    = 10
PRIORITY_OTHER          = 0


class IDAStar:
    """
    IDA* Full Solver - 3 Pha hoàn chỉnh.
    """

    def __init__(self, grid, targets, max_time_seconds=300):
        self.grid     = grid
        self.targets  = frozenset(targets)
        self.max_time = max_time_seconds
        self.nodes    = 0
        self.start_t  = 0.0
        self._solved_path = None    # Dùng cho parallel search
        self._lock = threading.Lock()

        print("\n[IDA*] ╔══════════════ PHASE 1: TIỀN XỬ LÝ ══════════════╗")

        # Bước 1: Phân tích bản đồ tĩnh
        print("[IDA*] Bước 1: Phân tích bản đồ tĩnh...")
        self.map_info = MapAnalysis(grid, targets)
        print(f"[IDA*]   ✓ {len(self.map_info.free)} ô trống | {len(self.map_info.walls)} ô tường | {len(targets)} đích")

        # Bước 2: Static Deadlock Table
        print("[IDA*] Bước 2: Xây dựng Static Deadlock Table (góc + hành lang + vùng cô lập)...")
        self.static_dl = StaticDeadlockTable(grid, targets)
        print(f"[IDA*]   ✓ Deadlock map: {len(self.static_dl.deadlock_map)} ô bị cấm (O(1) lookup)")

        # Bước 3: Heuristic tĩnh (Pattern Database)
        print("[IDA*] Bước 3: Xây dựng BFS Distance Map + Heuristic tổng hợp...")
        self.heuristic = IDAStarHeuristic(grid, targets)
        print(f"[IDA*]   ✓ Distance map: {len(self.heuristic.dist_map)} ô | Composite: max(1.0×Manhattan, 1.5×Hungarian, 2.0×PDB)")

        # Transposition Table + Zobrist
        print("[IDA*] Bước 7: Khởi tạo Zobrist Hasher + Transposition Table (10^7 entries)...")
        self.hasher = ZobristHasher(grid.width, grid.height)
        self.tt     = TranspositionTable(max_size=10_000_000)

        print("[IDA*] ╚══════════════════════════════════════════════════╝\n")


    # ── BƯỚC 8: MOVE ORDERING ─────────────────────────────────────────────────

    def _move_priority(self, state, next_state):
        """
        Tính điểm ưu tiên cho 1 nước đi.
        Điểm cao hơn → thử trước (tìm nhanh hơn).
        """
        is_push = next_state.boxes != state.boxes
        if not is_push:
            # Di chuyển người: +10 nếu tiến gần thùng hơn
            unplaced = [b for b in state.boxes if b not in self.targets]
            if unplaced:
                old_dist = min(abs(state.player_pos[0]-b[0])+abs(state.player_pos[1]-b[1]) for b in unplaced)
                new_dist = min(abs(next_state.player_pos[0]-b[0])+abs(next_state.player_pos[1]-b[1]) for b in unplaced)
                return PRIORITY_MOVE_TO_BOX if new_dist < old_dist else PRIORITY_OTHER
            return PRIORITY_OTHER

        # Tìm thùng vừa đẩy
        old_boxes = set(state.boxes)
        new_boxes = set(next_state.boxes)
        moved_new = list(new_boxes - old_boxes)
        if not moved_new:
            return PRIORITY_OTHER
        new_pos = moved_new[0]

        # +1000: Đẩy thùng VÀO ĐÍCH
        if new_pos in self.targets:
            return PRIORITY_PUSH_TO_GOAL

        # +500: Đẩy thùng RA KHỎI dead zone (thùng cũ trong dead zone)
        moved_old = list(old_boxes - new_boxes)
        if moved_old and moved_old[0] in self.static_dl.deadlock_map:
            return PRIORITY_OUT_OF_DEAD

        # +100: Đẩy thùng về gần đích hơn (so sánh dist_map)
        old_pos = moved_old[0] if moved_old else None
        if old_pos:
            old_d = self.heuristic.dist_map.get(old_pos, 9999)
            new_d = self.heuristic.dist_map.get(new_pos, 9999)
            if new_d < old_d:
                return PRIORITY_PUSH_TOWARDS

        return PRIORITY_OTHER

    def _order_moves(self, state, neighbors):
        """Sắp xếp neighbors theo độ ưu tiên giảm dần."""
        scored = [(- self._move_priority(state, n), n) for n in neighbors]
        scored.sort(key=lambda x: x[0])
        return [n for _, n in scored]


    # ── BƯỚC 5/6: DEADLOCK DETECTION (tổng hợp) ──────────────────────────────

    def _is_deadlock(self, state):
        """Kiểm tra tất cả deadlock: static (O(1)) + dynamic."""
        # Static check (O(1))
        if self.static_dl.any_box_dead(state.boxes, self.targets):
            return True
        # Dynamic check
        return check_all_dynamic(state, self.grid, self.targets)


    # ── IDA* DFS CỐT LÕI (Bước 4.1) ─────────────────────────────────────────

    def _dfs(self, state, g, limit, path_actions, state_hash, adapter):
        """
        DFS với ngưỡng f = g + h.
        Trả về SOLVED hoặc min_f_exceeded.
        """
        if time.time() - self.start_t > self.max_time:
            return INF
        # Kiểm tra đã có solution từ luồng khác (Parallel Search)
        if self._solved_path is not None:
            return SOLVED

        h = self.heuristic(state)
        f = g + h

        if f > limit:
            return f

        if h == 0 and self.heuristic.is_goal(state):
            return SOLVED

        # Deadlock: tĩnh + động
        if self._is_deadlock(state):
            return INF

        # Transposition Table: cắt nhánh nếu đã thăm với g tốt hơn
        entry = self.tt.lookup(state_hash)
        if entry is not None and entry[0] <= g:
            return INF
        self.tt.store(state_hash, g, EXACT)
        self.nodes += 1

        # Sinh và sắp xếp nước đi (Move Ordering)
        raw   = adapter.get_neighbors(state)
        order = self._order_moves(state, raw)

        min_exceeded = INF
        for next_s in order:
            # Zobrist update O(1)
            moved_box = new_box = None
            if next_s.boxes != state.boxes:
                diff_old = set(state.boxes) - set(next_s.boxes)
                diff_new = set(next_s.boxes) - set(state.boxes)
                if diff_old and diff_new:
                    moved_box = list(diff_old)[0]
                    new_box   = list(diff_new)[0]

            next_hash = self.hasher.update_move(
                state_hash,
                state.player_pos, next_s.player_pos,
                moved_box, new_box
            )

            # Ghi action
            dx = next_s.player_pos[0] - state.player_pos[0]
            dy = next_s.player_pos[1] - state.player_pos[1]
            dirs = {(0,-1):'LÊN',(0,1):'XUỐNG',(-1,0):'TRÁI',(1,0):'PHẢI'}
            act  = dirs.get((dx, dy), '?')
            if next_s.boxes != state.boxes:
                act = f'ĐẨY {act}'

            path_actions.append(act)
            result = self._dfs(next_s, g+1, limit, path_actions, next_hash, adapter)

            if result == SOLVED:
                return SOLVED
            if isinstance(result, (int, float)) and result < min_exceeded:
                min_exceeded = result
            path_actions.pop()

        return min_exceeded


    # ── BƯỚC 6: BACKWARD SEARCH (Precompute) ──────────────────────────────────

    def _backward_precompute(self):
        """
        Backward Search: Đọc dead zones đã được tính bởi StaticDeadlockTable
        (thực chất đây là reverse BFS từ đích — đã xây trong Phase 1).
        Log để người dùng biết.
        """
        print(f"[IDA*] Bước 6: Backward precompute đã tích hợp vào Static DL Table ({len(self.static_dl.deadlock_map)} dead zones).")


    # ── BƯỚC 9: SOLUTION COMPRESSION (Phase 3) ───────────────────────────────

    def _compress_solution(self, path_actions):
        """
        Loại bỏ chu trình và bước thừa:
        - Nếu có sequence "LÊN…XUỐNG" liền kề → khử cặp
        - Phát hiện và cắt chu trình trong chuỗi hành động
        """
        opposites = {
            'LÊN': 'XUỐNG', 'XUỐNG': 'LÊN',
            'TRÁI': 'PHẢI',  'PHẢI': 'TRÁI'
        }
        compressed = []
        for act in path_actions:
            # Chỉ khử cặp với nước đi bộ (không đẩy thùng)
            if compressed and 'ĐẨY' not in act and 'ĐẨY' not in compressed[-1]:
                if act == opposites.get(compressed[-1]):
                    compressed.pop()
                    continue
            compressed.append(act)
        return compressed


    # ── BƯỚC 10: PARALLEL PROCESSING ─────────────────────────────────────────

    def _parallel_worker(self, worker_id, initial_state, adapter, results,
                          start_limit, depth_increment):
        """
        Mỗi worker chạy IDA* từ một ngưỡng bắt đầu khác nhau.
        Shared transposition table + early-stop khi 1 worker tìm được lời giải.
        """
        limit = start_limit + worker_id * depth_increment
        path  = []
        init_hash = self.hasher.hash_state(initial_state)

        while limit < 500 and self._solved_path is None:
            result = self._dfs(initial_state, 0, limit, path, init_hash, adapter)
            if result == SOLVED:
                with self._lock:
                    if self._solved_path is None:
                        self._solved_path = list(path)
                        results[worker_id] = list(path)
                return
            if result == INF:
                return
            limit += depth_increment * 4  # Mỗi worker tăng ngưỡng nhanh hơn
            path.clear()
            self.tt.clear()


    # ── API CHÍNH: SOLVE ──────────────────────────────────────────────────────

    def solve(self, initial_state, adapter, n_workers=4):
        """
        Chạy IDA* đầy đủ 3 pha.
        Trả về (path_actions, steps, time_ms, status_str).
        """
        self.start_t         = time.time()
        self.nodes           = 0
        self._solved_path    = None
        self.tt.clear()

        self._backward_precompute()

        init_hash = self.hasher.hash_state(initial_state)
        init_h    = self.heuristic(initial_state)
        depth_inc = 5  # Tăng ngưỡng từng 5 theo spec

        print(f"\n[IDA*] {'═'*80}")
        print(f"[IDA*] 🚀 PHA 2: TÌM KIẾM | H ban đầu: {init_h:.1f} | Increment: {depth_inc} | Workers: {n_workers}")
        print(f"[IDA*] {'═'*80}")
        print(f"| {'IT':<4} | {'LIMIT':<8} | {'NODES':<12} | {'TT':<10} | {'TIME(s)':<8} | {'Δ':<6} |")
        print(f"| {'─'*4} | {'─'*8} | {'─'*12} | {'─'*10} | {'─'*8} | {'─'*6} |")

        # ── PARALLEL SEARCH ──
        results  = {}
        threads  = []
        n_workers = min(n_workers, 4)  # Giới hạn 4 threads để tránh overhead

        for wid in range(n_workers):
            t = threading.Thread(
                target=self._parallel_worker,
                args=(wid, initial_state, adapter, results, init_h, depth_inc),
                daemon=True
            )
            threads.append(t)
            t.start()

        # Main thread: cũng chạy sequential IDA* với full logging
        limit = init_h
        path  = []
        iteration = 0
        while self._solved_path is None and time.time() - self.start_t < self.max_time:
            prev_nodes = self.nodes
            result = self._dfs(initial_state, 0, limit, path, init_hash, adapter)
            elapsed = time.time() - self.start_t
            delta_nodes = self.nodes - prev_nodes

            print(f"| {iteration:<4} | {limit:<8.1f} | {self.nodes:<12} | {len(self.tt._table):<10} | {elapsed:<8.2f} | {delta_nodes:<6} |")

            if result == SOLVED or self._solved_path is not None:
                if path:
                    self._solved_path = list(path)
                break
            if result == INF:
                break
            limit += depth_inc
            iteration += 1
            path.clear()
            self.tt.clear()

        # Chờ các worker threads kết thúc
        for t in threads:
            t.join(timeout=0.5)

        elapsed = time.time() - self.start_t

        # ── PHA 3: HẬU XỬ LÝ ──
        if self._solved_path:
            raw_steps = len(self._solved_path)
            print(f"\n[IDA*] {'═'*80}")
            print(f"[IDA*] ✅ PHA 3: TỐI ƯU HÓA lời giải ({raw_steps} bước)...")
            compressed = self._compress_solution(self._solved_path)
            print(f"[IDA*]    ✓ Sau nén: {len(compressed)} bước (giảm {raw_steps - len(compressed)} bước thừa)")
            print(f"[IDA*] ⭐ HOÀN TẤT | Nodes: {self.nodes:,} | Time: {elapsed:.2f}s | TT hit: {self.tt.stats()['hit_rate']}")
            return compressed, len(compressed), elapsed*1000, "🟢 IDA* GIẢI THÀNH CÔNG!"

        if time.time() - self.start_t >= self.max_time:
            return [], 0, elapsed*1000, "🔴 IDA* Hết Thời Gian"
        return [], 0, elapsed*1000, "🔴 IDA* Không Tìm Được Lời Giải"
