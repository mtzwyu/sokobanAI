# src/data/random_config.py

# QUẢN LÝ CẤU HÌNH & TÍNH ĐIỂM CHO BẢN ĐỒ SINH NGẪU NHIÊN (RANDOM MAP)
#
# Dùng để đánh giá độ khó, cũng như điều hướng bộ sinh bản đồ LevelGenerator
# tạo ra những thử thách phù hợp.

class DynamicMapConfig:
    """Cấu hình hằng số cho Random Map Generation"""
    
    # Kích thước khung hình tỷ lệ sinh (vd. 800x600 -> 4:3)
    ASPECT_RATIO_W = 4
    ASPECT_RATIO_H = 3
    
    # Các tham số kiểm soát Mật độ (Density) và Độ Rộng (Spaciousness)
    
    # Diện tích trống tối thiểu cần thiết cho mỗi hộp (để đảm bảo không bị quá chật)
    MIN_FREE_SPACE_PER_BOX = 15
    
    # Tỷ lệ chướng ngại vật (Obstacle Divisor). Số càng nhỏ -> Đá càng nhiều
    OBSTACLE_DENSITY_HARD = 40  # Nhiều đá (Khó)
    OBSTACLE_DENSITY_EASY = 60  # Ít đá (Dễ)
    
    # Xác suất sinh đá ở vùng ranh giới (Làm cho map bớt vuông vức, tự nhiên hơn)
    EDGE_ROUGHNESS_LAYER_1_PROB = 0.40  # Tầng 1 (sát tường ngoài)
    EDGE_ROUGHNESS_LAYER_2_PROB = 0.10  # Tầng 2 (vào trong 1 ô)
    
    # Các thông số về Độ Sâu (Depth) của Bài toán (Walk rẽ nhánh)
    
    # Số bước đi lùi tối đa (Reverse Random Walk) mỗi thùng để trộn bản đồ.
    # Càng nhiều bước đi lùi -> Thùng và đích càng xa nhau -> Càng khó.
    WALK_BASE_MULTIPLIER = 800
    
    # Số bước tăng thêm mỗi lần Generate bị thất bại (tránh map quá dễ sinh tiếp loop)
    WALK_PENALTY_INCREMENT = 200

def evaluate_map_difficulty(width, height, num_boxes, boxes_off_target):
    """
    Hàm tham khảo để tính điểm (Score/Difficulty Rating) của Map vừa sinh ra.
    Dựa trên diện tích, mật độ khối và khoảng cách kéo hộp.
    """
    area = width * height
    density = num_boxes / max(1, area)
    
    difficulty_score = (num_boxes * 10) + (boxes_off_target * 5) + (density * 1000)
    
    if difficulty_score < 50:
        return "EASY"
    elif difficulty_score < 100:
        return "MEDIUM"
    else:
        return "HARD"
