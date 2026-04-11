import random

def jumping_hill_climbing(initial_state, get_neighbors, get_heuristic,
                          generate_random_state_fn=None, max_iterations=1000):
    """
    Thuật toán Leo đồi với bước nhảy (Jumping Hill Climbing).
    - Hoạt động như Steepest Ascent: đánh giá TẤT CẢ hàng xóm, chọn tốt nhất.
    - Khi kẹt Local Minima → thực hiện "CÚ NHẢY" ngẫu nhiên thoát ra.
    - Truyền prev_boxes để heuristic tính push bonus.
    - Bỏ qua trạng thái nhảy nếu H=inf (deadlock) — thử lại tối đa 3 lần.
    """
    if generate_random_state_fn is None:
        return initial_state, []

    current_state = initial_state
    current_h = get_heuristic(current_state)
    path = []

    MAX_JUMP_RETRIES = 3   # Số lần thử nhảy lại nếu gặp deadlock

    for _ in range(max_iterations):
        if current_h == 0:
            break

        neighbors = get_neighbors(current_state)
        if not neighbors:
            break

        best_next_state = None
        best_action = None
        best_h = float('inf')

        # Steepest Ascent: chọn hàng xóm TỐT NHẤT (truyền prev_boxes)
        for action, next_state in neighbors:
            next_h = get_heuristic(next_state, current_state.boxes)
            if next_h < best_h:
                best_h = next_h
                best_next_state = next_state
                best_action = action

        if best_h < current_h:
            # Cải thiện → đi tiếp (Steepest style)
            current_state = best_next_state
            current_h = get_heuristic(current_state)   # reset không prev_boxes
            path.append(best_action)
        else:
            # KẸT Local Minima → Kích hoạt CÚ NHẢY
            jumped = False
            for _ in range(MAX_JUMP_RETRIES):
                jumped_state, jump_actions = generate_random_state_fn(current_state)
                if jumped_state is None:
                    break
                jumped_h = get_heuristic(jumped_state)
                if jumped_h == float('inf'):
                    # Đã nhảy vào deadlock → thử lại
                    continue
                # Nhảy thành công
                current_state = jumped_state
                current_h = jumped_h
                path.extend(jump_actions)
                jumped = True
                break

            if not jumped:
                # Không tìm được điểm nhảy hợp lệ → dừng
                break

    return current_state, path
