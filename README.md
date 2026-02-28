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
| **0** | A* Search (Tìm đường ngắn nhất) |
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
| 0 | **A\* Search** | Đảm bảo tìm đường ngắn nhất (nếu tồn tại) |

---

## Hàm Heuristic

Công thức tổ hợp 4 yếu tố:

```
H_total = (W1 × H_Manhattan) + (W2 × H_Push) + (W3 × P_Deadlock) + (W4 × P_Goal)
```

| Yếu tố | Ý nghĩa | Trọng số |
|---------|---------|----------|
| **H_Manhattan** | Tổng khoảng cách Manhattan từ hộp → đích | W1 = 2.0 |
| **H_Push** | Khoảng cách người chơi → vị trí đẩy tối ưu | W2 = 0.5 |
| **P_Deadlock** | Phạt vô cực (∞) nếu rơi vào thế kẹt | W3 = ∞ |
| **P_Goal** | Thưởng khi hộp vào đích khó (góc/biên) | W4 = -1.5 |

### Phát Hiện Deadlock (3 lớp)

1. **Static Dead Zone** — Reverse BFS xác định vùng chết tĩnh (chạy 1 lần)
2. **Frozen Deadlock** — Phát hiện hộp bị đóng băng (kẹt 2 trục)
3. **Corral Deadlock** — Flood Fill kiểm tra người chơi bị nhốt

### Ưu Tiên Mục Tiêu (Goal Ordering)

- Đích trong **góc** (2 tường vuông góc) → priority **2.0**
- Đích trên **biên** bản đồ → priority **1.5**
- Đích **bình thường** → priority **1.0**

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
    │   ├── heuristic.py       # Hàm đánh giá Heuristic (4 yếu tố)
    │   ├── deadlock.py        # Phát hiện Deadlock (3 lớp)
    │   ├── solver_adapter.py  # Bộ chuyển đổi Level → State cho AI
    │   ├── simple_hill_climbing.py
    │   ├── steepest_ascent.py
    │   ├── stochastic_hill_climbing.py
    │   ├── random_restart.py
    │   ├── simulated_annealing.py
    │   ├── tabu_search.py
    │   ├── local_beam_search.py
    │   ├── stochastic_beam_search.py
    │   ├── gradient_descent.py
    │   └── nangcao/
    │       └── asao.py        # A* Search (Global Search)
    │
    ├── core/                  # Lõi game
    │   ├── game.py            # Vòng lặp chính, xử lý sự kiện, render
    │   ├── level.py           # Quản lý level (load, parse bản đồ)
    │   ├── level_generator.py # Sinh bản đồ ngẫu nhiên
    │   └── grid.py            # Lưới ô vuông (tường, sàn, đích)
    │
    ├── entities/              # Thực thể game
    │   ├── player.py          # Nhân vật người chơi
    │   └── box.py             # Hộp (thùng)
    │
    ├── systems/               # Hệ thống xử lý
    │   ├── movement.py        # Di chuyển & đẩy hộp
    │   ├── undo.py            # Hệ thống Undo (snapshot)
    │   ├── reverse_move.py    # Hệ thống Reverse Move (tua ngược)
    │   └── win_condition.py   # Kiểm tra điều kiện thắng
    │
    ├── ui/                    # Giao diện
    │   ├── menu.py            # Menu chính
    │   └── hud.py             # Thanh công cụ trong game
    │
    ├── map/                   # Bản đồ
    │   ├── map.txt            # Bản đồ hiện tại
    │   ├── map_default.txt    # Bản đồ mặc định
    │   └── load_map.py        # Export bản đồ ra file
    │
    └── utils/                 # Tiện ích
        ├── constants.py       # Hằng số (màu, hướng, ký tự bản đồ)
        └── loader.py          # Tải tài nguyên (ảnh, âm thanh)
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

## 👨‍💻 Tác Giả

**Hà Mạnh Trường** — Đồ án môn **Trí Tuệ Nhân Tạo**

📧 Email: [mtruong2509@gmail.com](mailto:mtruong2509@gmail.com)

---
