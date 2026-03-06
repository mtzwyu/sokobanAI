import time
from collections import deque

# ==============================================================================
# AI SOKOBAN: TABU SEARCH (TÌM KIẾM CẤM KỴ)
# ==============================================================================

def tabu_search(initial_state, get_neighbors_func, get_heuristic_func, max_steps=10000, tabu_tenure=50):
    """
    Thuật toán AI Tìm kiếm Tabu (Cấm kỵ).
    Nguyên lý: Cấm AI đi lại những nước đi vừa mới đi gần đây (Lưu trong Tabu List).
    Nhờ đó, AI bị ÉP PHẢI chọn những nước đi mới, dù cho Heuristic có tồi tệ hơn đi chăng nữa.
    Giúp thoát khỏi Local Optima (Thung lũng) một cách có hệ thống, thay vì random như Simulated Annealing.
    
    Args:
        tabu_tenure (int): Kích thước danh sách cấm (Độ dài trí nhớ ngắn hạn). 
                           Nếu = 50, AI sẽ không được đi lại 50 ô vừa đi qua gần nhất.
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box, cur_player = get_heuristic_func(current_state)
    
    # Kỷ lục Toàn cục (Global Best)
    best_state = current_state
    best_score = current_score
    best_box = cur_box
    best_player = cur_player
    best_path_actions = []
    current_path_actions = []
    
    # Trí nhớ ngắn hạn (Tabu List) - Dùng Deque để tự động đẩy phần tử cũ ra ngoài khi đầy
    tabu_list = deque(maxlen=tabu_tenure)
    tabu_list.append(current_state)
    
    steps = 0
    status = "🔴 Thất Bại (Kẹt Không Có Lối / Quá Limit)"
    
    print("\n" + "="*105)
    print(f"| {'STEP':<5} | {'HEURISTIC TỔNG HIỆN TẠI':<23} | {'HÀNH ĐỘNG':<25} | {'TRẠNG THÁI (TABU)':<20} |")
    print("="*105)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<23} | {'Khởi tạo ban đầu':<25} | {'Bắt đầu Ghi nhớ':<20} |")
    
    while steps < max_steps:
        # 1. Nếu tìm thấy Đích -> Dừng
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Tới đích trực tiếp)!"
            break
            
        if best_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Móc từ Kỷ Lục ra)!"
            current_state = best_state
            current_score = best_score
            cur_box, cur_player = best_box, best_player
            break
            
        # 2. Lấy tất cả các láng giềng
        neighbors = get_neighbors_func(current_state)
        
        # 3. Tìm ứng viên TỐT NHẤT TRONG SỐ CÁC LÁNG GIỀNG KHÔNG BỊ CẤM
        best_candidate = None
        best_candidate_score = float('inf')
        best_c_box = float('inf')
        best_c_player = float('inf')
        
        for neighbor in neighbors:
            score, box_w, player_w = get_heuristic_func(neighbor)
            
            # Hàm Heuristic đã trừ khử Deadlock bằng điểm vô cực (inf)
            if score == float('inf'):
                continue
                
            # LUẬT Aspiration Criterion (Đặc Ân Trâm Anh Thế Phiệt):
            # Nếu láng giềng này TỐT HƠN CẢ KỶ LỤC LỊCH SỬ (Global Best),
            # thì CHO PHÉP PHÁ VỠ LỆNH CẤM (Vượt qua Tabu List).
            is_tabu = neighbor in tabu_list
            if is_tabu and score < best_score:
                is_tabu = False # Xóa án cấm
                
            # Cập nhật Ứng viên (Miễn là Không Nhúng Chàm Tabu List)
            if not is_tabu and score < best_candidate_score:
                best_candidate = neighbor
                best_candidate_score = score
                best_c_box = box_w
                best_c_player = player_w
                
        # 4. Quyết định
        if best_candidate is not None:
            # So sánh xem Mình đang Tiết hay Lùi (In Log)
            delta_e = best_candidate_score - current_score
            action_flag = "Leo Tiến" if delta_e < 0 else "Đi Ngang" if delta_e == 0 else "Lùi (ÉP BUỘC)"
            
            # Suy ra Hành động
            dx = best_candidate.player_pos[0] - current_state.player_pos[0]
            dy = best_candidate.player_pos[1] - current_state.player_pos[1]
            action_str = "Không rõ"
            if dx == 0 and dy == -1: action_str = "Di chuyển LÊN"
            elif dx == 0 and dy == 1: action_str = "Di chuyển XUỐNG"
            elif dx == -1 and dy == 0: action_str = "Di chuyển TRÁI"
            elif dx == 1 and dy == 0: action_str = "Di chuyển PHẢI"
            
            if best_candidate.boxes != current_state.boxes:
                action_str = action_str.replace("Di chuyển", "ĐẨY HỘP")
                
            # Di chuyển sang Ứng viên (Dù điểm có Tệ hơn Heuristic hiện tại cũng phải chịu)
            current_state = best_candidate
            current_score = best_candidate_score
            cur_box = best_c_box
            cur_player = best_c_player
            current_path_actions.append(action_str)
            
            # Đưa nhánh vừa đi vào Sổ Bìa Đen (Tabu List)
            tabu_list.append(current_state)
            
            # Cập nhật Kỷ Lục Global Best
            if current_score < best_score:
                best_score = current_score
                best_state = current_state
                best_box = cur_box
                best_player = cur_player
                best_path_actions = list(current_path_actions)
                action_flag = "🌟 Phá Kỷ Lục"
                
            # Print tiến trình
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
            print(f"| {steps+1:<5} | {score_str:<23} | {action_str:<25} | {action_flag:<20} |")
            
        else:
            # Nhốt tứ bề (Tất cả xung quanh đều là ngõ cụt Deadlock HOẶC đều nằm trong sổ đen Tabu)
            print(f"| {steps+1:<5} | {'-':<23} | {'Bị giam cầm':<25} | {'Tabu chặn kín 4 hướng':<20} |")
            break
            
        steps += 1
        
    print("="*105)
    
    if "THÀNH CÔNG" in status:
        print(f"| {'END':<5} | {'0.0':<23} | {'CHẠM ĐÍCH VUI VẺ':<25} | {status:<20} |")
    else:
        status = "🔴 Hết Đường / Quá Limit"
        score_str = f"{best_score:.1f} ({best_box:.1f}+{best_player:.1f})"
        print(f"| {'END':<5} | {score_str:<23} | {'RÚT KỶ LỤC TỐT NHẤT':<25} | {status:<20} |")
        
    print("="*105)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return best_state, best_path_actions, best_score, steps, time_taken_ms, status
