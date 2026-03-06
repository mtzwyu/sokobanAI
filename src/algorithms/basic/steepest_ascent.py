import time

# ==============================================================================
# AI SOKOBAN: STEEPEST-ASCENT HILL CLIMBING (CÓ DEADLOCK & HEURISTIC 3 YẾU TỐ)
# ==============================================================================

def steepest_ascent_hill_climbing(initial_state, get_neighbors_func, get_heuristic_func, max_steps=10000):
    """
    Thuật toán AI Tìm kiếm leo đồi dốc đứng (Steepest-Ascent).
    Khác với Simple Hill (chọn bừa ngã rẽ đầu tiên tốt hơn), thuật toán này duyệt qua
    TẤT CẢ các nhánh đi có thể, và chọn ra nhánh TỐT NHẤT (Điểm Heuristic thấp nhất).
    
    Args:
        initial_state (State): Trạng thái đầu.
        get_neighbors_func: Hàm sinh nhánh đi.
        get_heuristic_func: Hàm đánh giá (Deadlock = Vô Cực).
        
    Returns:
        tuple: (final_state, best_score, steps, time_taken_ms, status_message)
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box, cur_player = get_heuristic_func(current_state)
    steps = 0
    visited = {current_state}
    path_actions = []
    
    status = "🔴 Thất Bại (Kẹt Đỉnh Đồi / Quá Limit)"
    
    # In table header
    print("\n" + "="*88)
    print(f"| {'STEP':<5} | {'HEURISTIC SCORE':<22} | {'HÀNH ĐỘNG':<25} | {'TRẠNG THÁI':<20} |")
    print("="*88)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<22} | {'Khởi tạo ban đầu':<25} | {'Đang quét mọi ngõ':<20} |")
    
    while steps < max_steps:
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG!"
            break
            
        neighbors = get_neighbors_func(current_state)
        
        best_neighbor = None
        best_score = current_score # Điểm kỷ lục phải tốt hơn STRICTLY (<) điểm cũ.
        best_box = float('inf')
        best_player = float('inf')
        
        # 3. Steepest-Ascent: Quét TOÀN BỘ nhánh xung quanh để tìm Vị Vua Tốt Nhất
        for neighbor in neighbors:
            if neighbor not in visited:
                score, box_w, player_w = get_heuristic_func(neighbor)
                
                # Hàm Heuristic đã trừ khử sẵn các nước đi "Deadlock" bằng cách trả về vô cực (inf)
                if score < best_score:
                    best_score = score
                    best_box = box_w
                    best_player = player_w
                    best_neighbor = neighbor
                    
        # 4. Kiểm tra có tìm được đường tốt hơn không
        if best_neighbor is not None:
            # Suy luận lại hướng đi từ thay đổi tọa độ để In Log
            dx = best_neighbor.player_pos[0] - current_state.player_pos[0]
            dy = best_neighbor.player_pos[1] - current_state.player_pos[1]
            action_str = "Không rõ"
            if dx == 0 and dy == -1: action_str = "Di chuyển LÊN"
            elif dx == 0 and dy == 1: action_str = "Di chuyển XUỐNG"
            elif dx == -1 and dy == 0: action_str = "Di chuyển TRÁI"
            elif dx == 1 and dy == 0: action_str = "Di chuyển PHẢI"
            
            if best_neighbor.boxes != current_state.boxes:
                action_str = action_str.replace("Di chuyển", "ĐẨY HỘP")
                
            current_state = best_neighbor
            current_score = best_score
            cur_box = best_box
            cur_player = best_player
            visited.add(best_neighbor)
            path_actions.append(action_str)
            
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
            print(f"| {steps+1:<5} | {score_str:<22} | {action_str:<25} | {'Chọn đường tốt nhất':<20} |")
            
        else:
            # Thuật toán chính thức bế tắc tại đây (Local Optimum).
            status = "🔴 Kẹt Ở Ngõ Cụt"
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
            print(f"| {'END':<5} | {score_str:<22} | {'KẸT LỐI ĐI':<25} | {status:<20} |")
            break
            
        steps += 1
        
    if status == "🟢 GIẢI THÀNH CÔNG!":
         score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
         print(f"| {'END':<5} | {score_str:<22} | {'CHẠM ĐÍCH':<25} | {status:<20} |")
        
    print("="*88)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return current_state, path_actions, current_score, steps, time_taken_ms, status


# #Tuyệt vời! Tôi đã lập trình xong thuật toán Steepest-Ascent Hill Climbing theo đúng yêu cầu sát sườn của bạn và lưu vào file riêng src/algorithms/steepest_ascent.py.

# Điểm khác biệt trí mạng so với Simple Hill Climbing lúc nãy là:

# Nó không còn kiểu "tham ăn" nhảy ngay vào nhánh đầu tiên có điểm tốt hơn nữa.
# Ở mỗi vòng lặp STEP, nó sẽ mở rộng vòng tay khảo sát TẤT CẢ các ngã rẽ (Neighbors) có thể đi được.
# Sau đó, nó sẽ chọn ra Chính xác 1 nhánh có Tình trạng TỐT NHẤT (Tức là khoảng cách Heuristic 3 yếu tố tới đích phải là nhỏ nhất) để bước đi.
# Tôi đã thay lệnh gán cho phím Space trong game.py thành Steepest-Ascent. Bạn thử bật lại cửa sổ game (tôi vừa start ở cửa sổ Terminal bên dưới) và bấm Space để kiểm tra bảng Log Terminal nhé! Bạn sẽ soi thấy chữ Chọn nhánh tốt nhất trên bảng phân tích AI đó ạ!