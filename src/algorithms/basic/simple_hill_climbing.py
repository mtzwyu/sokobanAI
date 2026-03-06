import time

# ==============================================================================
# AI SOKOBAN: SIMPLE HILL CLIMBING (CÓ DEADLOCK & HEURISTIC 3 YẾU TỐ)
# ==============================================================================

def simple_hill_climbing(initial_state, get_neighbors_func, get_heuristic_func, max_steps=10000):
    """
    Thuật toán AI Tìm kiếm leo đồi cơ bản.
    Luôn đi theo hướng có Heuristic Tốt Hơn gần nhất.
    
    Args:
        initial_state (State): OOP Tuple (player_pos, boxes) của game.
        get_neighbors_func (Callable): Hàm sinh các nhánh trạng thái đi được.
        get_heuristic_func (Callable): Hàm đánh giá điểm h_score từ Heuristic.py.
        max_steps (int): Giới hạn vòng lặp để tránh Game bị treo do mải mê đi lùi.
        
    Returns:
        tuple: (final_state, best_score, steps, time_taken_ms, status_message)
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box_w, cur_player_w = get_heuristic_func(current_state)
    steps = 0
    visited = {current_state} # Lưu vết tránh việc Player đi qua đi lại 2 ô (Lặp vòng)
    path_actions = []
    
    status = "🔴 Thất Bại (Kẹt Đỉnh Đồi / Quá Limit)"
    
    # In table header
    print("\n" + "="*88)
    print(f"| {'STEP':<5} | {'HEURISTIC SCORE':<22} | {'HÀNH ĐỘNG':<25} | {'TRẠNG THÁI':<20} |")
    print("="*88)
    score_str = f"{current_score:.1f} ({cur_box_w:.1f}+{cur_player_w:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<22} | {'Khởi tạo ban đầu':<25} | {'Đang xử lý...':<20} |")
    
    while steps < max_steps:
        # 1. Nếu điểm Heuristic chạm mốc 0 => Toàn bộ thùng đã ghép đôi trúng đích
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG!"
            break
            
        # 2. Sinh các ngã rẽ có thể đi hoặc đẩy thùng (Bao gồm logic không đẩy vào Tường)
        neighbors = get_neighbors_func(current_state)
        
        found_better_neighbor = False
        
        # 3. Simple Hill Climbing: Chọn NGAY LẬP TỨC ứng viên đầu tiên tốt hơn hiện tại
        for neighbor in neighbors:
            if neighbor not in visited:
                score, box_w, player_w = get_heuristic_func(neighbor)
                
                # Hàm Heuristic đã trừ khử sẵn các nước đi "Deadlock" bằng cách trả về vô cực (inf)
                # Cho nên if score < current_score sẽ loại bỏ luôn cả các Hướng đi dẫn đến Tình thế Kẹt Hộp
                if score < current_score:
                    # Suy luận lại hướng đi từ thay đổi tọa độ
                    dx = neighbor.player_pos[0] - current_state.player_pos[0]
                    dy = neighbor.player_pos[1] - current_state.player_pos[1]
                    action_str = "Không rõ"
                    if dx == 0 and dy == -1: action_str = "Di chuyển LÊN"
                    elif dx == 0 and dy == 1: action_str = "Di chuyển XUỐNG"
                    elif dx == -1 and dy == 0: action_str = "Di chuyển TRÁI"
                    elif dx == 1 and dy == 0: action_str = "Di chuyển PHẢI"
                    
                    if neighbor.boxes != current_state.boxes:
                        action_str = action_str.replace("Di chuyển", "ĐẨY HỘP")
                        
                    current_state = neighbor
                    current_score = score
                    cur_box_w = box_w
                    cur_player_w = player_w
                    visited.add(neighbor)
                    path_actions.append(action_str)
                    found_better_neighbor = True
                    
                    score_str = f"{current_score:.1f} ({cur_box_w:.1f}+{cur_player_w:.1f})"
                    print(f"| {steps+1:<5} | {score_str:<22} | {action_str:<25} | {'Tìm thấy đường tốt':<20} |")
                    break # Tham lam - Cắn ngay miếng ngon đầu tiên
                    
        # 4. Nếu toàn bộ xung quanh đều Tồi Tệ Hơn (Score cao hơn) hoặc bị Khóa (Deadlock Vô Cực)
        # Thuật toán chính thức bế tắc tại đây (Local Optimum).
        if not found_better_neighbor:
            status = "🔴 Kẹt Ở Ngõ Cụt"
            score_str = f"{current_score:.1f} ({cur_box_w:.1f}+{cur_player_w:.1f})"
            print(f"| {'END':<5} | {score_str:<22} | {'KẸT LỐI ĐI':<25} | {status:<20} |")
            break
            
        steps += 1
        
    if status == "🟢 GIẢI THÀNH CÔNG!":
         score_str = f"{current_score:.1f} ({cur_box_w:.1f}+{cur_player_w:.1f})"
         print(f"| {'END':<5} | {score_str:<22} | {'CHẠM ĐÍCH':<25} | {status:<20} |")
        
    print("="*88)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return current_state, path_actions, current_score, steps, time_taken_ms, status
