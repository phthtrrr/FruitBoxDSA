
FRUIT BOX DSA

Người chơi sẽ quét chuột tạo thành các vùng chọn hình chữ nhật. Nếu tổng
các phần tử bên trong vùng chọn đúng bằng 10, các quả táo sẽ bị triệt tiêu
và người chơi sẽ được cộng điểm.

--------------------------------------------------
(GIAI ĐOẠN TUẦN 1 & 2)
--------------------------------------------------
- Nhấn giữ chuột trái & Kéo: 
    Tạo một khung chọn (Bounding Box) màu xanh dương bao quanh các quả táo.
    
- Nhả chuột:
    Kiểm tra tổng các quả táo trong vùng vừa quét.
    + Nếu Tổng = 10: Xóa các quả táo đó (gán giá trị về 0) và cộng điểm.
    + Nếu Tổng != 10: Không có chuyện gì xảy ra.

--------------------------------------------------
KÝ HIỆU DỮ LIỆU (MA TRẬN 2 CHIỀU)
--------------------------------------------------
Trong ma trận self.grid:
     0    : Ô trống (táo đã bị ăn).
     1..9 : Quả táo mang giá trị tương ứng.

--------------------------------------------------
THÔNG SỐ HỆ THỐNG
--------------------------------------------------
ROWS = 10       Số hàng của bàn cờ
COLS = 15       Số cột của bàn cờ
CELL_SIZE = 40  Kích thước mỗi ô (Pixel)

--------------------------------------------------
THƯ VIỆN SỬ DỤNG
--------------------------------------------------
pygame : Xử lý đồ họa vòng lặp 60 FPS, vẽ hình khối, bắt sự kiện chuột.
random : Rải dữ liệu mảng ngẫu nhiên (Dummy Data).
sys    : Xử lý thoát chương trình an toàn.
"""

class FruitBoxDSA:
    def __init__(self):
        """
        Khởi tạo môi trường Pygame và các cấu trúc dữ liệu nền tảng.
        
        Công việc chính:
        1. Thiết lập cửa sổ hiển thị, font chữ, đồng hồ FPS.
        2. Khởi tạo mảng 2 chiều chứa táo (self.grid).
        3. Khởi tạo và tính toán mảng cộng dồn (self.prefix_sum).
        4. Chuẩn bị các biến trạng thái xử lý sự kiện chuột.
        """

    def generate_dummy_grid(self):
        """
        Tạo dữ liệu giả lập (Dummy Data) cho không gian bàn cờ.
        
        Chức năng:
        Khởi tạo ma trận kích thước ROWS x COLS và rải ngẫu nhiên các 
        số nguyên từ 1 đến 9 vào từng ô.
        
        Trả về:
            list[list[int]]: Ma trận 2 chiều chứa dữ liệu bàn cờ.
            
        Độ phức tạp:
            - Time Complexity: O(R * C)
            - Space Complexity: O(R * C)
        """

    def get_cell_from_mouse(self, pos):
        """
        [Giải thuật Ánh xạ] Chuyển tọa độ Pixel thành Index ma trận.
        
        Chức năng:
        Nhận tọa độ chuột hiện tại, trừ đi khoảng cách offset của viền màn hình,
        sau đó chia lấy phần nguyên cho kích thước ô (CELL_SIZE) để ra chỉ số dòng/cột.
        Sử dụng hàm min/max để kẹp biên, tránh lỗi Out of Bounds.
        
        Tham số:
            pos (tuple): Tọa độ (x, y) của chuột trên giao diện.
        
        Trả về:
            tuple: (row, col) chỉ số dòng và cột tương ứng trong self.grid.
            
        Độ phức tạp:
            - Time Complexity: O(1)
        """

    def build_prefix_sum(self):
        """
        Xây dựng Mảng cộng dồn 2 chiều (2D Prefix Sum Array).
        
        Chức năng:
        Tính toán tổng cộng dồn của mọi vùng hình chữ nhật từ tọa độ (0,0)
        đến (i, j). Hàm này được gọi 1 lần lúc khởi tạo và gọi lại mỗi khi 
        táo trên bàn cờ bị ăn mất để cập nhật dữ liệu.
        
        Không trả về giá trị (cập nhật trực tiếp vào self.prefix_sum).
        
        Độ phức tạp:
            - Time Complexity: O(R * C)
            - Space Complexity: O(R * C)
        """

    def query_sum(self, r1, c1, r2, c2):
        """
        Truy vấn tổng các phần tử trong một vùng hình chữ nhật bất kỳ.
        
        Chức năng:
        Sử dụng cấu trúc dữ liệu Mảng cộng dồn (Prefix Sum) để truy xuất tổng
        của vùng chọn Bounding Box chỉ bằng 4 phép tính cộng/trừ cơ bản, thay 
        vì phải dùng 2 vòng lặp lồng nhau duyệt qua từng ô.
        
        Tham số:
            r1, c1 (int): Tọa độ dòng, cột của ô bắt đầu (Top-Left).
            r2, c2 (int): Tọa độ dòng, cột của ô kết thúc (Bottom-Right).
            
        Trả về:
            int: Tổng các giá trị quả táo nằm bên trong vùng chọn.
            
        Độ phức tạp:
            - Time Complexity: O(1) tuyệt đối.
        """

    def check_selection(self):
        """
        Xử lý logic cốt lõi khi người chơi hoàn thành thao tác kéo chuột.
        
        Công việc chính:
        1. Quy đổi tọa độ 2 điểm kéo chuột thành tọa độ hình chữ nhật (min_r, max_r).
        2. Gọi hàm query_sum() để lấy tổng vùng.
        3. Nếu tổng = 10:
            - Duyệt qua vùng chọn, đổi giá trị táo > 0 thành 0.
            - Cộng điểm dựa trên số lượng táo bị ăn.
            - Gọi build_prefix_sum() để tính lại mảng cộng dồn.
            
        Không trả về giá trị.
        """

    def draw_grid(self):
        """
        Vẽ toàn bộ không gian lưới và các thực thể lên cửa sổ.
        
        Bao gồm:
        - Các đường kẻ ô vuông (Grid lines) màu xám.
        - Các quả táo (Hình tròn đỏ).
        - Giá trị số (Màu trắng) nằm căn giữa quả táo.
        
        Không trả về giá trị.
        """

    def draw_selection(self):
        """
        Vẽ vùng chọn Bounding Box trong suốt bám theo con trỏ chuột.
        
        Chức năng:
        Sử dụng cờ pygame.SRCALPHA để tạo một lớp (Surface) màu xanh dương
        có độ trong suốt (Alpha = 100), giúp hiển thị hiệu ứng highlight khi
        người chơi đang nhấn giữ và kéo chuột.
        
        Không trả về giá trị.
        """

    def run(self):
        """
        Vòng lặp chính điều khiển toàn bộ trò chơi (Game Loop).
        
        Công việc chính:
        1. Xóa màn hình và đổ màu nền (WHITE).
        2. Lắng nghe và xử lý sự kiện:
            - QUIT: Đóng game.
            - MOUSEBUTTONDOWN: Bắt đầu vẽ khung chọn.
            - MOUSEMOTION: Cập nhật tọa độ khung chọn.
            - MOUSEBUTTONUP: Kết thúc chọn và tính tổng.
        3. Gọi các hàm Render (vẽ lưới, vẽ khung chọn, vẽ điểm số).
        4. Cập nhật Frame màn hình với tốc độ 60 FPS.
        
        Không trả về giá trị.
        """
