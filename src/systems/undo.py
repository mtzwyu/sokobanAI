class UndoSystem:
    def __init__(self):
        self.history = []

    def save_state(self, player, boxes):
        state = {
            'player': (player.x, player.y),
            'boxes': [(box.x, box.y, box.is_on_target) for box in boxes]
        }
        self.history.append(state)

    def undo(self, player, boxes):
        if not self.history:
            return False
            
        state = self.history.pop()
        player.x, player.y = state['player']
        
        for i, box_state in enumerate(state['boxes']):
            boxes[i].x = box_state[0]
            boxes[i].y = box_state[1]
            boxes[i].is_on_target = box_state[2]
            
        return True
