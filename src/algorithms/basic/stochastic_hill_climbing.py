import time
import random

# ==============================================================================
# AI SOKOBAN: STOCHASTIC HILL CLIMBING (CÓ DEADLOCK & HEURISTIC 3 YẾU TỐ)
# ==============================================================================

def stochastic_hill_climbing(initial_state, get_neighbors_func, get_heuristic_func, max_steps=10000):
    """
    Thuật toán AI Tìm kiếm leo đồi Ngẫu nhiên (Stochastic).
    Chỉ chọn ngẫu nhiên MỘT nhánh trong Lưới "Các Nhánh Tốt Hơn hoặc Bằng" để đi tiếp.
    Giúp tránh kẹt tại "Cao nguyên" (Plateau) do bị lưỡng lự khi đi ngang.
    
    Args:
        initial_state (State): OOP Tuple (player_pos, boxes) của game.
        get_neighbors_func (Callable): Hàm sinh các nhánh.
        get_heuristic_func (Callable): Hàm đánh giá (Deadlock = Vô Cực).
        max_steps (int): Giới hạn lặp để Game khỏi bị crash.
        
    Returns:
        tuple: (final_state, best_score, steps, time_taken_ms, status_message)
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box, cur_player = get_heuristic_func(current_state)
    steps = 0
    visited = {current_state}
    path_actions = []
    
    status = "🔴 Thất Bại (Kẹt Đỉnh Đồi / Phải quay trượng)"
    
    print("\n" + "="*88)
    print(f"| {'STEP':<5} | {'HEURISTIC SCORE':<22} | {'HÀNH ĐỘNG':<25} | {'TRẠNG THÁI':<20} |")
    print("="*88)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<22} | {'Khởi tạo ban đầu':<25} | {'Đang xúc xắc...':<20} |")
    
    while steps < max_steps:
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG!"
            break
            
        neighbors = get_neighbors_func(current_state)
        
        # Tạo giỏ Rổ để lọc các nhánh Ứng viên (Candidates) tốt hơn (hoặc bằng) nhánh hiện tại
        better_or_equal_candidates = []
        
        for neighbor in neighbors:
            if neighbor not in visited:
                score, box_w, player_w = get_heuristic_func(neighbor)
                
                # Ở SOKOBAN, đi ngang là điều Cực Kỳ Cần Thiết (Đầu người chơi né hộp, tìm góc khác)
                # Stochastic sẽ đưa cả nhánh "Tốt hơn" và "Bằng điểm" vào giỏ gắp thăm
                if score <= current_score:
                    better_or_equal_candidates.append((score, box_w, player_w, neighbor))
                    
        # Nếu Rổ có đồ -> Móc thăm ngẫu nhiên 1 cái từ giỏ để đi (Stochastic)
        if better_or_equal_candidates:
            # Chọn ngẫu nhiên 1 ứng viên
            chosen_score, chosen_box, chosen_player, chosen_state = random.choice(better_or_equal_candidates)
            
            # Khảo sát Action in trên Log
            dx = chosen_state.player_pos[0] - current_state.player_pos[0]
            dy = chosen_state.player_pos[1] - current_state.player_pos[1]
            action_str = "Không rõ"
            if dx == 0 and dy == -1: action_str = "Di chuyển LÊN"
            elif dx == 0 and dy == 1: action_str = "Di chuyển XUỐNG"
            elif dx == -1 and dy == 0: action_str = "Di chuyển TRÁI"
            elif dx == 1 and dy == 0: action_str = "Di chuyển PHẢI"
            
            if chosen_state.boxes != current_state.boxes:
                action_str = action_str.replace("Di chuyển", "ĐẨY HỘP")
                
            # Phân tích cờ Plateau (Đi ngang) dựa trên điểm số hiện tại TRƯỚC khi gán
            plateau_flag = "Đi Rẻ Ngang" if chosen_score == current_score else "Tốt lên (Random)"
            
            current_state = chosen_state
            current_score = chosen_score
            cur_box = chosen_box
            cur_player = chosen_player
            visited.add(chosen_state)
            path_actions.append(action_str)
            
            # Print tiến trình
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
            print(f"| {steps+1:<5} | {score_str:<22} | {action_str:<25} | {plateau_flag:<20} |")
            
        else:
            # Thuật toán chính thức bế tắc tại đây do tất cả ngã rẽ xung quanh đều TỘI TỆ HƠN hẳn (Score Cao)
            status = "🔴 Kẹt Ở Ngõ Cụt"
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
            print(f"| {'END':<5} | {score_str:<22} | {'KẸT (Tất cả đường Xấu)':<25} | {status:<20} |")
            break
            
        steps += 1
        
    if status == "🟢 GIẢI THÀNH CÔNG!":
         score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
         print(f"| {'END':<5} | {score_str:<22} | {'CHẠM ĐÍCH VUI VẺ':<25} | {status:<20} |")
        
    print("="*88)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return current_state, path_actions, current_score, steps, time_taken_ms, status
