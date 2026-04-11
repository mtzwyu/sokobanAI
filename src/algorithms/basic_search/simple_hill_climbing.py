def simple_hill_climbing(initial_state, get_neighbors, get_heuristic, max_iterations=1000):
    """
    Thuật toán Leo đồi đơn giản (Simple Hill Climbing).
    - Đánh giá tuần tự từng trạng thái kề.
    - Ngay khi tìm thấy hàng xóm tốt hơn (next_h < current_h), di chuyển ngay.
    - Truyền prev_boxes để heuristic tự tính push bonus và Euclidean ưu tiên.
    - Dừng khi không còn hàng xóm nào tốt hơn (Local Minima).
    """
    current_state = initial_state
    current_h = get_heuristic(current_state)
    path = []

    for _ in range(max_iterations):
        if current_h == 0:
            break

        neighbors = get_neighbors(current_state)
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
            break

    return current_state, path
