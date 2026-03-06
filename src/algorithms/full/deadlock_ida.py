from collections import deque

# ==============================================================================
# DEADLOCK_IDA.PY - Hệ thống phát hiện Deadlock toàn diện cho IDA*
# ==============================================================================
# PHASE 1 - TĨNH (Tính 1 lần, dùng mãi):
#   1.1 Góc tường chết (Corner Deadlock)
#   1.2 Hành lang cụt (Dead-end Corridors)
#   1.3 Vùng bị cô lập (Isolated Zones)
#   → Lưu vào deadlock_map[] → Kiểm tra O(1)
#
# PHASE 2 - ĐỘNG (Kiểm tra mỗi trạng thái):
#   2.1 Hai thùng tự kẹt nhau (Mutual Deadlock)
#   2.2 Freeze Deadlock (bị bao vây 3 mặt)
#   2.3 Tunnel Deadlock (hành lang bị chặn)
#   2.4 Corral Deadlock (vùng kín)
# ==============================================================================


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1: DEADLOCK TĨNH - Tiền xử lý
# ══════════════════════════════════════════════════════════════════════════════

def _is_blocked(x, y, grid):
    """True nếu ô (x,y) là tường hoặc ngoài biên."""
    return grid.is_wall(x, y) or grid.is_outside(x, y)

def _build_corner_deadlock(grid, targets):
    """
    1.1 Góc tường chết: Ô có ≥2 hướng vuông góc bị chặn → không thể đẩy thùng ra.
    Đây là dạng deadlock tuyệt đối: thùng vào là chết.
    """
    corners = set()
    for y in range(grid.height):
        for x in range(grid.width):
            if (x, y) in targets or _is_blocked(x, y, grid):
                continue
            up    = _is_blocked(x, y-1, grid)
            down  = _is_blocked(x, y+1, grid)
            left  = _is_blocked(x-1, y, grid)
            right = _is_blocked(x+1, y, grid)
            if (up and left) or (up and right) or (down and left) or (down and right):
                corners.add((x, y))
    return corners

def _build_dead_end_corridors(grid, targets, corner_deadlocks):
    """
    1.2 Hành lang cụt: Lan rộng từ các góc chết theo BFS.
    Nếu 1 ô hành lang có 2 cạnh bị chặn VÀ chỉ thông về 1 hướng dẫn đến góc chết
    → Ô đó cũng là deadlock.
    """
    dead_corridors = set(corner_deadlocks)
    changed = True
    while changed:
        changed = False
        for y in range(grid.height):
            for x in range(grid.width):
                pos = (x, y)
                if pos in dead_corridors or pos in targets or _is_blocked(x, y, grid):
                    continue
                # Đếm số hướng thoát được (không phải tường, không phải dead corridor)
                exits = []
                for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = x+dx, y+dy
                    if not _is_blocked(nx, ny, grid) and (nx, ny) not in dead_corridors:
                        exits.append((nx, ny))
                # Hướng thoát theo trục ngang + dọc
                horiz_blocked = _is_blocked(x-1, y, grid) or (x-1,y) in dead_corridors
                horiz_blocked = horiz_blocked and (_is_blocked(x+1, y, grid) or (x+1,y) in dead_corridors)
                vert_blocked  = _is_blocked(x, y-1, grid) or (x,y-1) in dead_corridors
                vert_blocked  = vert_blocked and (_is_blocked(x, y+1, grid) or (x,y+1) in dead_corridors)
                if horiz_blocked or vert_blocked:
                    dead_corridors.add(pos)
                    changed = True
    return dead_corridors

def _build_isolated_zones(grid, targets):
    """
    1.3 Vùng bị cô lập: Dùng BFS ngược từ các đích.
    Nếu 1 ô không thể đến được bằng cách kéo thùng ngược từ đích
    → Ô đó là dead zone tuyệt đối.
    """
    reachable = set(targets)
    queue = deque(list(targets))
    while queue:
        bx, by = queue.popleft()
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            prev_bx, prev_by = bx - dx, by - dy
            player_x, player_y = bx + dx, by + dy
            if (prev_bx, prev_by) in reachable:
                continue
            if _is_blocked(prev_bx, prev_by, grid) or _is_blocked(player_x, player_y, grid):
                continue
            reachable.add((prev_bx, prev_by))
            queue.append((prev_bx, prev_by))

    isolated = set()
    for y in range(grid.height):
        for x in range(grid.width):
            if not _is_blocked(x, y, grid) and (x, y) not in reachable:
                isolated.add((x, y))
    return isolated


class StaticDeadlockTable:
    """
    Bảng deadlock tĩnh tổng hợp — O(1) per lookup.
    Tạo 1 lần khi bắt đầu màn, dùng suốt quá trình tìm kiếm.
    """
    def __init__(self, grid, targets):
        corners    = _build_corner_deadlock(grid, targets)
        corridors  = _build_dead_end_corridors(grid, targets, corners)
        isolated   = _build_isolated_zones(grid, targets)

        # Union tất cả các loại deadlock tĩnh thành 1 set duy nhất
        self.deadlock_map = corridors | isolated
        # Xóa các đích (đích không bao giờ là deadlock)
        self.deadlock_map -= set(targets)

    def is_dead(self, pos):
        """True nếu vị trí này là dead zone tĩnh → Cắt ngay."""
        return pos in self.deadlock_map

    def any_box_dead(self, boxes, targets):
        """True nếu BẤT KỲ thùng nào (chưa ở đích) nằm trong dead zone."""
        for b in boxes:
            if b not in targets and b in self.deadlock_map:
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2: DEADLOCK ĐỘNG - Kiểm tra runtime
# ══════════════════════════════════════════════════════════════════════════════

