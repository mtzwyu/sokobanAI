import time

# ==============================================================================
# AI SOKOBAN: GRADIENT DESCENT (ĐỔ ĐÈO / XUỐNG DỐC NHANH NHẤT)
# ==============================================================================

def gradient_descent(initial_state, get_neighbors_func, get_heuristic_func, max_steps=1000):
    """
    Thuật toán AI Gradient Descent (Vi phân Xuống dốc).
    Trong không gian rời rạc như Grid của Sokoban, Đạo hàm (Gradient) tại một bước
    chính là giá trị Delta (Sự chênh lệch) giữa Trạng thái Kế tiếp và Hiện tại.
    Công thức Gradient: ∇ = H(Next) - H(Current)
    Luật: AI luôn bị "Lực hút Trái Đất" kéo về hướng có Gradient Âm mạnh nhất (Độ dốc sâu nhất).
    Nếu tất cả mọi hướng đều có ∇ >= 0 (Đường Bằng hoặc Đi Lên), xe hết đà, dừng ở Local Minimum.
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box, cur_player = get_heuristic_func(current_state)
    
    steps = 0
    status = "🔴 Thất Bại (Mắc kẹt ở Local Minimum)"
    
    # Kỷ lục Đỉnh cao
    best_state = current_state
    best_score = current_score
    best_box = cur_box
    best_player = cur_player
    best_path_actions = []
    current_path_actions = []
    
    # Không cần Visited cho Gradient Descent thuần túy, 
    # vì nguyên lý Đổ Đèo (strictly negative gradient) cấm nó quay lên dốc.
    
    print("\n" + "="*105)
    print(f"| {'STEP':<5} | {'HEURISTIC TỔNG HIỆN TẠI':<23} | {'HÀNH ĐỘNG':<25} | {'ĐỘ DỐC (GRADIENT ∇)':<20} |")
    print("="*105)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<23} | {'Khởi tạo Đỉnh dốc':<25} | {'Bắt đầu Đổ Đèo':<20} |")
    
    while steps < max_steps:
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Trôi tuột thẳng Đích)!"
            break
            
        neighbors = get_neighbors_func(current_state)
        
        steepest_neighbor = None
        steepest_gradient = 0.0 # ∇ <= 0 mới có lực hút. 0 là bằng phẳng.
        steepest_box = 0.0
        steepest_player = 0.0
        steepest_score = float('inf')
        
        # Đoạt tất cả các độ dốc xung quanh
        for neighbor in neighbors:
            n_score, n_b, n_p = get_heuristic_func(neighbor)
            
            # Hàm trừ khử Deadlock bằng điểm vô cực (inf)
            if n_score == float('inf'):
                continue
                
            # Đạo hàm ∇ = f(x+1) - f(x)
            gradient = n_score - current_score
            
            # Chọn con dốc ÂM và SÂU NHẤT (Ví dụ: -5 dốc hơn -2)
            if gradient < steepest_gradient:
                steepest_gradient = gradient
                steepest_neighbor = neighbor
                steepest_score = n_score
                steepest_box = n_b
                steepest_player = n_p
                
        # Phanh xe chốt hạ
        if steepest_neighbor is not None:
            # So sánh xem Mình đang Tiết hay Lùi (In Log)
            dx = steepest_neighbor.player_pos[0] - current_state.player_pos[0]
            dy = steepest_neighbor.player_pos[1] - current_state.player_pos[1]
            action_str = "Không rõ"
            if dx == 0 and dy == -1: action_str = "Lao LÊN"
            elif dx == 0 and dy == 1: action_str = "Trôi XUỐNG"
            elif dx == -1 and dy == 0: action_str = "Trượt TRÁI"
            elif dx == 1 and dy == 0: action_str = "Đổ PHẢI"
            
            if steepest_neighbor.boxes != current_state.boxes:
                action_str = action_str.replace("Lao", "TỤT HỘP").replace("Trôi", "TỤT HỘP").replace("Trượt", "TỤT HỘP").replace("Đổ", "TỤT HỘP")
                
            current_state = steepest_neighbor
            current_score = steepest_score
            cur_box = steepest_box
            cur_player = steepest_player
            current_path_actions.append(action_str)
            
            if current_score < best_score:
                best_score = current_score
                best_state = current_state
                best_box = cur_box
                best_player = cur_player
                best_path_actions = list(current_path_actions)
                
            grad_str = f"∇ = {steepest_gradient:.1f} (Cực dốc)" if steepest_gradient < -1.0 else f"∇ = {steepest_gradient:.1f} (Dốc lài)"
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
            print(f"| {steps+1:<5} | {score_str:<23} | {action_str:<25} | {grad_str:<20} |")
            
        else:
            # Tất cả đạo hàm ∇ >= 0. Trượt xe đến đáy thung lũng rồi!
            print(f"| {steps+1:<5} | {'-':<23} | {'Đạp phanh chết':<25} | {'∇ >= 0 (Tới đáy/Kẹt)':<20} |")
            break
            
        steps += 1
        
    print("="*105)
    
    if "THÀNH CÔNG" in status:
        print(f"| {'END':<5} | {'0.0':<23} | {'VỀ ĐÍCH AN TOÀN':<25} | {status:<20} |")
    else:
        status = "🔴 Chạm Đáy Thung Lũng (Local Min)"
        score_str = f"{best_score:.1f} ({best_box:.1f}+{best_player:.1f})"
        print(f"| {'END':<5} | {score_str:<23} | {'KẸT Ở ĐÁY VỰC':<25} | {status:<20} |")
        
    print("="*105)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return best_state, best_path_actions, best_score, steps, time_taken_ms, status
