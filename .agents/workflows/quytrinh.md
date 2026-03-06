---
description:  QUY TRÌNH TỔNG THỂ (FLOWCHART DẠNG TEXT)
---

START
  │
  ├─► PHA 1: TIỀN XỬ LÝ
  │     ├─► Đọc map, xác định tường/đích
  │     ├─► Tạo static deadlock map
  │     ├─► Tính khoảng cách Manhattan
  │     └─► Xây dựng Pattern Databases
  │
  ├─► PHA 2: TÌM KIẾM CHÍNH (IDA*)
  │     │
  │     ├─► depth = 1
  │     │
  │     ├─► WHILE chưa tìm thấy lời giải:
  │     │     │
  │     │     ├─► Gọi DFS với depth hiện tại
  │     │     │     │
  │     │     │     ├─► Kiểm tra deadlock (tĩnh + động)
  │     │     │     ├─► Nếu deadlock → backtrack
  │     │     │     │
  │     │     │     ├─► Tính heuristic tổng hợp
  │     │     │     ├─► Nếu f > depth → cắt tỉa
  │     │     │     │
  │     │     │     ├─► Sắp xếp nước đi theo ưu tiên
  │     │     │     ├─► Thử từng nước đi
  │     │     │     │     │
  │     │     │     │     ├─► Cập nhật transposition table
  │     │     │     │     ├─► Đệ quy tìm tiếp
  │     │     │     │     └─► Nếu tìm thấy → trả về
  │     │     │     │
  │     │     │     └─► Hết nước đi → backtrack
  │     │     │
  │     │     └─► depth += 5
  │     │
  │     └─► Tìm thấy lời giải thô
  │
  ├─► PHA 3: TỐI ƯU HÓA
  │     ├─► Loại bỏ bước thừa
  │     ├─► Phát hiện và cắt chu trình
  │     └─► Tối ưu đường đi người chơi
  │
  └─► OUTPUT: Lời giải tối ưu (số bước tối thiểu)
        │
        └─► END