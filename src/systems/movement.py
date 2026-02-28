class MovementSystem:
    def __init__(self, grid, player, boxes, undo_system):
        self.grid = grid
        self.player = player
        self.boxes = boxes
        self.undo_system = undo_system

    def move(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if self.grid.is_wall(new_x, new_y):
            return False, False

        box_to_push = None
        for box in self.boxes:
            if box.x == new_x and box.y == new_y:
                box_to_push = box
                break

        if box_to_push:
            box_new_x = box_to_push.x + dx
            box_new_y = box_to_push.y + dy

            if self.grid.is_wall(box_new_x, box_new_y):
                return False, False

            for other_box in self.boxes:
                if other_box.x == box_new_x and other_box.y == box_new_y:
                    return False, False

            self.undo_system.save_state(self.player, self.boxes)

            box_to_push.move(dx, dy)
            box_to_push.update_target_state(self.grid.is_target(box_to_push.x, box_to_push.y))
            self.player.move(dx, dy)
            return True, True
        else:
            self.undo_system.save_state(self.player, self.boxes)
            self.player.move(dx, dy)
            return True, False
