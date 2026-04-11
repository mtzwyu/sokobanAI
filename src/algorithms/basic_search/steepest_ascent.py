def steepest_ascent_hill_climbing(initial_state, get_neighbors, get_heuristic, max_iterations=1000):
    """
    Thuật toán Leo đồi dốc đứng (Steepest Ascent Hill Climbing).
    - Đánh giá TẤT CẢ hàng xóm, chọn hàng xóm TỐT NHẤT (nhỏ nhất H).
    - Di chuyển nếu và CHỈ NẾU hàng xóm tốt nhất STRICTLY < current_h.
    - Dừng ngay khi không còn hàng xóm nào tốt hơn → đây là Local Minima.
    - KHÔNG có sideways moves — giữ nguyên tính chất Steepest Ascent thuần túy.
    - Truyền prev_boxes để heuristic tính push bonus.
    """
    current_state = initial_state
    current_h = get_heuristic(current_state)
    path = []

    for _ in range(max_iterations):
        if current_h == 0:
            break

        neighbors = get_neighbors(current_state)
        if not neighbors:
            break

        best_next_state = None
        best_action = None
        best_h = float('inf')

        # Steepest: xét TẤT CẢ hàng xóm, chọn hàng xóm tốt nhất
        for action, next_state in neighbors:
            next_h = get_heuristic(next_state, current_state.boxes)
            if next_h < best_h:
                best_h = next_h
                best_next_state = next_state
                best_action = action

        if best_h < current_h:
            # Cải thiện → đi tiếp
            current_state = best_next_state
            current_h = get_heuristic(current_state)
            path.append(best_action)
        else:
            # Local Minima — đúng theo định nghĩa Steepest Ascent, dừng lại
            break

    return current_state, path
