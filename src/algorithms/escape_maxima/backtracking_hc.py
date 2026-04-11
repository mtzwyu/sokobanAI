def backtracking_hill_climbing(initial_state, get_neighbors, get_heuristic, max_iterations=1000):
    """
    Thuật toán Leo đồi có quay lui (Backtracking Hill Climbing).
    - Duy trì danh sách lịch sử các con đường đã đi.
    - Khi bị kẹt ở cực đại cục bộ, thuật toán sẽ 'QUAY LUI' (Backtrack) về các trạng thái trước đó.
    - Tại điểm đã quay lui, tiếp tục khám phá các hướng đi chưa từng thử nghiệm.
    """
    visited_states = set()
    
    # Biến stack lưu trữ đường đi: mỗi phần tử gồm (trạng_thái, điểm_số, danh_sách_các_nhánh_chưa_xét, hành_động_để_tới_đây)
    # Lần đầu tiên chưa có hành động trước đó nên để None
    stack = []
    
    # Khởi tạo trạng thái ban đầu
    current_h = get_heuristic(initial_state)
    start_neighbors = get_neighbors(initial_state)
    # Sắp xếp các hàng xóm từ tốt nhất đến tệ nhất để ưu tiên duyệt
    start_neighbors.sort(key=lambda x: get_heuristic(x[1]))
    stack.append((initial_state, current_h, start_neighbors, None))
    visited_states.add(initial_state)
    
    # Lưu lại trạng thái tốt nhất tổng thể từng thấy
    best_state_overall = initial_state
    best_h_overall = current_h
    best_path_overall = []
    
    current_path = [] # Cây đường đi hiện tại

    iterations = 0
    while stack and iterations < max_iterations:
        iterations += 1
        
        # Xem xét trạng thái đỉnh của ngăn xếp
        curr_state, curr_h, unexplored_branches, action_to_here = stack[-1]
        
        # Nếu nhánh này hoàn toàn trống (hết đường đi) -> Xóa khỏi ngăn xếp (Quay lui)
        if not unexplored_branches:
            stack.pop()
            if current_path:
                current_path.pop() # Lùi lại 1 bước trong quỹ đạo
            continue
            
        # Lấy nhánh tiếp theo (nhánh tiềm năng nhất do ta đã sort phía trên)
        next_action, next_state = unexplored_branches.pop(0) # Rút nhánh đầu tiên khỏi list
        
        # Nếu đỉnh này bị chặn vì đã từng dẫm chân lên (chống lặp vô hạn)
        if next_state in visited_states:
            continue
            
        next_h = get_heuristic(next_state)
        
        # Bắt đầu duyệt sâu xuống nhánh dưới này
        visited_states.add(next_state)
        new_neighbors = get_neighbors(next_state)
        new_neighbors.sort(key=lambda x: get_heuristic(x[1]))
        
        stack.append((next_state, next_h, new_neighbors, next_action))
        current_path.append(next_action)
        
        # Cập nhật kết quả tốt nhất từng thấy (Record holder)
        if next_h < best_h_overall:
            best_h_overall = next_h
            best_state_overall = next_state
            best_path_overall = list(current_path) # Sao chép quỹ đạo

        # Nếu tìm thấy đích tuyệt đối (H=0), ta có thể dừng luôn
        if next_h == 0:
            break
            
    return best_state_overall, best_path_overall
