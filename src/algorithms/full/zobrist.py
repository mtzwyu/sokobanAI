import random

# ==============================================================================
# ZOBRIST HASHING - Mã hóa trạng thái game thành số nguyên O(1)
# ==============================================================================
# Nguyên lý: 
#   Gán cho mỗi (vị_trí, loại_vật_thể) một số ngẫu nhiên cố định.
#   Hash của toàn bộ trạng thái = XOR của tất cả các số ngẫu nhiên ứng với vật thể hiện có.
#
# Ưu điểm:
#   - Cập nhật hash khi đi 1 bước: O(1) chỉ cần XOR 2-4 số (thay vì tính lại từ đầu)
#   - Phân phối đều → Ít xung đột
#   - Dùng làm key cho Transposition Table
# ==============================================================================

ENTITY_BOX    = 0  # Thùng bình thường
ENTITY_PLAYER = 1  # Người chơi

class ZobristHasher:
    """
    Tạo và quản lý bảng Zobrist cho bản đồ Sokoban.
    Khởi tạo 1 lần và dùng mãi mãi cho cả màn.
    """
    def __init__(self, width, height, seed=42):
        rng = random.Random(seed)
        # zobrist_table[entity_type][x][y] = một số ngẫu nhiên 64-bit
        self.table = [
            [[rng.getrandbits(64) for _ in range(height)] for _ in range(width)]
            for _ in range(2)  # 0=BOX, 1=PLAYER
        ]
        self.width  = width
        self.height = height

    def hash_state(self, state):
        """
        Tính Zobrist hash đầy đủ từ một State.
        Dùng khi cần hash trạng thái ban đầu.
        """
        h = 0
        px, py = state.player_pos
        h ^= self.table[ENTITY_PLAYER][px][py]
        for bx, by in state.boxes:
            h ^= self.table[ENTITY_BOX][bx][by]
        return h

    def update_move(self, current_hash, old_player, new_player, moved_box=None, new_box_pos=None):
        """
        Cập nhật hash O(1) sau một bước đi:
        - XOR ra vị trí player cũ, XOR vào vị trí player mới
        - Nếu có đẩy thùng: XOR ra thùng cũ, XOR vào thùng mới
        """
        h = current_hash
        h ^= self.table[ENTITY_PLAYER][old_player[0]][old_player[1]]
        h ^= self.table[ENTITY_PLAYER][new_player[0]][new_player[1]]
        if moved_box is not None and new_box_pos is not None:
            h ^= self.table[ENTITY_BOX][moved_box[0]][moved_box[1]]
            h ^= self.table[ENTITY_BOX][new_box_pos[0]][new_box_pos[1]]
        return h
