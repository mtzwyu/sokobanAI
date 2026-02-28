from src.utils.constants import WALL, TARGET

class Grid:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.data = []

    def load_from_2d_array(self, grid_data):
        self.data = grid_data
        self.height = len(grid_data)
        self.width = len(grid_data[0]) if self.height > 0 else 0

    def is_wall(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x] == WALL
        return True # Coi ngoài rìa bản đồ là tường
        
    def is_target(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x] == TARGET
        return False
        
    def is_outside(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            from src.utils.constants import OUTSIDE
            return self.data[y][x] == OUTSIDE
        return True
