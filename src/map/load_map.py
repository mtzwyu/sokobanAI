import os
from src.utils.constants import WALL, TARGET, BOX, PLAYER, BOX_ON_TARGET, PLAYER_ON_TARGET, EMPTY, OUTSIDE

class MapExporter:
    @staticmethod
    def export(level, filepath="src/map/map.txt"):
        if not level or level.width == 0 or level.height == 0:
            return
        
        # Tính toán đường dẫn tuyệt đối cho map.txt dựa trên thư mục của tệp này
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(filepath):
            if filepath == "src/map/map.txt":
                filepath = os.path.join(current_dir, "map.txt")
            else:
                base_dir = os.path.dirname(current_dir)
                filepath = os.path.join(base_dir, filepath)
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        lines = []
        for y in range(level.height):
            row = []
            for x in range(level.width):
                char = EMPTY
                
                # Kiểm tra ô trên lưới (grid) định trước
                if level.grid.is_wall(x, y):
                    char = WALL
                elif level.grid.is_outside(x, y):
                    char = OUTSIDE
                elif level.grid.is_target(x, y):
                    char = TARGET
                    
                # Kiểm tra thực thể (hộp, người chơi) đè lên
                is_box = any(b.x == x and b.y == y for b in level.boxes)
                is_player = level.player and level.player.x == x and level.player.y == y
                
                if is_box:
                    char = BOX_ON_TARGET if char == TARGET else BOX
                elif is_player:
                    char = PLAYER_ON_TARGET if char == TARGET else PLAYER
                    
                row.append(char)
            lines.append("".join(row))
            
        with open(filepath, 'w') as f:
            for line in lines:
                f.write(line + "\n")
