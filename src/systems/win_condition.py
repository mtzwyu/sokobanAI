class WinCondition:
    def __init__(self, grid, boxes):
        self.grid = grid
        self.boxes = boxes

    def check_win(self):
        if not self.boxes:
            return False
            
        for box in self.boxes:
            if not self.grid.is_target(box.x, box.y):
                return False
        return True
