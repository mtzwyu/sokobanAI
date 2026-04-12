# 🎮 Sokoban AI — Trí Tuệ Nhân Tạo Giải Quyết Bài Toán Sokoban

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame--CE-2.3.2%2B-00B140?style=for-the-badge&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.11%2B-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Đồ án Trí Tuệ Nhân Tạo — Ứng dụng các thuật toán Leo Đồi (Hill Climbing) để giải bài toán Sokoban cổ điển.**

</div>

---

## 📋 Mục Lục

- [Giới Thiệu](#-giới-thiệu)
- [Tính Năng](#-tính-năng)
- [Kiến Trúc Hệ Thống](#-kiến-trúc-hệ-thống)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Các Thuật Toán AI](#-các-thuật-toán-ai)
- [Hàm Heuristic](#-hàm-heuristic)
- [Cài Đặt](#-cài-đặt)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Đánh Giá Thuật Toán](#-đánh-giá-thuật-toán)
- [Điều Khiển Game](#-điều-khiển-game)
- [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)

---

## 🧩 Giới Thiệu

**Sokoban** (倉庫番) là bài toán tối ưu hóa tổ hợp (combinatorial optimization) thuộc lớp PSPACE-complete, trong đó người chơi phải đẩy các hộp (`$`) vào đúng các vị trí đích (`.`) trên bản đồ lưới 2D.

Dự án này xây dựng một **hệ thống AI hoàn chỉnh** bao gồm:

- **Game engine** viết bằng `pygame-ce` với đồ họa sprite đầy đủ.
- **7 thuật toán tìm kiếm cục bộ (Local Search)** thuộc họ Hill Climbing.
- **Hàm Heuristic đa thành phần** dựa trên thuật toán Hungarian (phân công tối ưu) kết hợp BFS thực tế.
- **Chế độ AI Debug**: trực quan hoá từng bước phân tích heuristic theo thời gian thực.
- **AI Auto-Drive**: hệ thống tự động chọn thuật toán tốt nhất và tự chơi.
- **Xuất kết quả Excel** để so sánh hiệu suất 7 thuật toán một cách hệ thống.

---

## ✨ Tính Năng

| Tính Năng | Mô Tả |
|---|---|
| 🎮 **Game Engine** | Đồ họa sprite, âm thanh, animation, HUD đầy đủ |
| 🖥️ **Responsive UI** | Tính năng tự động Scale toàn bộ Map và các Menu vừa theo mọi kích thước khung hình tuỳ ý của sổ |
| 🎨 **Card UI Design** | Hệ thống UI (Main Menu, AI Menu, Win Screen) được thiết kế hiện đại với hiệu ứng shadow, pulse phát sáng tiếng Việt |
| 🤖 **7 Thuật Toán AI** | Từ Simple Hill Climbing cơ bản đến Random Restart nâng cao |
| 🧠 **Heuristic Thông Minh** | Hungarian Algorithm + BFS đa nguồn + kiểm tra Deadlock |
| 🔍 **AI Debug Mode** | Cửa sổ phân tích heuristic real-time (Tkinter overlay) |
| 🚗 **AI Auto-Drive** | Tự động chọn thuật toán tốt nhất, tự chơi với animation |
| 📊 **Xuất Excel** | So sánh chi tiết từng bước, từng thuật toán với màu sắc |
| 🗺️ **Level Generator** | Tự sinh màn chơi ngẫu nhiên theo số hộp tùy chọn |
| ↩️ **Undo/Reverse** | Hoàn tác nhiều bước & kéo hộp ngược lại |
| 🔇 **Âm Thanh** | Nhạc nền, hiệu ứng move/push/win, tắt/bật tự do |

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                    GAME ENGINE (Pygame)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │  Menu    │  │  Level   │  │   HUD    │  │ Sound  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
├─────────────────────────────────────────────────────────┤
│                    SYSTEMS LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Movement  │  │   Undo   │  │Reverse   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
├─────────────────────────────────────────────────────────┤
│                    AI / ALGORITHMS                       │
│  ┌──────────────────┐  ┌────────────────────────────┐   │
│  │  SolverAdapter   │  │     Heuristic Engine       │   │
│  │  (State Bridge)  │  │  Hungarian + BFS + Deadlock│   │
│  └──────────────────┘  └────────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Basic   │  │Stochastic│  │   Escape Maxima       │  │
│  │  Search  │  │  Search  │  │ (Backtrack/Jump/Restart)│  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc Dự Án

```
sokoban/
│
├── main.py                         # Điểm khởi chạy game
├── config.py                       # Cấu hình màn hình, FPS
├── evaluate_algorithms.py          # Script chạy & so sánh 7 thuật toán → Excel
├── requirements.txt                # Dependencies
├── Kq_Thuật_toán_AI_Bảng.xlsx     # Kết quả đánh giá (tự động sinh)
│
├── assets/
│   ├── sprites/                    # Hình ảnh: wall, floor, box, player, target
│   └── sounds/                     # Âm thanh: Soundtrack.wav, move, push, win
│
└── src/
    ├── core/
    │   ├── game.py                 # Game loop chính, AI Debug HUD, Auto-Drive
    │   ├── level.py                # Quản lý màn chơi (load/parse)
    │   ├── level_generator.py      # Sinh màn chơi ngẫu nhiên
    │   └── grid.py                 # Grid utilities (wall/outside/target check)
    │
    ├── algorithms/
    │   ├── heuristic.py            # Hàm H(S): H1+H2+H3+H4+H5+Push Bonus
    │   ├── deadlock.py             # Phát hiện Deadlock (góc chết, 2×2)
    │   ├── solver_adapter.py       # Cầu nối Level → AI State/Neighbors
    │   │
    │   ├── basic_search/
    │   │   ├── simple_hill_climbing.py     # Leo đồi đơn giản (first-better)
    │   │   └── steepest_ascent.py          # Leo đồi dốc nhất (best-of-all)
    │   │
    │   ├── stochastic_search/
    │   │   ├── stochastic_hc.py            # Leo đồi ngẫu nhiên (random neighbor)
    │   │   └── first_choice_hc.py          # First-choice Hill Climbing
    │   │
    │   └── escape_maxima/
    │       ├── backtracking_hc.py          # Backtracking với bộ nhớ
    │       ├── jumping_hc.py               # Nhảy ngẫu nhiên thoát cực trị
    │       └── random_restart_hc.py        # Khởi động lại ngẫu nhiên
    │
    ├── entities/                   # Player, Box (sprite + animation)
    ├── systems/
    │   ├── movement.py             # Xử lý di chuyển player + push box
    │   ├── undo.py                 # Hoàn tác bước đi (Ctrl+Z)
    │   ├── reverse_move.py         # Kéo hộp ngược lại (Backspace)
    │   └── win_condition.py        # Kiểm tra thắng
    │
    ├── ui/
    │   ├── menu.py                 # Main Menu (Card UI giao diện chọn chế độ)
    │   ├── ai_menu.py              # Menu AI điều khiển phân tích & Auto-Drive
    │   ├── win_screen.py           # Màn hình chiến thắng có Navigation UI
    │   └── hud.py                  # HUD trong game (Home, Reset, Menu, Sound)
    │
    ├── map/
    │   ├── map.txt                 # Bản đồ dạng text (ký tự)
    │   ├── map_default.xlsx        # Bản đồ mặc định dạng Excel
    │   └── load_map.py             # MapExporter: đọc/ghi state ra Excel
    │
    ├── data/                       # Dữ liệu trạng thái game
    └── utils/
        ├── constants.py            # Hằng số màu sắc, hướng di chuyển
        └── loader.py               # AssetLoader (sprite, sound)
```

---

## 🤖 Các Thuật Toán AI

Dự án triển khai **7 biến thể thuật toán tìm kiếm cục bộ** theo phân loại học thuật:

### 🔷 Nhóm 1: Basic Search (Tìm kiếm cơ bản)

| Thuật Toán | File | Mô Tả |
|---|---|---|
| **Simple Hill Climbing** | `simple_hill_climbing.py` | Duyệt tuần tự hàng xóm, di chuyển ngay khi tìm thấy hàng xóm **đầu tiên** tốt hơn (first-better). Dừng khi không còn hàng xóm tốt hơn. |
| **Steepest Ascent HC** | `steepest_ascent.py` | Đánh giá **toàn bộ** hàng xóm, chọn hàng xóm **tốt nhất** để di chuyển. Chính xác hơn nhưng tốn tài nguyên hơn. |

### 🔶 Nhóm 2: Stochastic Search (Tìm kiếm ngẫu nhiên)

| Thuật Toán | File | Mô Tả |
|---|---|---|
| **Stochastic HC** | `stochastic_hc.py` | Chọn **ngẫu nhiên** trong số các hàng xóm tốt hơn, giúp thoát khỏi các local minima đơn giản. |
| **First Choice HC** | `first_choice_hc.py` | Sinh hàng xóm ngẫu nhiên đến khi tìm được hàng xóm cải thiện. Hiệu quả khi không gian hàng xóm rộng. |

### 🔴 Nhóm 3: Escape Maxima (Thoát cực trị cục bộ)

| Thuật Toán | File | Mô Tả |
|---|---|---|
| **Backtracking HC** | `backtracking_hc.py` | Ghi nhớ trạng thái đã thăm, quay lui khi gặp local minima. |
| **Jumping HC** | `jumping_hc.py` | Thực hiện **5–15 bước ngẫu nhiên** để "nhảy" ra khỏi vùng local minima. |
| **Random Restart HC** | `random_restart_hc.py` | Khởi động lại từ điểm ngẫu nhiên (nhiễu **3–10 bước** từ trạng thái ban đầu) khi bị kẹt. |

---

## 🧠 Hàm Heuristic

Hàm đánh giá trạng thái `H(S)` là **đa thành phần**, được thiết kế đặc biệt cho Sokoban:

```
H(S) = Wt × H1 + Wa × H2 + Wp × H3 + H4 + Wb × H5 − W_push × [push_bonus]
```

| Thành Phần | Tên | Mô Tả | Trọng Số |
|---|---|---|---|
| **H1** | Transport Cost | Chi phí vận chuyển tối ưu: **Hungarian Algorithm** phân công Hộp→Đích + **BFS đa nguồn** để tính khoảng cách thực tế né tường | `Wt = 1.0` |
| **H2** | Accessibility Cost | Chi phí tiếp cận: **BFS từ Player** đến vị trí đẩy tốt nhất (push position), có Euclidean tie-breaker | `Wa = 0.5` |
| **H3** | Penalty Score | Điểm phạt rủi ro: `∞` (góc chết), `+100` (khối 2×2), `+10` (sát tường) | `Wp = 1000.0` |
| **H4** | Unplaced Penalty | Phạt mỗi hộp chưa vào đích (bảo vệ hộp đã an toàn) | `W_done = 1000.0` |
| **H5** | Push Direction | BFS đến push_pos + Euclidean tie-breaker: tạo gradient theo hướng đẩy đúng | `Wb = 0.05` |
| **Push Bonus** | Box Move Bonus | Thưởng `-0.5` khi nước đi là **đẩy hộp** (phá tie khi H bằng nhau) | `W_push = 0.5` |

> **Nguyên tắc thiết kế:** `H(S) = 0` ↔ giải quyết xong. `H(S) = ∞` ↔ deadlock tuyệt đối.

### Phát hiện Deadlock (`deadlock.py`)

- **Góc chết tĩnh (Static Dead Zone)**: Tiền tính trước các ô mà hộp không thể thoát ra.
- **Khối 2×2 động (Dynamic 2×2)**: Phát hiện 4 ô liên thành khối vuông đều là hộp/tường → deadlock ngay.

---

## 🛠️ Cài Đặt

### Yêu Cầu

- **Python 3.10+**
- **pip** (hoặc môi trường ảo `venv`)

### Bước 1: Clone dự án

```bash
git clone https://github.com/<your-username>/sokoban.git
cd sokoban
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

> **Lưu ý:** Script đánh giá `evaluate_algorithms.py` cần thêm `openpyxl` và `pandas`:
>
> ```bash
> pip install openpyxl pandas
> ```

### Bước 4: Chạy game

```bash
python main.py
```

---

## 🎮 Hướng Dẫn Sử Dụng

### Chế Độ Chơi

Sau khi vào game, **Main Menu** cho phép:

- **Default Map**: Chơi bản đồ cố định (`map_default.xlsx`).
- **Random Map**: Tự sinh màn chơi ngẫu nhiên (chọn số hộp từ 1–20).

### Chế Độ AI (Nhấn `SPACE` trong khi chơi)

Menu AI xuất hiện với 3 tùy chọn:

```
╔═══════════════════════════════════════════════╗
║         HỆ THỐNG AI CHO SOKOBAN               ║
║                                               ║
║  [1] Phân tích Heuristic (Simple Hill Climbing)║
║  [2] Chạy 7 Thuật toán & Tự Lái (Auto Drive)  ║
║  [3] Hủy Tự Lái & Tắt tia Laser               ║
║  [SPACE/ESC] Đóng menu                        ║
╚═══════════════════════════════════════════════╝
```

#### `[1]` — Chế Độ AI Debug (Heuristic Analysis)

- Mở cửa sổ **Tkinter** hiển thị real-time:
  - H hiện tại của trạng thái
  - H của 4 hướng di chuyển (LÊN/XUỐNG/TRÁI/PHẢI)
  - Phân tách H1 (vận chuyển), H2 (tiếp cận), H3 (phạt rủi ro)
  - Đánh dấu hướng **TỐI ƯU** (Simple HC sẽ chọn hướng nào)
- Vẽ **mũi tên màu** trên bản đồ:
  - 🟢 **Xanh** = hướng tối ưu (H giảm)
  - 🔴 **Đỏ** = hướng không tối ưu

#### `[2]` — AI Auto-Drive

- Chạy **7 thuật toán** song song (ngầm).
- Xuất kết quả chi tiết ra file **`Kq_Thuật_toán_AI_Bảng.xlsx`**.
- Tự động chọn thuật toán có `H(end)` thấp nhất và ít bước nhất.
- Game tự **chơi** từng bước với tốc độ 150ms/bước.

#### `[3]` — Hủy AI

- Dừng ngay chế độ tự lái và tắt overlay debug.

---

## 📊 Đánh Giá Thuật Toán

Chạy đánh giá độc lập (không cần mở game):

```bash
python evaluate_algorithms.py
```

### Kết Quả Xuất Ra (`Kq_Thuật_toán_AI_Bảng.xlsx`)

File Excel được định dạng tự động với màu sắc:

| Cột | Nội Dung |
|---|---|
| Bước thứ | Số thứ tự bước đi (0 = khởi đầu) |
| Hành động | LÊN / XUỐNG / TRÁI / PHẢI |
| Heuristic | Giá trị H(S) tại mỗi bước |

- 🟦 **Header** xanh dương (tên thuật toán + thời gian chạy)
- ✅ **Kết luận xanh**: Thuật toán thành công (H=0)
- ❌ **Kết luận đỏ**: Thuật toán bị kẹt local minima

### Tiêu Chí So Sánh

```
Ưu tiên 1: H(end) thấp nhất
Ưu tiên 2: Số bước ít nhất (nếu H(end) bằng nhau)
```

---

## ⌨️ Điều Khiển Game

| Phím | Chức Năng |
|---|---|
| `↑ ↓ ← →` | Di chuyển nhân vật |
| `SPACE` | Mở menu AI |
| `Ctrl + Z` | Hoàn tác bước đi (Undo) |
| `Backspace` | Kéo hộp ngược lại (Reverse Move) |
| `R` | Khởi động lại màn hiện tại |
| `3` | Hủy AI Auto-Drive ngay lập tức |
| Click 🏠 | Về Main Menu |
| Click 🔄 | Reset màn chơi |
| Click 🔇/🔊 | Bật/Tắt âm thanh |

---

## 🖥️ Yêu Cầu Hệ Thống

| Thành Phần | Yêu Cầu Tối Thiểu |
|---|---|
| **OS** | Windows 10, macOS 10.14, Ubuntu 20.04 trở lên |
| **Python** | 3.10+ |
| **RAM** | 512 MB |
| **Màn hình** | 1024 × 768 trở lên |
| **GPU** | Không yêu cầu (CPU rendering) |

### Dependencies (`requirements.txt`)

```
pygame-ce>=2.3.2    # Game engine (Community Edition - nhanh hơn pygame gốc)
numpy>=1.26.0       # Ma trận chi phí cho Hungarian Algorithm
scipy>=1.11.0       # linear_sum_assignment (Hungarian Algorithm)
```

---

## 📚 Tài Liệu Tham Khảo

- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Chapter 4: Search in Complex Environments.
- Hungarian Algorithm: Kuhn, H. W. (1955). *The Hungarian method for the assignment problem*. Naval Research Logistics Quarterly, 2(1–2), 83–97.
- SciPy `linear_sum_assignment`: [scipy.optimize.linear_sum_assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)

---

## 👨‍💻 Tác Giả

Dự án được thực hiện trong khuôn khổ **môn học Trí Tuệ Nhân Tạo**, tập trung vào việc so sánh thực nghiệm các thuật toán tìm kiếm cục bộ trên bài toán Sokoban — một bài toán benchmark kinh điển trong AI.

---

<div align="center">

**Made with ❤️ using Python & Pygame**

</div>
