import copy
from src.utils.constants import UP, DOWN, LEFT, RIGHT

class State:
    def __init__(self, player_pos, boxes):
        self.player_pos = player_pos
        self.boxes = tuple(sorted(boxes))  # Tupled and sorted for hashing

    def __eq__(self, other):
        return self.player_pos == other.player_pos and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.player_pos, self.boxes))

class SolverAdapter:
    def __init__(self, level):
        self.grid = level.grid
        
        # Initial extraction
        self.initial_player = None
        self.initial_boxes = []
        self.targets = set()
        
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.is_target(x, y):
                    self.targets.add((x, y))

        if level.player:
            self.initial_player = (level.player.x, level.player.y)
        for b in level.boxes:
            self.initial_boxes.append((b.x, b.y))

        # Cache dist_maps 1 lần duy nhất khi khởi tạo
        # (BFS từ từng đích — tốn kém khi gọi lại nhiều lần trong SA)
        from src.algorithms.heuristic import build_dist_maps
        self.dist_maps = build_dist_maps(self.grid, self.targets)

    def get_initial_state(self):
        return State(self.initial_player, self.initial_boxes)

    def get_targets(self):
        return self.targets

    def get_neighbors(self, state):
        neighbors = []
        moves = [
            (UP, "LÊN"),
            (DOWN, "XUỐNG"),
            (LEFT, "TRÁI"),
            (RIGHT, "PHẢI")
        ]

        px, py = state.player_pos

        for (dx, dy), action_name in moves:
            nx, ny = px + dx, py + dy

            # Check wall
            if self.grid.is_wall(nx, ny) or self.grid.is_outside(nx, ny):
                continue

            # Check box push
            if (nx, ny) in state.boxes:
                # Need to push the box
                bx, by = nx + dx, ny + dy
                
                # Cannot push into wall or another box
                if self.grid.is_wall(bx, by) or self.grid.is_outside(bx, by) or (bx, by) in state.boxes:
                    continue
                
                # Valid push
                new_boxes = list(state.boxes)
                new_boxes.remove((nx, ny))
                new_boxes.append((bx, by))
                
                new_state = State((nx, ny), new_boxes)
                neighbors.append((action_name, new_state))
            else:
                # Simple move
                new_state = State((nx, ny), state.boxes)
                neighbors.append((action_name, new_state))

        return neighbors

    def get_heuristic_func(self):
        from src.algorithms.heuristic import calculate_heuristic
        dist_maps = self.dist_maps  # Dùng bản đã cache
        
        def h(state, prev_boxes=None):
            score, _, _, _ = calculate_heuristic(
                state, self.targets, self.grid,
                dist_maps=dist_maps, prev_boxes=prev_boxes
            )
            return score
            
        return h

    def get_detailed_heuristic_func(self):
        from src.algorithms.heuristic import calculate_heuristic
        dist_maps = self.dist_maps  # Dùng bản đã cache
        
        def h_detail(state, prev_boxes=None):
            score, h1, h2, h3 = calculate_heuristic(
                state, self.targets, self.grid,
                dist_maps=dist_maps, prev_boxes=prev_boxes
            )
            return score, h1, h2, h3
            
        return h_detail
