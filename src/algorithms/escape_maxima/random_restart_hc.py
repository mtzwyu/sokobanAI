def random_restart_hill_climbing(initial_state, get_neighbors, get_heuristic,
                                  generate_random_initial_state_fn=None,
                                  max_restarts=5, max_steps_per_restart=500):
    """
    Thuật toán Khởi động lại Ngẫu nhiên (Random Restart Hill Climbing).
    - Chạy Simple HC (first better) từ điểm xuất phát.
    - Khi kẹt tại local minima → restart từ vị trí ngẫu nhiên mới.
    - Trả về trạng thái tốt nhất trên tất cả các lần restart.
    - Truyền prev_boxes để heuristic tự tính push bonus.
    """
    best_overall_state = initial_state
    best_overall_h = get_heuristic(initial_state)
    best_overall_path = []

    current_start_state = initial_state

    for restart_idx in range(max_restarts + 1):
        current_state = current_start_state
        current_h = get_heuristic(current_state)
        current_path = []

        # Chạy Simple HC (first better) từ điểm xuất phát hiện tại
        for _ in range(max_steps_per_restart):
            if current_h == 0:
                break

            neighbors = get_neighbors(current_state)
            if not neighbors:
                break

            found_better = False
            for action, next_state in neighbors:
                next_h = get_heuristic(next_state, current_state.boxes)
                if next_h < current_h:
                    current_state = next_state
                    current_h = get_heuristic(current_state)
                    current_path.append(action)
                    found_better = True
                    break

            if not found_better:
                break  # Kẹt local minima → sẽ restart

        # Cập nhật kết quả tốt nhất toàn cục
        if current_h < best_overall_h:
            best_overall_h = current_h
            best_overall_state = current_state
            best_overall_path = current_path

        if best_overall_h == 0:
            break

        # Restart: tạo điểm xuất phát mới
        if generate_random_initial_state_fn is not None and restart_idx < max_restarts:
            new_start = generate_random_initial_state_fn()
            if new_start is not None and hasattr(new_start, 'boxes'):
                current_start_state = new_start
            else:
                break  # Không tạo được state mới hợp lệ → dừng

    return best_overall_state, best_overall_path
