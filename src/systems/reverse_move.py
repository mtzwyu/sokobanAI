# ==============================================================================
# HỆ THỐNG ĐẢO NGƯỢC DI CHUYỂN (REVERSE MOVE) - KÉO HỘP NGƯỢC LẠI
# ==============================================================================
# Khác với Undo (khôi phục snapshot), Reverse Move cho phép người chơi
# đi ngược lại và KÉO hộp theo mình (giống như tua ngược video).
# Hữu ích khi AI replay hoặc khi người chơi muốn thử lại một nhánh khác.
# ==============================================================================

class ReverseMove:
    """Hệ thống đảo ngược di chuyển.
    Lưu lại lịch sử từng bước (player pos, box pushed, direction)
    để có thể tua ngược chính xác từng action một.
    """
    
    def __init__(self):
        # Mỗi phần tử: (old_player_pos, pushed_box_index, dx, dy)
        # pushed_box_index = -1 nếu bước đó không đẩy hộp
        self.move_history = []
    
    def record_move(self, player, boxes, dx, dy, pushed_box=None):
        """Ghi lại một bước di chuyển vào lịch sử.
        
        Args:
            player: Đối tượng Player (trước khi di chuyển).
            boxes: Danh sách các hộp.
            dx, dy: Hướng di chuyển.
            pushed_box: Hộp bị đẩy (None nếu chỉ đi bộ).
        """
        box_index = -1
        if pushed_box is not None:
            for i, box in enumerate(boxes):
                if box is pushed_box:
                    box_index = i
                    break
        
        self.move_history.append({
            'old_player_x': player.x - dx,  # Vị trí TRƯỚC khi di chuyển
            'old_player_y': player.y - dy,
            'box_index': box_index,
            'dx': dx,
            'dy': dy,
        })
    
    def reverse(self, player, boxes, grid):
        """Đảo ngược bước di chuyển cuối cùng.
        
        - Người chơi lùi lại vị trí cũ.
        - Nếu bước đó có đẩy hộp, hộp cũng bị kéo ngược lại.
        
        Returns:
            bool: True nếu đảo ngược thành công, False nếu không có lịch sử.
        """
        if not self.move_history:
            return False
        
        record = self.move_history.pop()
        dx = record['dx']
        dy = record['dy']
        box_index = record['box_index']
        
        # Nếu bước này có đẩy hộp → kéo hộp ngược lại
        if box_index >= 0 and box_index < len(boxes):
            box = boxes[box_index]
            # Hộp lùi lại 1 ô (ngược hướng đẩy)
            box.move(-dx, -dy)
            box.update_target_state(grid.is_target(box.x, box.y))
        
        # Người chơi lùi lại vị trí cũ
        player.move(-dx, -dy)
        
        return True
    
    def clear(self):
        """Xóa toàn bộ lịch sử."""
        self.move_history.clear()
    
    def has_history(self):
        """Kiểm tra có lịch sử để đảo ngược không."""
        return len(self.move_history) > 0
    
    def get_step_count(self):
        """Trả về số bước đã ghi."""
        return len(self.move_history)
