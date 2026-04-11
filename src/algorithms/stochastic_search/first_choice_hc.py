import random

def first_choice_hill_climbing(initial_state, get_neighbors, get_heuristic, max_iterations=1000):
    """
    Thuật toán Leo đồi Lựa chọn Đầu tiên (First-Choice HC).
    - Xáo trộn NGẪU NHIÊN danh sách hàng xóm.
    - Lấy NGAY hàng xóm ĐẦU TIÊN tốt hơn (next_h < current_h).
    - Dừng khi không có hàng xóm nào tốt hơn (Local Minima — đúng theo định nghĩa).
    - Truyền prev_boxes để heuristic tự tính push bonus.
    """
    current_state = initial_state
    current_h = get_heuristic(current_state)
    path = []

    for _ in range(max_iterations):
        if current_h == 0:
            break

        neighbors = get_neighbors(current_state)
        random.shuffle(neighbors)

        found_better = False
        for action, next_state in neighbors:
            next_h = get_heuristic(next_state, current_state.boxes)
            if next_h < current_h:
                current_state = next_state
                current_h = get_heuristic(current_state)
                path.append(action)
                found_better = True
                break

        if not found_better:
            break  # Local Minima — đúng theo định nghĩa First Choice HC

    return current_state, path
