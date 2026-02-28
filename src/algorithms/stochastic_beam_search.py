import time
import random

# ==============================================================================
# AI SOKOBAN: STOCHASTIC BEAM SEARCH (TÌM KIẾM CHÙM NGẪU NHIÊN P)
# ==============================================================================

def stochastic_beam_search(initial_state, get_neighbors_func, get_heuristic_func, k_beam=10, max_steps=1000):
    """
    Thuật toán AI Stochastic Beam Search (Tìm kiếm Chùm Ngẫu nhiên).
    Thay vì vét cạn 10 thằng Giỏi Nhất cứng nhắc như bộ máy rập khuôn (Local Beam), 
    Nó quay Sổ Số kiến thiết để chọn 10 thằng đi tiêp!
    
    Luật Rút Thăm: Điểm Heuristic AI càng THẤP (Càng gần đích) thì Tỉ lệ Trúng Vé Số càng CAO,
    Nhưng những nhánh ngu ngốc rẽ bậy bạ cũng có 1 ít đặc ân trúng số < 1%. 
    ===> Bí kíp giúp Duy trì Đa Dạng Tiên Sinh (Diversity), mở đường cho Đột Biến Gen Đỉnh Cao!
    
    Args:
        k_beam (int): Kích Thước Chùm lướt (VD: 10 Vệt Máu).
    """
    start_time = time.time()
    
    current_score, cur_box, cur_player = get_heuristic_func(initial_state)
    
    if current_score <= 0.0:
        return initial_state, current_score, 0, (time.time() - start_time) * 1000, "🟢 GIẢI THÀNH CÔNG TỪ ĐẦU!"
        
    beam_states = [(current_score, cur_box, cur_player, initial_state, [])]
    visited = {initial_state}
    
    best_overall_score = current_score
    best_overall_state = initial_state
    best_o_box, best_o_player = cur_box, cur_player
    best_overall_path = []
    
    steps = 0
    status = "🔴 Thất Bại Kép (Chết Chùm / Đứt Hơi)"
    
    print("\n" + "="*105)
    print(f"| {'STEP':<5} | {'CHÙM TOP 1 HIỆN TẠI':<23} | {'SỐ ỨNG VIÊN SINH RA':<25} | {'BỐC VÉ SỐ TOÀN CỤC':<20} |")
    print("="*105)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})"
    print(f"| {0:<5} | {score_str:<23} | {'Khởi tạo hạt giống 1':<25} | {'Bắt đầu Tỏa Chùm':<20} |")
    
    while steps < max_steps and beam_states:
        # Check condition to win
        beam_states.sort(key=lambda x: x[0])
        if beam_states[0][0] <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Tia Sáng Đã Chạm Đích)!"
            best_overall_score = beam_states[0][0]
            best_overall_state = beam_states[0][3]
            best_o_box, best_o_player = beam_states[0][1], beam_states[0][2]
            best_overall_path = beam_states[0][4]
            break
            
        all_neighbors_pool = []
        
        for score, b_w, p_w, state, path in beam_states:
            neighbors = get_neighbors_func(state)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    
                    n_score, n_b, n_p = get_heuristic_func(neighbor)
                    
                    if n_score != float('inf'):
                        dx = neighbor.player_pos[0] - state.player_pos[0]
                        dy = neighbor.player_pos[1] - state.player_pos[1]
                        action_str = "LÊN" if dy == -1 else "XUỐNG" if dy == 1 else "TRÁI" if dx == -1 else "PHẢI"
                        if neighbor.boxes != state.boxes: action_str = "ĐẨY " + action_str
                        
                        all_neighbors_pool.append((n_score, n_b, n_p, neighbor, path + [action_str]))
                        
        if not all_neighbors_pool:
            status = "🔴 Kẹt Nhóm (Tất cả các Tia Sáng đều chui vào Ngõ Cụt / Loop)"
            print(f"| {steps+1:<5} | {'-':<23} | {'Đuối lý toàn tập':<25} | {'Tắt ngóm chùm tia':<20} |")
            break
            
        # =========================================================================
        # QUAY SỔ XỐ (Weighted Random Sampling Without Replacement)
        # =========================================================================
        max_pool_score = max(item[0] for item in all_neighbors_pool)
        
        next_beam = []
        pool_copy = list(all_neighbors_pool)
        
        # CÔNG THỨC: Điểm Heuristic càng Thấp -> Càng tới gần Đích -> Số lượng Vé Số Tỉ Lệ Nghịch Càng Cao 
        # (Để cho Điểm Lớn cực tồi tệ vẫn còn cửa sống hẹp với 0.1 vé)
        epsilon = 0.1
        weights = [max_pool_score - item[0] + epsilon for item in pool_copy]
        
        target_k = min(k_beam, len(pool_copy))
        for _ in range(target_k):
            total_weight = sum(weights)
            
            # Xoay vòng quay xổ số lượm kẹo
            r = random.uniform(0, total_weight)
            upto = 0
            for i, w in enumerate(weights):
                if upto + w >= r:
                    next_beam.append(pool_copy.pop(i))
                    weights.pop(i) # Xé vé đi luôn, vòng lặp sau chừa nhánh rẽ khác
                    break
                upto += w
                
        beam_states = next_beam
        beam_states.sort(key=lambda x: x[0])
        
        champ_score, champ_b, champ_p, champ_state, champ_path = beam_states[0]
        if champ_score < best_overall_score:
            best_overall_score = champ_score
            best_overall_state = champ_state
            best_o_box, best_o_player = champ_b, champ_p
            best_overall_path = champ_path
            
        score_str = f"{champ_score:.1f} ({champ_b:.1f}+{champ_p:.1f})"
        cand_str = f"Sinh {len(all_neighbors_pool)} Mạng Lưới"
        vet_str = f"Rút thăm {len(beam_states)} Lô Kép"
        print(f"| {steps+1:<5} | {score_str:<23} | {cand_str:<25} | {vet_str:<20} |")
        
        steps += 1
        
    print("="*105)
    
    if "THÀNH CÔNG" in status:
        print(f"| {'END':<5} | {'0.0':<23} | {'CHẠM ĐÍCH VUI VẺ':<25} | {status:<20} |")
    else:
        score_str = f"{best_overall_score:.1f} ({best_o_box:.1f}+{best_o_player:.1f})"
        print(f"| {'END':<5} | {score_str:<23} | {'RÚT ĐỈNH CHÓP CHÙM':<25} | {status:<20} |")
        
    print("="*105)
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return best_overall_state, best_overall_path, best_overall_score, steps, time_taken_ms, status
