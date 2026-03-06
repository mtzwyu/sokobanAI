import time

# ==============================================================================
# AI SOKOBAN: LOCAL BEAM SEARCH (TÌM KIẾM CHÙM ĐỊA PHƯƠNG)
# ==============================================================================

def local_beam_search(initial_state, get_neighbors_func, get_heuristic_func, k_beam=10, max_steps=1000):
    """
    Thuật toán AI Local Beam Search (Tìm kiếm Chùm).
    Thay vì chỉ nhớ 1 trạng thái hiện tại (Hill Climbing thông thường), nó duy trì K trạng thái (Beam) cùng lúc.
    Mỗi vòng lặp, nó bung toàn bộ láng giềng của K trạng thái này ra, dồn vào một đống chung.
    Sau đó chọn lọc khắt khe K láng giềng TỐT NHẤT trong đống đó để đi tiếp vòng sau.
    
    Giúp lan tỏa song song (BFS bị giới hạn), tránh sa lầy vào Local Optima đơn độc.
    
    Args:
        k_beam (int): Độ rộng chùm sáng (Số vòng xoay song song). VD: 10
    """
    start_time = time.time()
    
    # -------------------------------------------------------------
    # KHỞI TẠO BƯỚC 1 (Chỉ có 1 hạt giống ban đầu)
    # -------------------------------------------------------------
    current_score, cur_box, cur_player = get_heuristic_func(initial_state)
    
    if current_score <= 0.0:
        return initial_state, current_score, 0, (time.time() - start_time) * 1000, "🟢 GIẢI THÀNH CÔNG TỪ ĐẦU!"
        
    beam_states = [(current_score, cur_box, cur_player, initial_state, [])]
    visited = {initial_state} # Vẫn xài Visited để cắt đứt các Vệt Chùm tự tát vào mặt nhau
    
    best_overall_score = current_score
    best_overall_state = initial_state
    best_o_box, best_o_player = cur_box, cur_player
    best_overall_path = []
    
    steps = 0
    status = "🔴 Thất Bại Kép (Chết Chùm / Quá Limit)"
    
    print("\n" + "="*105)
    print(f"| {'STEP':<5} | {'CHÙM TOP 1 HIỆN TẠI':<23} | {'SỐ ỨNG VIÊN SINH RA':<25} | {'VÉT SÀNG (K_BEAM)':<20} |")
    print("="*105)
    score_str = f"{current_score:.1f} ({cur_box:.1f}+{cur_player:.1f})" if current_score != float('inf') else "inf"
    print(f"| {0:<5} | {score_str:<23} | {'Khởi tạo hạt giống 1':<25} | {'Bắt đầu Tỏa Chùm':<20} |")
    
    # -------------------------------------------------------------
    # VÒNG LẶP TOẢ CHÙM (BEAM EXPANSION)
    # -------------------------------------------------------------
    while steps < max_steps and beam_states:
        # Kiểm tra Nhóm Chùm Sáng xem có tên nào lọt lưới Win không?
        top_score = beam_states[0][0]
        if top_score <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Tia Sáng Đã Chạm Đích)!"
            best_overall_state = beam_states[0][3]
            best_overall_score = beam_states[0][0]
            best_o_box, best_o_player = beam_states[0][1], beam_states[0][2]
            best_overall_path = beam_states[0][4]
            break
            
        all_neighbors_pool = []
        
        # 1. Tỏa Sáng: Sinh con đẻ cái của TOÀN BỘ K trạng thái trong Chùm
        for score, b_w, p_w, state, path in beam_states:
            neighbors = get_neighbors_func(state)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    
                    n_score, n_b, n_p = get_heuristic_func(neighbor)
                    
                    # Bỏ sọt rác mấy cái nhánh tự tạo Deadlock
                    if n_score != float('inf'):
                        dx = neighbor.player_pos[0] - state.player_pos[0]
                        dy = neighbor.player_pos[1] - state.player_pos[1]
                        action_str = "LÊN" if dy == -1 else "XUỐNG" if dy == 1 else "TRÁI" if dx == -1 else "PHẢI"
                        if neighbor.boxes != state.boxes: action_str = "ĐẨY " + action_str
                        
                        all_neighbors_pool.append((n_score, n_b, n_p, neighbor, path + [action_str]))
                        
        # 2. Sinh Tồn: Đám cưới xong nếu tuyệt tự thì Chết Chùm luôn
        if not all_neighbors_pool:
            status = "🔴 Kẹt Nhóm (Tất cả các Tia Sáng đều chui vào Ngõ Cụt / Loop)"
            print(f"| {steps+1:<5} | {'-':<23} | {'Đuối lý toàn tập':<25} | {'Tắt ngóm chùm tia':<20} |")
            break
            
        # 3. Tranh Giành Bề Thế: Sort lại cái Nhóm Tổng To đùng vừa gom được
        all_neighbors_pool.sort(key=lambda x: x[0])
        
        # Cắt ngọn, chỉ xả lại Max K nhánh sáng chói lọi nhất! (Sức mạnh Cốt lõi của Local Beam Search)
        beam_states = all_neighbors_pool[:k_beam]
        
        # Update Quả Cầu Pha Lê Kỷ Lục
        champ_score, champ_b, champ_p, champ_state, champ_path = beam_states[0]
        if champ_score < best_overall_score:
            best_overall_score = champ_score
            best_overall_state = champ_state
            best_o_box, best_o_player = champ_b, champ_p
            best_overall_path = champ_path
            
        # In Báo Cáo Chùm Top 1 ra Console
        score_str = f"{champ_score:.1f} ({champ_b:.1f}+{champ_p:.1f})"
        cand_str = f"Sinh {len(all_neighbors_pool)} Mạng Lưới"
        vet_str = f"Giữ lại {len(beam_states)} Elite"
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
