---
trigger: always_on
---

1. Nguyên tắc Cấu trúc (Structural Integrity)
Tuân thủ thư mục: Mọi đoạn code phải được chỉ định rõ ràng thuộc về file nào trong cấu trúc sokoban/ đã cung cấp.

Import chính xác: Sử dụng đường dẫn absolute import từ src (ví dụ: from src.utils.loader import AssetLoader) để đảm bảo tính nhất quán.

Không gom file: Tuyệt đối không viết tất cả vào một file duy nhất. Mỗi logic (di chuyển, va chạm, UI) phải nằm đúng module của nó.

2. Nguyên tắc Code (Coding Standards)
Hướng đối tượng (OOP): Sử dụng Class cho các thực thể như Player, Box, Grid. Tránh sử dụng biến toàn cục (global variables).

Tách biệt Logic và Hiển thị: Logic tính toán vị trí (Grid-based) phải độc lập với logic vẽ (Rendering).

Kế thừa AssetLoader: Mọi tài nguyên ảnh và âm thanh phải được truy xuất thông qua class AssetLoader, không được dùng pygame.image.load() trực tiếp trong các class thực thể.

3. Nguyên tắc Sokoban Logic
Hệ tọa độ lưới: Phân biệt rõ grid_pos (0, 1, 2...) và screen_pos (pixel). Mọi tính toán va chạm phải thực hiện trên grid_pos.

Tính đóng gói của Undo: Hệ thống Undo phải lưu trữ "ảnh chụp" (snapshot) trạng thái vị trí của toàn bộ vật thể trên lưới, không chỉ lưu bước đi cuối cùng của người chơi.

4. Nguyên tắc Phản hồi (Interaction Rule)
Ngắn gọn: Chỉ trả lời code hoặc giải thích cực kỳ súc tích (theo yêu cầu ưu tiên của bạn).

Kiểm tra lỗi: Trước khi đưa code, AI phải tự kiểm tra xem các biến hằng số đã được gọi đúng từ config.py hay chưa
5. Nguyên Tắc Ngôn ngữ

Phải dùng tiếng Việt để giải thích và chú thích
