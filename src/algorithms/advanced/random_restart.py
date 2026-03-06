import time
from src.algorithms.basic.stochastic_hill_climbing import stochastic_hill_climbing

# ==============================================================================
# AI SOKOBAN: RANDOM-RESTART HILL CLIMBING
# ==============================================================================

def random_restart_hill_climbing(initial_state, get_neighbors_func, get_heuristic_func, max_restarts=10, max_steps_per_restart=200):
    """
    Thuật toán AI Tìm kiếm Random-Restart Hill Climbing.
    Dựa trên nền tảng Stochastic Hill Climbing nhưng cho phép "Đập đi xây lại".
    Nếu Stochastic chạy vào ngõ cụt hoặc bị kẹt vòng lặp, AI sẽ tự động Khởi động lại
    từ vạch xuất phát, hy vọng lần tung xúc xắc tiếp theo sẽ rẽ sang một nhánh tốt hơn.
    
    Args:
        initial_state (State): Trạng thái đầu.
        get_neighbors_func: Hàm sinh nhánh đi.
        get_heuristic_func: Hàm đánh giá (Deadlock = Vô Cực).
        max_restarts: Số mạng tối đa được hồi sinh.
        max_steps_per_restart: Số bước cho mỗi mạng.
        
    Returns:
        tuple: (final_state, best_score, total_steps, time_taken_ms, status_message)
    """
    start_time = time.time()
    
    # Khảo sát điểm kỷ lục của tất cả các Lần Khởi Động
    global_best_state = initial_state
    global_best_path = []
    global_best_score = get_heuristic_func(initial_state)[0]
    total_steps_all_restarts = 0
    final_status = "🔴 Thất Bại Kép (Hết Mạng)"
    
    print("\n" + "*"*80)
    print(f"⭐ BẮT ĐẦU RANDOM-RESTART HILL CLIMBING (Cấp cho AI vỏn vẹn {max_restarts} Mạng)")
    print("*"*80)
    
    for restart in range(max_restarts):
        print(f"\n[🚀 LẦN KHỞI ĐỘNG LẠI THỨ {restart + 1}/{max_restarts}] Đang tung xúc xắc tìm đường...")
        
        # Gọi Stochastic Hill Climbing để "vượt rào" ở lần cược này
        final_state, path_actions, score, steps, _, local_status = stochastic_hill_climbing(
            initial_state, 
            get_neighbors_func, 
            get_heuristic_func, 
            max_steps=max_steps_per_restart
        )
        
        total_steps_all_restarts += steps
        
        # Cập nhật kết quả Kỷ Lục Toàn Cục
        if score < global_best_score:
            global_best_score = score
            global_best_state = final_state
            global_best_path = path_actions
            
        # Kiểm tra Thắng game
        if score <= 0.0:
            final_status = "🟢 GIẢI THÀNH CÔNG BẰNG RANDOM-RESTART!"
            print(f"\n✅ ĐÃ TÌM THẤY ĐÍCH TRONG LẦN CHẠY THỨ {restart + 1}!")
            break
            
        # Nếu chưa thắng, thông báo kẹt để tiếp tục Vòng Hồi Sinh tiếp theo
        print(f"❌ Lần {restart + 1} thất bại (Dừng ở Heuristic {score:.2f}). Khởi động lại!")
        
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    return global_best_state, global_best_path, global_best_score, total_steps_all_restarts, time_taken_ms, final_status
