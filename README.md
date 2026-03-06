# 🎮 SOKOBAN AI - Đồ Án Trí Tuệ Nhân Tạo

> Game giải đố Sokoban tích hợp **10 thuật toán AI** với giao diện đồ họa Pygame, hỗ trợ replay từng bước và phân tích heuristic thời gian thực.

---

## 📋 Mục Lục

- [Giới Thiệu](#giới-thiệu)
- [Tính Năng](#tính-năng)
- [Cài Đặt](#cài-đặt)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Thuật Toán AI](#thuật-toán-ai)
- [Hàm Heuristic](#hàm-heuristic)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)

---

## Giới Thiệu

**Sokoban** (倉庫番 - "Người quản kho") là trò chơi giải đố cổ điển trong đó người chơi đẩy các hộp vào đúng vị trí đích trên bản đồ lưới. Dự án này mở rộng Sokoban bằng cách tích hợp các thuật toán **Tìm kiếm Cục bộ (Local Search)** và **Tìm kiếm Toàn cục (Global Search)** từ lĩnh vực Trí Tuệ Nhân Tạo để tự động giải bài toán.

**Công nghệ sử dụng:**

- **Python 3.10+**
- **Pygame-CE** (Community Edition) — thư viện đồ họa game

---

## Tính Năng

| Tính năng | Mô tả |
|-----------|-------|
| 🎮 **Chơi thủ công** | Điều khiển nhân vật bằng phím mũi tên |
| 🤖 **10 thuật toán AI** | Tự động giải Sokoban bằng các thuật toán tìm kiếm |
| 🔄 **Replay từng bước** | Xem AI giải bài toán từng bước bằng phím Enter |
| 📊 **Heuristic thời gian thực** | In giá trị heuristic mỗi bước trên console |
| ⏪ **Reverse Move** | Tua ngược từng bước bằng phím Backspace |
| ↩️ **Undo (Ctrl+Z)** | Khôi phục trạng thái trước đó |
| 🗺️ **2 chế độ bản đồ** | Default (từ file) hoặc Random (sinh ngẫu nhiên) |
| 🔊 **Âm thanh & Nhạc nền** | Hiệu ứng di chuyển, đẩy hộp, thắng game |
| 🧱 **Phát hiện Deadlock** | 3 lớp bảo vệ: Static, Frozen, Corral |

---

## Cài Đặt

### Yêu cầu hệ thống

- Python >= 3.10
- pip (trình quản lý gói Python)

### Các bước cài đặt

```bash
# 1. Clone hoặc giải nén dự án
cd sokoban

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Chạy game
python main.py
```

---

## Hướng Dẫn Sử Dụng

### Menu Chính

| Phím | Chức năng |
|------|-----------|
| ↑ ↓ | Chọn mục menu |
| ← → | Thay đổi Mode / Số hộp |
| Enter | Xác nhận lựa chọn |

### Trong Game

| Phím | Chức năng |
|------|-----------|
| ↑ ↓ ← → | Di chuyển nhân vật |
| **Space** | Mở menu thuật toán AI |
| **Ctrl+Z** | Undo (khôi phục snapshot) |
| **Backspace** | Reverse Move (tua ngược từng bước, kéo hộp lùi) |
| **R** | Reset level |

### Menu Thuật Toán AI (sau khi nhấn Space)

| Phím | Thuật toán |
|------|-----------|
| **1** | Simple Hill Climbing |
| **2** | Steepest-Ascent Hill Climbing |
| **3** | Stochastic Hill Climbing |
| **4** | Random-Restart Hill Climbing |
| **5** | Simulated Annealing |
| **6** | Tabu Search |
| **7** | Local Beam Search |
| **8** | Stochastic Beam Search |
| **9** | Gradient Descent |
| **0** | IDA* Full Solver (Tìm đường ngắn nhất) |
| **ESC** | Thoát menu AI |

### Chế Độ Replay (sau khi AI giải thành công)

| Phím | Chức năng |
|------|-----------|
| **Enter** | Thực hiện 1 bước tiếp theo |
| **ESC** | Hủy replay, quay về chơi tự do |

---

## Thuật Toán AI

### Tìm Kiếm Cục Bộ (Local Search)

| # | Thuật toán | Đặc điểm |
|---|-----------|----------|
| 1 | **Simple Hill Climbing** | Chọn ngay hàng xóm tốt hơn đầu tiên |
| 2 | **Steepest-Ascent** | Chọn hàng xóm tốt nhất trong tất cả |
| 3 | **Stochastic Hill Climbing** | Chọn ngẫu nhiên trong các hàng xóm tốt hơn |
| 4 | **Random-Restart** | Lặp lại Stochastic nhiều lần từ đầu nếu kẹt |
| 5 | **Simulated Annealing** | Cho phép đi nước xấu với xác suất giảm dần |
| 6 | **Tabu Search** | Cấm lặp lại trạng thái đã đi qua (danh sách Tabu) |
| 7 | **Local Beam Search** | Duy trì K tia sáng song song |
| 8 | **Stochastic Beam Search** | Beam Search với xác suất chọn ngẫu nhiên |
| 9 | **Gradient Descent** | Tối ưu theo hướng gradient nhỏ nhất |

### Tìm Kiếm Toàn Cục (Global Search)

| # | Thuật toán | Đặc điểm |
|---|-----------|----------|
| 0 | **IDA\* Search** | Đảm bảo tìm đường bằng Iterative Deepening A* |

---

## Hàm Heuristic & Kỹ Thuật Tối Ưu

### Hệ Thống Tìm Kiếm Cục Bộ (Hill Climbing variants)

Công thức tổ hợp các yếu tố trong hàm Heuristic:

```
H(S) = Wt × H_Transport  +  Wa × H_Approach  +  Wp × H_Penalty  +  H_Unplaced
```

| Yếu tố | Ý nghĩa | Trọng số |
|---------|---------|----------|
| **H_Transport** | Chi phí vận chuyển (Ghép cặp tối ưu Thùng → Đích qua thuật toán Hungarian + BFS Distances) | Wt = 1.0 |
| **H_Approach** | Chi phí tiếp cận (Khoảng cách tính từ Player → Vị trí đẩy của thùng gần nhất) | Wa = 0.1 |
| **H_Penalty** | Điểm phạt Rủi ro (Dính chùm 2x2: +100, Sát tường đơn thuần: +10, Kẹt góc chết: ∞) | Wp = 1000.0 |
| **H_Unplaced** | Phạt thêm mỗi thùng KHÔNG ở đích (Tránh việc AI có xu hướng đẩy thùng đã vào đích ra ngoài lại) | +1000/thùng |

### Hệ Thống Tìm Kiếm Toàn Cục (IDA* Engine)

Để thuật toán IDA* đảm bảo luôn tìm được lời giải tối ưu (shortest path), hệ thống sử dụng Heuristic tổng hợp Admissible, trả về kết quả MAX để cắt được nhiều nhánh nhất có thể:

```
H(s) = max( Manhattan × 1.0,  Hungarian+BFS × 1.5,  Per-goal BFS × 2.0 )
```

---

## Hệ Thống Phát Hiện Deadlock (Cắt tỉa nhánh)

Tối ưu tốc độ duyệt cây tìm kiếm bằng cơ chế nhận diện mọi trạng thái bế tắc:

### Cho Hệ Thống Cục Bộ (Kiểm tra O(1) & Khối 2x2)

1. **Ô Tử Thần Tĩnh (Static Dead Zone)** — Tính trước 1 lần:
   - Góc tường chết (Corner Deadlock)
   - Vùng quét cạnh (Edge Deadlocks qua Reverse BFS)
2. **Khối Kẹt Vuông (Square 2x2 Deadlock)** — Phát hiện ngay lập tức 4 ô vuông kín tường/thùng (nhưng không chứa đích) sẽ không thể phá vỡ.

### Cho Máy Giải Toàn Cục IDA* (5 Lớp Nâng Cao)

_**Pha 1: Tĩnh (Tính 1 lần)**_

1. Góc tường chết (Corner Deadlock)
2. Hành lang cụt (Dead-end Corridors)
3. Vùng bị cô lập (Isolated Zones)

_**Pha 2: Động (Kiểm tra liên tục lúc Runtime)**_
4. Kẹt tương hỗ (Mutual Pair Deadlock) - 2 thùng kề nhau sát tường
5. Bị đóng băng (Freeze Deadlock) - Bị vây kín ≥ 3 mặt
6. Hành lang hẹp (Tunnel Deadlock) - Bị tắc trên đoạn hẹp 1 ô
7. Bị bủa vây (Corral Deadlock) - Dùng Flood Fill kiểm tra người chơi bị nhốt vòng trong thùng.

---

## Cấu Trúc Dự Án

```
sokoban/
├── main.py                    # Điểm khởi chạy
├── config.py                  # Cấu hình (FPS, kích thước màn hình)
├── requirements.txt           # Thư viện cần cài
├── README.md                  # Tài liệu hướng dẫn
│
├── assets/                    # Tài nguyên đồ họa & âm thanh
│   ├── sprites/               # Hình ảnh (tường, hộp, nhân vật, đích...)
│   └── sounds/                # Âm thanh (di chuyển, đẩy, thắng, nhạc nền)
│
└── src/                       # Mã nguồn chính
    ├── algorithms/            # Thuật toán AI
    │   ├── advanced/          # Nhóm thuật toán nâng cao
    │   │   ├── random_restart.py
    │   │   ├── simulated_annealing.py
    │   │   └── tabu_search.py
    │   ├── basic/             # Nhóm thuật toán leo đồi cơ bản (Hill Climbing)
    │   │   ├── simple_hill_climbing.py
    │   │   ├── steepest_ascent.py
    │   │   └── stochastic_hill_climbing.py
    │   ├── data_science/      # Tìm kiếm cực trị (Gradient)
    │   │   └── gradient_descent.py
    │   ├── full/              # Bộ giải toàn cầu (Global Solver)
    │   │   ├── ida_star.py             # IDA* Search (Thay thế A*)
    │   │   ├── deadlock_ida.py         # Phát hiện Deadlock chuyên sâu
    │   │   ├── heuristic_ida.py        # Heuristic Admissible
    │   │   ├── transposition_table.py  # Bộ nhớ đệm Transposition Table
    │   │   └── zobrist.py              # Zobrist Hashing
    │   ├── parallel/          # Các thuật toán kết hợp chùm (Beam Search)
    │   │   ├── local_beam_search.py
    │   │   └── stochastic_beam_search.py
    │   ├── heuristic.py       # Hàm đánh giá Heuristic (4 yếu tố)
    │   ├── deadlock.py        # Phát hiện Deadlock (3 lớp)
    │   └── solver_adapter.py  # Bộ chuyển đổi Level → State cho AI
    │
    ├── core/                  # Lõi game
    │   ├── game.py            # Vòng lặp chính, xử lý sự kiện, render
    │   ├── level.py           # Quản lý level (load, parse bản đồ)
    │   ├── level_generator.py # Sinh bản đồ ngẫu nhiên
    │   └── grid.py            # Lưới ô vuông (tường, sàn, đích)
    │
    ├── data/                  # Dữ liệu hằng
    │   └── random_config.py   # Cấu hình tính điểm Map động
    │
    ├── entities/              # Thực thể game
    │   ├── player.py          # Nhân vật người chơi
    │   └── box.py             # Hộp (thùng)
    │
    ├── systems/               # Hệ thống xử lý
    │   ├── movement.py        # Di chuyển với nội suy
    │   ├── undo.py            # Hệ thống Undo (snapshot bộ nhớ)
    │   ├── reverse_move.py    # Kéo ngược trạng thái hộp
    │   └── win_condition.py   # Kiểm tra điều kiện thắng
    │
    ├── ui/                    # Giao diện Đồ họa
    │   ├── menu.py            # Menu chính
    │   └── hud.py             # Thanh thông số game
    │
    ├── map/                   # Bản đồ
    │   └── load_map.py        # Tải map từ file văn bản (.txt)
    │
    └── utils/                 # Tiện ích hệ thống
        ├── constants.py       # Cấu hình trạng thái màu, độ lớn KH
        └── loader.py          # Nạp ảnh tĩnh và Cache Memory Game
```

### Ký Hiệu Bản Đồ

| Ký tự | Ý nghĩa |
|-------|---------|
| `#` | Tường |
| ` ` | Sàn trống |
| `$` | Hộp |
| `.` | Đích |
| `@` | Người chơi |
| `*` | Hộp trên đích |
| `+` | Người chơi trên đích |
| `-` | Ngoài bản đồ |

---

## 👨💻 Tác Giả

**Hà Mạnh Trường** — Đồ án môn **Trí Tuệ Nhân Tạo**

📧 Email: [mtruong2509@gmail.com](mailto:mtruong2509@gmail.com)

---
