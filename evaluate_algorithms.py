import time
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.level import Level
from src.algorithms.solver_adapter import SolverAdapter

from src.algorithms.basic_search.simple_hill_climbing import simple_hill_climbing
from src.algorithms.basic_search.steepest_ascent import steepest_ascent_hill_climbing
from src.algorithms.stochastic_search.stochastic_hc import stochastic_hill_climbing
from src.algorithms.stochastic_search.first_choice_hc import first_choice_hill_climbing
from src.algorithms.escape_maxima.backtracking_hc import backtracking_hill_climbing
from src.algorithms.escape_maxima.jumping_hc import jumping_hill_climbing
from src.algorithms.escape_maxima.random_restart_hc import random_restart_hill_climbing


def make_jump_function(adapter):
    """
    Tạo hàm nhảy ngẫu nhiên cho Jumping HC.
    Thực hiện 5-15 bước di chuyển hợp lệ ngẫu nhiên từ trạng thái hiện tại
    để thoát khỏi Local Minima.
    """
    def generate_random_jump(current_state):
        import random
        state = current_state
        actions = []
        num_jumps = random.randint(5, 15)
        
        for _ in range(num_jumps):
            neighbors = adapter.get_neighbors(state)
            if not neighbors:
                break
            action, next_state = random.choice(neighbors)
            state = next_state
            actions.append(action)
        
        if actions:
            return state, actions
        return None, []
    
    return generate_random_jump

def make_restart_function(initial_state, adapter):
    """
    Tạo hàm khởi động lại cho Random Restart HC.
    Đưa nhân vật đi ngẫu nhiên 3-10 bước từ trạng thái ban đầu
    để tạo điểm xuất phát mới mỗi lần restart.
    """
    def generate_random_initial():
        import random
        state = initial_state
        num_moves = random.randint(3, 10)
        
        for _ in range(num_moves):
            neighbors = adapter.get_neighbors(state)
            if not neighbors:
                break
            _, next_state = random.choice(neighbors)
            state = next_state
        
        return state
    
    return generate_random_initial

def trace_heuristic_history(initial_state, path, solver_adapter):
    """
    Takes the final taken path and reconstructs the heuristic states step-by-step
    to show exactly how the algorithm navigated down the heuristic landscape.
    """
    get_neighbors = solver_adapter.get_neighbors
    original_h = solver_adapter.get_heuristic_func()
    
    history = []
    current_state = initial_state
    
    history.append(original_h(current_state))
    
    for action_taken in path:
        neighbors = get_neighbors(current_state)
        found = False
        for a, s in neighbors:
            if a == action_taken:
                current_state = s
                found = True
                break
        # Just in case our fast 'get_neighbors' doesn't align with jump logic, fallback handle
        if not found:
            pass # Ideally path is strictly valid neighbors
        
        history.append(original_h(current_state))
        
    return history

