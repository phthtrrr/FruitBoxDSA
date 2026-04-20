# 🍎 Fruit Box DSA 
Đồ án môn Cấu trúc Dữ liệu và Giải thuật - Game Fruit Box
Dự án là một tựa game giải đố (Puzzle Game) được làm mô phỏng lại dựa trên game Fruit Box cùng tên của gamesaien xây dựng bằng Python và Pygame, tập trung vào việc áp dụng các kỹ thuật tối ưu hóa và cấu trúc dữ liệu.

## 🚀 Các Cấu trúc Dữ liệu & Giải thuật nổi bật
* **2D Array (Mảng 2 chiều):** Lưu trữ và quản lý không gian tọa độ dạng lưới (Grid-based).
* **2D Prefix Sum (Mảng cộng dồn 2 chiều):** Tối ưu hóa truy vấn tính tổng vùng chọn (Bounding Box) từ độ phức tạp `O(W x H)` xuống mức tuyệt đối `O(1)`.

## 🛠 Yêu cầu hệ thống
* Python 3. trở lên
* Pygame `pip install pygame`

## 🎮 Cách chơi
* Sử dụng chuột trái kéo và tạo thành một vùng chọn hình chữ nhật.
* Nếu tổng các con số bên trong vùng chọn **bằng chính xác 10**, các quả táo sẽ được triệt tiêu và ứng với mỗi quả táo bạn sẽ nhận 1 điểm.
