import random

def stochastic_hill_climbing(initial_state, get_neighbors, get_heuristic, max_iterations=1000):
    """
    Thuật toán Leo đồi ngẫu nhiên (Stochastic Hill Climbing).
    - Lọc hàng xóm TỐT HƠN, chọn NGẪU NHIÊN 1 trong số đó.
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
        better_neighbors = []

        for action, next_state in neighbors:
            next_h = get_heuristic(next_state, current_state.boxes)
            if next_h < current_h:
                better_neighbors.append((action, next_state, next_h))

        if not better_neighbors:
            break  # Local Minima — đúng theo định nghĩa Stochastic HC

        chosen_action, chosen_state, chosen_h = random.choice(better_neighbors)
        current_state = chosen_state
        current_h = get_heuristic(current_state)
        path.append(chosen_action)

    return current_state, path