def run_evaluation(target_level=None):
    if target_level is None:
        print("Đang tải bàn cờ mặc định (Map)...")
        level = Level()
        # Chạy trên map mặc định, bạn có thể đổi tên tùy ý
        level.load_from_file("src/map/map_default.xlsx")
    else:
        print("Đang lấy mốc bàn cờ hiện tại từ game...")
        level = target_level
    
    adapter = SolverAdapter(level)
    initial_state = adapter.get_initial_state()
    get_neighbors = adapter.get_neighbors
    get_heuristic = adapter.get_heuristic_func()
    
    # Tạo hàm hỗ trợ thật cho Jumping HC và Random Restart HC
    jump_fn = make_jump_function(adapter)
    restart_fn = make_restart_function(initial_state, adapter)
    
    algorithms = [
        ("Simple Hill Climbing",      simple_hill_climbing,          [5000]),
        ("Steepest Ascent",           steepest_ascent_hill_climbing,  [5000]),
        ("Stochastic Hill Climbing",  stochastic_hill_climbing,       [5000]),
        ("First Choice Hill Climbing",first_choice_hill_climbing,     [5000]),
        ("Backtracking Hill Climbing",backtracking_hill_climbing,     [5000]),
        ("Jumping Hill Climbing",     jumping_hill_climbing,          [jump_fn, 5000]),
        ("Random Restart HC",         random_restart_hill_climbing,   [restart_fn, 10, 500]),
    ]
    
    results = []
    max_steps = 0 # To align excel columns nicely
    
    print("Bắt đầu chạy thí nghiệm 7 thuật toán...\n")
    for name, func, extra_args in algorithms:
        print(f"-> Đang chạy: {name} ...", end=" ")
        start_time = time.time()
        
        # Gọi hàm
        best_state, path = func(initial_state, get_neighbors, get_heuristic, *extra_args)
        
        end_time = time.time()
        exec_time_ms = (end_time - start_time) * 1000
        
        print(f"Hoàn thành ({exec_time_ms:.2f} ms). H(cuối)={get_heuristic(best_state)}")
        
        # Truy vết lịch sử Heuristic (đường đi hàm giảm)
        h_history = trace_heuristic_history(initial_state, path, adapter)
        max_steps = max(max_steps, len(h_history))
        
        results.append({
            "Thuật toán": name,
            "Tốc độ (ms)": round(exec_time_ms, 2),
            "Số bước đi": len(path),
            "H(Start)": h_history[0],
            "H(End)": get_heuristic(best_state),
            "h_history_list": h_history,
            "path": path
        })
        
    print("\nQuá trình chạy hoàn tất. Đang cập nhật ra file dạng bảng tách biệt...")
    
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    filename = "Kq_Thuật_toán_AI_Bảng.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kq AI"

    # Định nghĩa màu sắc (Hex codes)
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid") # Xanh dương
    header_font = Font(color="FFFFFF", bold=True)
    algo_font = Font(color="1F497D", bold=True) # Xanh đậm
    time_font = Font(color="00B050", bold=True) # Xanh lá cây
    center_align = Alignment(horizontal='center', vertical='center')

    # Dòng 1 & 2: Tên thuật toán & Tốc độ
    # Dòng 3: Tiêu đề cột chi tiết
    for c_idx, r in enumerate(results):
        base_col = c_idx * 3 + 1
        
        # Algo Name
        ws.cell(row=1, column=base_col+1, value=f"Thuật toán: {r['Thuật toán']}")
        ws.cell(row=1, column=base_col+1).font = algo_font
        ws.cell(row=1, column=base_col+1).alignment = center_align
        
        # Time
        ws.cell(row=2, column=base_col+1, value=f"Thời gian: {r['Tốc độ (ms)']} ms")
        ws.cell(row=2, column=base_col+1).font = time_font
        ws.cell(row=2, column=base_col+1).alignment = center_align

        # Headers
        headers = ["Bước thứ", "Hành động", "Heuristic"]
        for j, h in enumerate(headers):
            c = ws.cell(row=3, column=base_col+j, value=h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = center_align

    # Lấy số vòng lặp tối đa
    max_steps = max([len(r["path"]) for r in results]) if results else 0
    
    # Dòng 4 trở đi: Kết quả từng bước
    for step in range(-1, max_steps):
        row_idx = step + 5 # Bắt đầu in từ dòng thứ 4 (vì -1 + 5 = 4)
        for c_idx, r in enumerate(results):
            base_col = c_idx * 3 + 1
            path_list = r["path"]
            h_list = r["h_history_list"]
            
            if step == -1:
                ws.cell(row=row_idx, column=base_col+0, value=0).alignment = center_align
                ws.cell(row=row_idx, column=base_col+1, value="Khởi đầu").alignment = center_align
                ws.cell(row=row_idx, column=base_col+2, value=h_list[0]).alignment = center_align
            else:
                if step < len(path_list):
                    action = path_list[step]
                    h_val = h_list[step+1] if step+1 < len(h_list) else "N/A"
                    ws.cell(row=row_idx, column=base_col+0, value=step+1).alignment = center_align
                    ws.cell(row=row_idx, column=base_col+1, value=action).alignment = center_align
                    ws.cell(row=row_idx, column=base_col+2, value=h_val).alignment = center_align

    # Phần Kết Luận ở cuối bảng
    conclusion_row = max_steps + 7
    for c_idx, r in enumerate(results):
        base_col = c_idx * 3 + 1
        name = r["Thuật toán"]
        h_end = r["H(End)"]
        steps = r["Số bước đi"]
        time_ms = r["Tốc độ (ms)"]
        
        if h_end == 0:
            conclusion = f"✓ Thành công: Phá đảo trong {steps} bước ({time_ms} ms)."
        else:
            conclusion = f"✗ Thất bại: Bị kẹt tại đỉnh cục bộ \n(H = {h_end})."
            
        ws.merge_cells(start_row=conclusion_row, start_column=base_col, end_row=conclusion_row+1, end_column=base_col+2)
        cell = ws.cell(row=conclusion_row, column=base_col, value=conclusion)
        cell.font = Font(bold=True, color="9C0006" if h_end > 0 else "006100") # Xanh nếu thắng, Đỏ sẫm nếu thua
        cell.fill = PatternFill(start_color="FFC7CE" if h_end > 0 else "C6EFCE", end_color="FFC7CE" if h_end > 0 else "C6EFCE", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Chỉnh lại cỡ cột cho đẹp
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 15

    wb.save(filename)
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kết quả tuyệt đẹp vào: {filename}")

    # --- Tìm đường đi tốt nhất để trả về ---
    best_algo = None
    best_h = float('inf')
    best_path = []
    
    for r in results:
        h_end = r["H(End)"]
        steps = r["Số bước đi"]
        
        # Tiêu chí: H thấp nhất, nếu bằng thì ưu tiên số bước ít hơn
        if h_end < best_h or (h_end == best_h and steps < len(best_path)):
            best_h = h_end
            best_path = r["path"]
            best_algo = r["Thuật toán"]
            
    print(f"\n[🚀 AI AUTO-DRIVE] Thuật toán ưu việt nhất: {best_algo} | H={best_h} ({len(best_path)} bước)")
    
    return best_path

if __name__ == "__main__":
    run_evaluation()
