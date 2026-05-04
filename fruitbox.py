import pygame
import random
import sys

# ===============================
# CẤU HÌNH CƠ BẢN CỦA GAME
# ==============================
WIDTH, HEIGHT = 850, 650
CELL_SIZE = 40
ROWS, COLS = 10, 15
GRID_OFFSET_X, GRID_OFFSET_Y = 120, 100

# Bảng màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 50, 50)
LIGHT_BLUE = (173, 216, 230)
GRAY = (220, 220, 220)
GREEN = (50, 200, 50)
DARK_GRAY = (100, 100, 100)

class FruitBoxDSA:
    def __init__(self):
        """Khởi tạo Game và thiết lập các biến trạng thái cơ bản."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fruit Box DSA")
        self.font = pygame.font.SysFont('consolas', 22, bold=True)
        self.clock = pygame.time.Clock()
        
        self.score = 0
        self.game_won = False
        
        # 1. Khởi tạo mảng 2 chiều bằng thuật toán Tối thượng (Ultimate Hybrid)
        self.grid = self.generate_ultimate_grid()
        
        # 2. Khởi tạo Mảng cộng dồn 2D (Prefix Sum)
        self.prefix_sum = [[0] * (COLS + 1) for _ in range(ROWS + 1)]
        self.build_prefix_sum()

        # Biến xử lý sự kiện chuột
        self.dragging = False
        self.start_pos = None
        self.current_pos = None

    # ==========================================================
    # [DSA 1] THUẬT TOÁN SINH TÁO 
    # ==========================================================
    def generate_ultimate_grid(self):
        """
        Thuật toán Sinh táo 
        Kết hợp: Cụm phân tán (Búp bê Nga) + Nhiễu Trọng số.
        Đảm bảo cấu trúc giải đố lồng ghép nhưng vẫn giữ được tỷ lệ xuất hiện của các số lớn.
        
        Time Complexity: O(N^2 log N) do sử dụng hàm sort() trong vòng lặp.
        Space Complexity: O(R * C) cho mảng lưới.
        """
        grid = [[0] * COLS for _ in range(ROWS)]
        
        # Tạo danh sách toàn bộ tọa độ và xáo trộn ngẫu nhiên
        available_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
        random.shuffle(available_cells)
        
        # --- CỤM "BÚP BÊ NGA" ---
        num_clusters = 25 
        for _ in range(num_clusters):
            if len(available_cells) < 4: break
            
            k = random.choices([2, 3, 4], weights=[50, 35, 15], k=1)[0]
            
            group_coords = [available_cells.pop(0)]
            center_r, center_c = group_coords[0]
            
            # Sắp xếp các ô trống theo khoảng cách tới trung tâm + nhiễu không gian
            available_cells.sort(key=lambda pos: abs(pos[0] - center_r) + abs(pos[1] - center_c) + random.uniform(0, 3))
            
            for _ in range(k - 1):
                group_coords.append(available_cells.pop(0))
                
            # Chia tổng 10 cho cụm
            vals = [1] * k
            target = 10 - k
            while target > 0:
                idx = random.randint(0, k - 1)
                if vals[idx] < 9:
                    vals[idx] += 1
                    target -= 1
                    
            for i, (r, c) in enumerate(group_coords):
                grid[r][c] = vals[i]
                
        # --- ĐỔ NHIỄU THEO TRỌNG SỐ ---
        # Bộ trọng số nhiều số lớn (7,8,9) để tăng độ khó và lấp đầy khoảng trống
        noise_population = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        noise_weights = [8, 8, 9, 8, 8, 8, 17, 17, 17] 
        
        for (r, c) in available_cells:
            grid[r][c] = random.choices(noise_population, weights=noise_weights, k=1)[0]
            
        return grid

    # ==========================================================
    # [DSA 2] MẢNG CỘNG DỒN 2 CHIỀU (2D PREFIX SUM)
    # ==========================================================
    def build_prefix_sum(self):
        """
        Xây dựng Mảng cộng dồn 2 chiều (2D Prefix Sum Array).
        Time Complexity: O(R * C)
        Space Complexity: O(R * C)
        """
        for r in range(1, ROWS + 1):
            for c in range(1, COLS + 1):
                self.prefix_sum[r][c] = (self.grid[r-1][c-1] 
                                       + self.prefix_sum[r-1][c] 
                                       + self.prefix_sum[r][c-1] 
                                       - self.prefix_sum[r-1][c-1])

    def query_sum(self, r1, c1, r2, c2):
        """
        Truy vấn tổng các phần tử trong một vùng hình chữ nhật bất kỳ.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return (self.prefix_sum[r2 + 1][c2 + 1] 
              - self.prefix_sum[r1][c2 + 1] 
              - self.prefix_sum[r2 + 1][c1] 
              + self.prefix_sum[r1][c1])

    # ==========================================================
    # XỬ LÝ SỰ KIỆN GIAO DIỆN CHUỘT
    # ==========================================================
    def get_cell_from_mouse(self, pos):
        """Chuyển đổi tọa độ Pixel thành Index mảng 2 chiều."""
        x, y = pos
        col = max(0, min((x - GRID_OFFSET_X) // CELL_SIZE, COLS - 1))
        row = max(0, min((y - GRID_OFFSET_Y) // CELL_SIZE, ROWS - 1))
        return row, col

    def check_selection(self):
        """Xử lý logic khi người chơi nhả chuột sau khi kéo Bounding Box."""
        if not self.start_pos or not self.current_pos: return

        r1, c1 = self.get_cell_from_mouse(self.start_pos)
        r2, c2 = self.get_cell_from_mouse(self.current_pos)
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)

        # Prefix Sum tính tổng O(1)
        total_sum = self.query_sum(min_r, min_c, max_r, max_c)

        if total_sum == 10:
            apples_eaten = 0
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    if self.grid[r][c] > 0:
                        apples_eaten += 1
                        self.grid[r][c] = 0 
            
            if apples_eaten > 0:
                self.score += apples_eaten
                self.build_prefix_sum()
                
            # Kiểm tra Win Condition
            apples_left = sum(1 for r in range(ROWS) for c in range(COLS) if self.grid[r][c] > 0)
            if apples_left == 0:
                self.game_won = True

    def draw_grid(self):
        """Vẽ lưới bàn cờ và các quả táo."""
        for r in range(ROWS):
            for c in range(COLS):
                val = self.grid[r][c]
                x = GRID_OFFSET_X + c * CELL_SIZE
                y = GRID_OFFSET_Y + r * CELL_SIZE
                
                pygame.draw.rect(self.screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
                
                if val > 0:
                    pygame.draw.circle(self.screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//2 - 2)
                    text = self.font.render(str(val), True, WHITE)
                    self.screen.blit(text, text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2)))

    def draw_selection(self):
        """Vẽ vùng chọn (Bounding Box) màu xanh dương trong suốt."""
        if self.dragging and self.start_pos and self.current_pos:
            r1, c1 = self.get_cell_from_mouse(self.start_pos)
            r2, c2 = self.get_cell_from_mouse(self.current_pos)
            min_r, max_r = min(r1, r2), max(r1, r2)
            min_c, max_c = min(c1, c2), max(c1, c2)
            
            x, y = GRID_OFFSET_X + min_c * CELL_SIZE, GRID_OFFSET_Y + min_r * CELL_SIZE
            w, h = (max_c - min_c + 1) * CELL_SIZE, (max_r - min_r + 1) * CELL_SIZE
            
            surface = pygame.Surface((w, h), pygame.SRCALPHA)
            surface.fill((173, 216, 230, 100))
            self.screen.blit(surface, (x, y))
            pygame.draw.rect(self.screen, LIGHT_BLUE, (x, y, w, h), 3)

    def run(self):
        """Vòng lặp chính của Game."""
        running = True

        while running:
            self.screen.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.game_won:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.dragging = True
                        self.start_pos = self.current_pos = event.pos
                    elif event.type == pygame.MOUSEMOTION and self.dragging:
                        self.current_pos = event.pos
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.dragging = False
                        self.check_selection()

            self.draw_grid()
            self.draw_selection()
            
            # Giao diện hiển thị
            score_text = self.font.render(f"🍎 ĐIỂM: {self.score}", True, BLACK)
            hint_text = self.font.render("💡 Drag the mouse to sum = 10", True, DARK_GRAY)
            
            self.screen.blit(score_text, (GRID_OFFSET_X, 40))
            self.screen.blit(hint_text, (WIDTH - 380, 40))

            if self.game_won:
                win_text = self.font.render("🎉 WIN! ĐÃ CLEAR SẠCH BÀN CỜ! [R] ĐỂ CHƠI LẠI", True, GREEN)
                self.screen.blit(win_text, (WIDTH//2 - 280, HEIGHT - 60))
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]: 
                    self.__init__()

            pygame.display.flip()
            self.clock.tick(60) 
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FruitBoxDSA()
    game.run()