def check_mutual_deadlock(boxes, targets, grid):
    """
    2.1 Mutual (Pair) Deadlock: 2 thùng kề nhau, một thùng kề tường, cả 2 chưa ở đích.
    Trong tình huống này, 2 thùng sẽ chặn nhau vĩnh viễn.
    """
    box_set = set(boxes)
    for b in boxes:
        if b in targets:
            continue
        x, y = b
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            neighbor = (x+dx, y+dy)
            if neighbor in box_set and neighbor not in targets:
                # 2 thùng kề nhau, kiểm tra xem có tường chặn vuông góc không
                if dx == 0:  # Hai thùng theo cột → cần tường theo chiều ngang
                    if (_is_blocked(x-1, y, grid) and _is_blocked(x-1, y+dy, grid)) or \
                       (_is_blocked(x+1, y, grid) and _is_blocked(x+1, y+dy, grid)):
                        return True
                else:  # Hai thùng theo hàng → cần tường theo chiều dọc
                    if (_is_blocked(x, y-1, grid) and _is_blocked(x+dx, y-1, grid)) or \
                       (_is_blocked(x, y+1, grid) and _is_blocked(x+dx, y+1, grid)):
                        return True
    return False

def check_freeze_deadlock(box, boxes, targets, grid):
    """
    2.2 Freeze Deadlock: Thùng bị bao vây bởi tường/thùng khác ở ≥3 mặt.
    Thùng không thể di chuyển vĩnh viễn.
    """
    if box in targets:
        return False
    x, y = box
    box_set = set(boxes)
    blocked_sides = 0
    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = x+dx, y+dy
        if _is_blocked(nx, ny, grid) or (nx, ny) in box_set:
            blocked_sides += 1
    return blocked_sides >= 3

def check_tunnel_deadlock(box, push_dir, boxes, targets, grid):
    """
    2.3 Tunnel Deadlock: Thùng trong hành lang hẹp (rộng 1 ô), đầu hàng bị chặn thùng khác.
    Nếu đẩy vào hành lang mà cuối hành lang là thùng hoặc tường chết → deadlock.
    """
    if box in targets:
        return False
    dx, dy = push_dir
    x, y = box
    box_set = set(boxes)
    # Kiểm tra xem hiện tại có đang trong hành lang theo chiều đẩy không
    perp = [(-dy, dx), (dy, -dx)]  # 2 hướng vuông góc
    in_tunnel = all(_is_blocked(x + pdx, y + pdy, grid) for pdx, pdy in perp)
    if not in_tunnel:
        return False
    # Dò đến cuối hành lang
    cx, cy = x + dx, y + dy
    while not _is_blocked(cx, cy, grid):
        if (cx, cy) in box_set and (cx, cy) not in targets:
            return True  # Cuối hành lang là thùng không ở đích → deadlock
        cx += dx
        cy += dy
    return False

def check_corral_deadlock(state, grid, targets):
    """
    2.4 Corral Deadlock: Người chơi bị vây bởi thùng tạo "hàng rào".
    Nếu không thể đẩy bất kỳ thùng nào trong hàng rào → deadlock.
    """
    # BFS từ player tìm vùng tiếp cận
    player_area = set()
    queue = deque([state.player_pos])
    player_area.add(state.player_pos)
    box_set = set(state.boxes)
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in player_area and (nx, ny) not in box_set:
                if not _is_blocked(nx, ny, grid):
                    player_area.add((nx, ny))
                    queue.append((nx, ny))

    # Tìm các thùng tạo hàng rào (tiếp giáp vùng player)
    corral_boxes = set()
    for px, py in player_area:
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nb = (px+dx, py+dy)
            if nb in box_set:
                corral_boxes.add(nb)

    if not corral_boxes:
        return False

    # Kiểm tra xem có thể đẩy ít nhất 1 thùng trong corral không
    for bx, by in corral_boxes:
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            push_from = (bx-dx, by-dy)  # Người đứng ở đây để đẩy
            push_to   = (bx+dx, by+dy)  # Thùng đi đến đây
            if push_from in player_area:
                if not _is_blocked(push_to[0], push_to[1], grid) and push_to not in box_set:
                    return False  # Đẩy được ít nhất 1 thùng → không deadlock
    return True  # Không đẩy được gì → Deadlock!


def check_all_dynamic(state, grid, targets):
    """
    Hàm tổng hợp kiểm tra TẤT CẢ deadlock động.
    Trả về True nếu gặp bất kỳ loại deadlock nào.
    """
    boxes = state.boxes
    if check_mutual_deadlock(boxes, targets, grid):
        return True
    for b in boxes:
        if check_freeze_deadlock(b, boxes, targets, grid):
            return True
    if check_corral_deadlock(state, grid, targets):
        return True
    return False
