import pygame
import random
import sys

# ========================
# CẤU HÌNH CƠ BẢN CỦA GAME
# ========================
WIDTH, HEIGHT = 850, 650
CELL_SIZE = 40
ROWS, COLS = 10, 15
GRID_OFFSET_X, GRID_OFFSET_Y = 120, 100

# BẢNG MÀU
BLACK = (0, 0, 0)
DARK_GRAY = (100, 100, 100)
RED = (230, 50, 50)
GRAY = (220, 220, 220)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230) 

class FruitBoxDSA:
    def __init__(self):
        """Khởi tạo môi trường Pygame và không gian ma trận lưới của game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fruit Box DSA - Tuần 2: Prefix Sum & Core Logic")
        self.font = pygame.font.SysFont('consolas', 22, bold=True)
        self.clock = pygame.time.Clock()
        
        # Khởi tạo mảng 2 chiều với dữ liệu giả lập ngẫu nhiên từ 1-9
        self.grid = self.generate_dummy_grid()

        # Khởi tạo các biến phục vụ cho logic chính và Prefix Sum
        self.score = 0
        self.prefix_sum = [[0] * (COLS + 1) for _ in range(ROWS + 1)]
        self.build_prefix_sum()

        self.dragging = False
        self.start_pos = None
        self.current_pos = None


    def generate_dummy_grid(self):
        """Tạo một mảng 2 chiều với các giá trị ngẫu nhiên từ 1-9 để làm dữ liệu giả lập."""
        grid = [[0] * COLS for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                grid[r][c] = random.randint(1, 9)
        return grid

    def get_cell_from_mouse(self, pos):
        """Chuyển tọa độ Pixel thành tọa ddoj (row, col)."""
        x, y = pos
        col = max(0, min((x - GRID_OFFSET_X) // CELL_SIZE, COLS - 1))
        row = max(0, min((y - GRID_OFFSET_Y) // CELL_SIZE, ROWS - 1))
        return row, col


    def build_prefix_sum(self):
        """Xây dựng Mảng cộng dồn 2 chiều (2D Prefix Sum)."""
        for r in range(1, ROWS + 1):
            for c in range(1, COLS + 1):
                self.prefix_sum[r][c] = (self.grid[r-1][c-1]  + self.prefix_sum[r-1][c] + self.prefix_sum[r][c-1] - self.prefix_sum[r-1][c-1])

    def query_sum(self, r1, c1, r2, c2):
        """Truy vấn tổng các phần tử trong một vùng hình chữ nhật bất kỳ."""
        return (self.prefix_sum[r2 + 1][c2 + 1] - self.prefix_sum[r1][c2 + 1] - self.prefix_sum[r2 + 1][c1] + self.prefix_sum[r1][c1])

    def check_selection(self):
        """Xử lý logic tính tổng vùng chọn, xóa táo và cộng điểm."""
        if not self.start_pos or not self.current_pos: return

        r1, c1 = self.get_cell_from_mouse(self.start_pos)
        r2, c2 = self.get_cell_from_mouse(self.current_pos)
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)

        total_sum = self.query_sum(min_r, min_c, max_r, max_c)

        if total_sum == 10:
            apples_eaten = 0
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    if self.grid[r][c] > 0:
                        apples_eaten += 1
                        self.grid[r][c] = 0 # Xóa táo (gán = 0)
            
            if apples_eaten > 0:
                self.score += apples_eaten
                # Cập nhật lại mảng cộng dồn vừa thay đổi
                self.build_prefix_sum()


    def draw_grid(self):
        """Duyệt mảng 2 chiều để vẽ lưới và táo lên màn hình."""
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
        running = True
        while running:
            self.screen.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Nhậm sự kiện kéo thả chuột
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.dragging = True
                    self.start_pos = self.current_pos = event.pos
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.current_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging:
                        self.dragging = False
                        self.check_selection() # Nhả chuột thì kiểm tra tổng

            self.draw_grid()
            self.draw_selection() # Vẽ khung bounding box
            
            # Giao diện hiển thị Điểm số
            score_text = self.font.render(f"SCORE: {self.score}", True, BLACK)
            hint_text = self.font.render("Drag the mouse to sum = 10.", True, DARK_GRAY)
            
            self.screen.blit(score_text, (GRID_OFFSET_X, 40))
            self.screen.blit(hint_text, (WIDTH - 380, 40))

            pygame.display.flip()
            self.clock.tick(60) 
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FruitBoxDSA()
    game.run()