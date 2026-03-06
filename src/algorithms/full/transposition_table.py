# ==============================================================================
# TRANSPOSITION TABLE - Bảng cache trạng thái đã duyệt
# ==============================================================================
# Nguyên lý:
#   Khi IDA* duyệt đến một trạng thái đã gặp trước đó với chi phí ít hơn hoặc bằng,
#   cắt nhánh ngay (Pruning) để tiết kiệm thời gian.
#
# Cấu trúc mỗi entry:
#   { hash → (g_cost, flag) }
#   - g_cost: số bước đi từ trạng thái đầu đến trạng thái này
#   - flag:   'EXACT' | 'LOWER_BOUND' | 'UPPER_BOUND'
# ==============================================================================

EXACT       = 'EXACT'
LOWER_BOUND = 'LOWER_BOUND'
UPPER_BOUND = 'UPPER_BOUND'

class TranspositionTable:
    """
    Bảng lưu trữ trạng thái đã duyệt trong IDA*.
    Key = Zobrist hash (64-bit int)
    Value = (g_cost, flag)
    """
    def __init__(self, max_size=2_000_000):
        self._table = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def lookup(self, state_hash):
        """
        Tra cứu trạng thái. Trả về (g_cost, flag) hoặc None nếu không có.
        """
        entry = self._table.get(state_hash)
        if entry is not None:
            self.hits += 1
            return entry
        self.misses += 1
        return None

    def store(self, state_hash, g_cost, flag=EXACT):
        """
        Lưu hoặc cập nhật entry. Nếu entry cũ có g_cost tốt hơn → giữ nguyên.
        """
        existing = self._table.get(state_hash)
        if existing is None or g_cost <= existing[0]:
            # Giới hạn kích thước bảng để tránh tràn RAM
            if len(self._table) >= self.max_size:
                # Đơn giản: xóa một phần bảng (LRU-light)
                keys_to_delete = list(self._table.keys())[:self.max_size // 4]
                for k in keys_to_delete:
                    del self._table[k]
            self._table[state_hash] = (g_cost, flag)

    def clear(self):
        """Xóa sạch bảng cho màn chơi mới."""
        self._table.clear()
        self.hits = 0
        self.misses = 0

    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size':     len(self._table),
            'hits':     self.hits,
            'misses':   self.misses,
            'hit_rate': f'{hit_rate:.1f}%'
        }
