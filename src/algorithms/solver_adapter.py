from src.utils.constants import UP, DOWN, LEFT, RIGHT

class State:
    def __init__(self, player_pos, boxes):
        self.player_pos = player_pos
        self.boxes = frozenset(boxes)
        self._hash = hash((self.player_pos, self.boxes))

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.player_pos == other.player_pos and self.boxes == other.boxes

    def __hash__(self):
        return self._hash

class SolverAdapter:
    def __init__(self, level):
        self.level = level
        self.grid = level.grid
        
    def get_initial_state(self):
        player_pos = (self.level.player.x, self.level.player.y)
        boxes = [(b.x, b.y) for b in self.level.boxes]
        return State(player_pos, boxes)
        
    def get_targets(self):
        targets = []
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.is_target(x, y):
                    targets.append((x, y))
        return targets

    def _is_wall(self, x, y):
        return self.grid.is_wall(x, y)

    def get_neighbors(self, state):
        neighbors = []
        px, py = state.player_pos
        directions = [UP, DOWN, LEFT, RIGHT]
        
        for dx, dy in directions:
            nx, ny = px + dx, py + dy
            
            if self._is_wall(nx, ny):
                continue
                
            if (nx, ny) in state.boxes:
                nnx, nny = nx + dx, ny + dy
                if self._is_wall(nnx, nny) or (nnx, nny) in state.boxes:
                    continue
                new_boxes = set(state.boxes)
                new_boxes.remove((nx, ny))
                new_boxes.add((nnx, nny))
                neighbors.append(State((nx, ny), new_boxes))
            else:
                neighbors.append(State((nx, ny), state.boxes))
                
        return neighbors

    def get_heuristic_func(self):
        targets = self.get_targets()
        
        # Tiền xử lý (Pre-calculate) Vùng Chết (O(1) Check)
        from src.algorithms.deadlock import build_dead_zones
        dead_zones = build_dead_zones(self.grid, targets)
        
        # Load hàm Heuristic kết hợp Check Deadlock Siêu chuẩn
        from src.algorithms.heuristic import calculate_heuristic
        
        def heuristic(state):
            return calculate_heuristic(state, targets, self.grid, dead_zones)
            
        return heuristic
