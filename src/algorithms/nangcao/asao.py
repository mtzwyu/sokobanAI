import time
import heapq # Hàng Đợi Ưu Tiên (Priority Queue) bắt buộc của A-Star

# ==============================================================================
# AI SOKOBAN: A* SEARCH (TÌM KIẾM THEO Gợi Ý HEURISTIC TOÀN CỤC)
# ==============================================================================

class AStarNode:
    """Đại diện cho 1 Trạng thái (Node) trên Cây Tìm Kiếm của A*"""
    def __init__(self, state, parent=None, action_str="", g_cost=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action_str = action_str
        
        # G (Chi phí thực tế đoạn đường TỪ ĐẦU tới Node này)
        self.g_cost = g_cost
        
        # H (Chi phí ước tính từ Node này CHẠM ĐÍCH - Heuristic)
        self.h_cost = h_cost
        
        # F = G + H (Tổng Chi Phí Đại Diện - Thước đo Đẳng Cấp của Node)
        self.f_cost = g_cost + h_cost
        
    def __lt__(self, other):
        # Hàm so sánh bé hơn (<) cho heapq: Giúp Heap tự động NỔI bọt thằng có F Nhỏ Nhất lên ngọn
        if self.f_cost == other.f_cost:
            # Nếu F bằng nhau (Đồng Hạng), Ưu tiên bốc thằng có H (Heuristic) cự ly tới đích nhỏ hơn ra trước!
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost


def a_star_search(initial_state, get_neighbors_func, get_heuristic_func, max_nodes=100000):
    """
    Thuật toán AI A* (A-Star) - Trùm Cuối Global Search.
    Không như Hill Climbing bị mù chỉ thấy bọn Láng giềng xung quanh.
    A* lưu BẢN ĐỒ TOÀN CỤC. Nó lưu tất cả những ngã rẽ đã từng thấy vào Hàng Đợi (Frontier / Open Set).
    Nó luôn luôn Bốc Rút (Pop) Trạng Thái có điểm F_Cost Nhỏ Nhất toàn bản đồ ra xem xét tiếp.
    ĐẢM BẢO 100%: Nếu có Dòng Đời Nào chui lọt tới đích, A* sẽ tìm ra Dòng Đời NGẮN NHẤT.
    Tuy nhiên: Tốn cái GIÁ là Nhai Siêu Phân Giải RAM (Vì phải Lưu Cây).
    """
    start_time = time.time()
    
    # -------------------------------------------------------------
    # 1. KHỞI TẠO BỘ NHỚ TOÀN CỤC (GLOBAL MEMORY)
    # -------------------------------------------------------------
    start_h, start_box, start_player = get_heuristic_func(initial_state)
    start_node = AStarNode(state=initial_state, parent=None, action_str="Spawn", g_cost=0, h_cost=start_h)
    
    open_set = [] # Tập các Node đang Chờ Khám Xét (FRONTIER)
    heapq.heappush(open_set, start_node)
    
    # Tập các Node Đã Khám Xét (Closed Set) - Lưu State để không Đâm đầu vào Vết Xe Đổ
    # Lưu kiểu Dict: state -> min_g_cost_so_far
    # Vì cùng 1 State (Cùng Hộp, Cùng Vị Trí) nhưng ĐẾN BẰNG ĐƯỜNG NGẮN HƠN thì mới cho vào
    visited = {initial_state: 0}
    
    nodes_explored = 0
    status = "🔴 Thất Bại Kép (Không Tồn Tại Lối Thoát / Tràn RAM Mở Trí Nhớ)"
    best_overall_score = start_h
    
    print("\n" + "="*105)
    print(f"| {'NODES MỞ':<10} | {'ĐỘ SÂU ĐẠT (G)':<20} | {'HEURISTIC TỐT NHẤT (H)':<25} | {'HÀNG ĐỢI RAM (Open)':<20} |")
    print("="*105)

    # -------------------------------------------------------------
    # 2. VÒNG LẶP RÚT RUỘT THẾ GIỚI MỞ
    # -------------------------------------------------------------
    while open_set and nodes_explored < max_nodes:
        # Bốc thằng có Tương Lai Sáng Lạn Nhất Toàn Map ra (F Nhỏ Nhất)
        current_node = heapq.heappop(open_set)
        nodes_explored += 1
        
        # A* Báo Cáo Định Kỳ mỗi 1000 Nodes Khám (Không in lép bép từng bước như Local Search)
        if nodes_explored % 2000 == 0:
            print(f"| {nodes_explored:<10} | Lội Tới Bước G={current_node.g_cost:<10} | H={current_node.h_cost:<23.1f} | Nạp {len(open_set):<15} Nodes |")
            
        # VẼ SANG LỊCH SỬ NHƯ THỦ QUỸ
        if current_node.h_cost < best_overall_score:
            best_overall_score = current_node.h_cost
            
        # 🟢 KIỂM TRA MỤC ĐÍCH CAO CẢ (WIN CONDITION) 🟢
        if current_node.h_cost <= 0.0:
            status = "🟢 GIẢI THÀNH CÔNG (Tới Đích Bằng Đường Nhanh Nhất)!"
            break
            
        # KHAI CHI LÁNG GIỀNG 
        neighbors = get_neighbors_func(current_node.state)
        
        for neighbor in neighbors:
            # Tính Chi Phí Đi Bộ Tới Đứa Này
            # Giả định: Mỗi bước đi Tốn MỘT đơn vị Mồ hôi (Nếu Đẩy Hộp Mệt hơn thì Thuế G cộng 2, nhưng ta cứ tính 1 bước = 1G cho dễ)
            # Ta có thể Thưởng Phạt G nếu đây là Push
            is_push = neighbor.boxes != current_node.state.boxes
            step_cost = 2.0 if is_push else 1.0 # Vd: Ưu tiên AI đi bộ né Hộp chăng? (Thường Sokoban cứ G=1 là chuẩn)
            
            tentative_g = current_node.g_cost + 1.0 # 1 Bước đi = 1 G Cost
            
            # KIỂM DUYỆT BỘ NHỚ
            # Kẻ này Đã Từng Gặp Chưa? NẾU CHƯA GẶP hoặc ĐI ĐƯỜNG NGẮN HƠN (G Nhỏ Kết) -> Thêm vào hàng đợi
            if neighbor not in visited or tentative_g < visited[neighbor]:
                visited[neighbor] = tentative_g
                
                n_hscore, _, _ = get_heuristic_func(neighbor)
                
                # Trừ Cử Kẻ Bị Deadlock (Quyền hạn Tử Hình)
                if n_hscore != float('inf'):
                    # Đạo tên hành động
                    dx = neighbor.player_pos[0] - current_node.state.player_pos[0]
                    dy = neighbor.player_pos[1] - current_node.state.player_pos[1]
                    action_str = "LÊN" if dy == -1 else "XUỐNG" if dy == 1 else "TRÁI" if dx == -1 else "PHẢI"
                    if is_push: action_str = "ĐẨY " + action_str
                    else: action_str = "BƯỚC " + action_str
                        
                    n_node = AStarNode(
                        state=neighbor,
                        parent=current_node,
                        action_str=action_str,
                        g_cost=tentative_g,
                        h_cost=n_hscore
                    )
                    heapq.heappush(open_set, n_node)
                    
    # =========================================================================
    # KẾT THÚC HÀNH DIỄN - GỘP BÁO CÁO CÔNG TRẠNG
    # =========================================================================
    print("="*105)
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    
    # TRUY VẾT DÒNG ĐỜI LUÂN HỒI (RECONSTRUCT PATH)
    # Lần mò từ Nhánh Hiện Tại lùi lên tận Thủy Tổ (Parent=None)
    path_actions = []
    crawl_node = current_node
    while crawl_node.parent is not None:
        path_actions.append(crawl_node.action_str)
        crawl_node = crawl_node.parent
    path_actions.reverse() # Xếp Lịch Sử Xui Chèo
    
    if "THÀNH CÔNG" in status:
        print(f"| {'END':<10} | THÀNH CÔNG BƯỚC G={current_node.g_cost:<7} | Chạm H=0.0                | Còn RAM: {len(open_set):<8}    |")
    else:
        print(f"| {'END':<10} | THẤT BẠI. DỪNG Ở G={current_node.g_cost:<7} | Mắc cạn tại H={best_overall_score:<11.1f} | Nổ RAM: Đã Mở {nodes_explored} Limit|")
        
    print("="*105)
    
    return current_node.state, path_actions, nodes_explored, time_taken_ms, status
