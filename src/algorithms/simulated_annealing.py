import time
import math
import random

# ==============================================================================
# AI SOKOBAN: SIMULATED ANNEALING (LUYỆN KIM MÔ PHỎNG)
# ==============================================================================

def simulated_annealing(initial_state, get_neighbors_func, get_heuristic_func, initial_temp=100.0, cooling_rate=0.99, max_steps=10000):
    """
    Thuật toán AI Tìm kiếm Simulated Annealing (Luyện kim mô phỏng).
    Cho phép "Leo xuống dốc" (chọn nhánh tồi tệ hơn) để lấy đà nhảy qua thung lũng (thoát Local Optima).
    Xác suất dũng cảm đi xuống dốc này sẽ nguội dần theo thời gian (Temp).
    
    Args:
        initial_temp (float): Nhiệt độ ban đầu (Cấp đà nhảy cực mạnh).
        cooling_rate (float): Hệ số Tốc độ nguội kim loại (Ví dụ 0.99 = Giảm 1% mỗi bước).
    """
    start_time = time.time()
    
    current_state = initial_state
    current_score, cur_box, cur_player = get_heuristic_func(current_state)
    
    # Lưu danh Kỷ Lục Toàn Cục (Không bị trôi dạt theo biến current)
    best_state = current_state
    best_score = current_score
    best_box = cur_box
    best_player = cur_player
    best_path_actions = []
    current_path_actions = []
    
    steps = 0
    temp = initial_temp
    status = "🔴 Thất Bại (Lạnh Cứng / Quá Limit)"
    
    # Ở Thuật toán này không dùng bộ lọc Set(visited) do Quá Trình Luyện Kim đòi hỏi 
    # cho phép "Tua đi tua lại" một đoạn đường (đi lùi rồi lại tiến) để chờ Đợi Nhiệt Nguội!
    
    print("\n" + "="*105)
    print(f"| {'STEP':<5} | {'HEURISTIC TỔNG HIỆN TẠI':<23} | {'HÀNH ĐỘNG':<25} | {'TRẠNG THÁI':<20} | {'NHIỆT':<8} |")
    print("="*105)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<23} | {'Khởi tạo ban đầu':<25} | {'Lò Đang Nóng...':<20} | {temp:<8.2f} |")
    
    while steps < max_steps and temp > 0.001:
        if current_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG TẠI ĐẦU BẢNG LƯU TRỮ!"
            break
            
        if best_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Kéo Tủ Kỷ Lục Ra)!"
            current_state = best_state
            current_score = best_score
            cur_box = best_box
            cur_player = best_player
            break
            
        neighbors = get_neighbors_func(current_state)
        
        # Chọn ngẫu nhiên 1 nhánh (BẤT KỂ TỐT XẤU, không cần lọc như Stochastic)
        if not neighbors:
            status = "🔴 Kẹt cứng (Không còn nước đi)"
            break
            
        chosen_neighbor = random.choice(neighbors)
        next_score, box_w, player_w = get_heuristic_func(chosen_neighbor)
        
        # Độ chênh lệch Điểm (Delta E). Nếu âm = Đã tốt lên. Nếu dương = Bị Tồi đi!
        delta_e = next_score - current_score
        
        should_move = False
        action_flag = ""
        
        # Hàm Heuristic chặn chết Deadlock bằng Inf
        if next_score != float('inf'):
            
            # TRƯỜNG HỢP 1: NƯỚC ĐI TỐT HƠN HOẶC BẰNG (NHẬN LUÔN)
            if delta_e <= 0:
                should_move = True
                action_flag = "Leo Lên (Tốt)" if delta_e < 0 else "Đi Ngang (Hòa)"
                
            # TRƯỜNG HỢP 2: NƯỚC ĐI TỒI TỆ HƠN (DÙNG ĐÀ NHIỆT LƯỢNG ĐỂ BẬT NHẢY ANNEALING)
            else:
                try:
                    # Phương trình xác suất Boltzman e^(-deltaE / Temp)
                    prob = math.exp(-delta_e / temp)
                    # Lấy cò súng Radom (0->1). Nếu xác suất Prob lớn hơn viên đạn, Ta dũng cảm Đi lùi!
                    if random.random() < prob:
                        should_move = True
                        action_flag = "Nhảy Lùi (Chịu Đấm)"
                except OverflowError:
                    pass # Temp rớt quá sâu => Xác suất 0% => Không theèm nhúc nhích
                    
        # Nếu Quả lắc chọn nước đi này
        if should_move:
            # Khảo sát Lịch Sử
            dx = chosen_neighbor.player_pos[0] - current_state.player_pos[0]
            dy = chosen_neighbor.player_pos[1] - current_state.player_pos[1]
            action_str = "Không rõ"
            if dx == 0 and dy == -1: action_str = "Di chuyển LÊN"
            elif dx == 0 and dy == 1: action_str = "Di chuyển XUỐNG"
            elif dx == -1 and dy == 0: action_str = "Di chuyển TRÁI"
            elif dx == 1 and dy == 0: action_str = "Di chuyển PHẢI"
            
            if chosen_neighbor.boxes != current_state.boxes:
                action_str = action_str.replace("Di chuyển", "ĐẨY HỘP")
                
            # Đổi chỗ Current
            current_state = chosen_neighbor
            current_score = next_score
            cur_box = box_w
            cur_player = player_w
            current_path_actions.append(action_str)
            
            # Cập nhật Bộ Lưu Trữ Tối Cổ Kỷ Lục (Global Best)
            # Tại sao? Vì SA hay ngáo ngơ nhảy lùi rớt xuống vách núi, nên phải có cái neo giữ Kỷ Lục Đẹp Nhất!
            if current_score < best_score:
                best_score = current_score
                best_state = current_state
                best_box = cur_box
                best_player = cur_player
                best_path_actions = list(current_path_actions)
                
            # Print tiến trình
            score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
            print(f"| {steps+1:<5} | {score_str:<23} | {action_str:<25} | {action_flag:<20} | {temp:<8.2f} |")
            
        else:
            # Random đập trúng tảng đá (Deadlock / Hoặc Không Vượt Qua Xác Suất Nguội) => Đứng vỗ Đùi
            print(f"| {steps+1:<5} | {'-':<23} | {'Đứng im (Bị từ chối)':<25} | {'Từ chối Nước xấu':<20} | {temp:<8.2f} |")
            
        # Nguội bớt Lò Rèn
        temp *= cooling_rate
        steps += 1
        
    print("="*105)
    
    # SA luôn luôn trả về Bản Save Game xịn nhất (Best State) chứ hiếm khi trả về Hiện Tại
    if status == "🟢 GIẢI THÀNH CÔNG TẠI ĐẦU BẢNG LƯU TRỮ!" or status == "🟢 GIẢI THÀNH CÔNG (Kéo Tủ Kỷ Lục Ra)!":
        print(f"| {'END':<5} | {'0.0':<23} | {'CHẠM ĐÍCH VUI VẺ':<25} | {status:<20} | {'-':<8} |")
    else:
        status = "🔴 Hết Nhiệt / Kẹt ở Thung Lũng"
        score_str = f"{best_score:.1f} ({best_box:.1f}+{best_player:.1f})"
        print(f"| {'END':<5} | {score_str:<23} | {'RÚT KỶ LỤC AN TOÀN NHẤT':<25} | {status:<20} | {'-':<8} |")
        
    print("="*105)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return best_state, best_path_actions, best_score, steps, time_taken_ms, status
