import pygame
import random
import sys


"""Phân tích và thiết kế game giải đố Fruit Box.

Tựa game giải đố trí tuệ kết hợp yếu tố Time Attack. Người chơi tương tác 
trên một ma trận lưới 10x15 bằng cách kéo chuột khoanh vùng các quả táo sao 
cho tổng các giá trị trong vùng bằng đúng 10.

Các kỹ thuật Cấu trúc Dữ liệu & Giải thuật (DSA) áp dụng:
  * Tuật toán Sinh mảng lai  (Hybrid Generation) nhằm cchống bí nước.
  * Mảng cộng dồn 2 chiều (2D Prefix Sum) đệm biên giúp tăng tốc giảm thời gian truy vấn còn O(1).
  * Giải thuật Tìm kiếm Cắt tỉa (Pruning Search) cho hệ thống gợi ý.
"""

# CẤU HÌNH CƠ BẢN 
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
DARK_RED = (180, 30, 30)
GOLD = (255, 215, 0)  

class FruitBoxDSA:
    def __init__(self):
        """Khởi tạo Game và thiết lập các biến trạng thái cơ bản."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fruit Box DSA")
        
        # Khởi tạo Fonts
        self.font = pygame.font.SysFont('consolas', 22, bold=True)
        self.font_small = pygame.font.SysFont('consolas', 18, bold=True) 
        self.font_large = pygame.font.SysFont('consolas', 60, bold=True)
        self.font_title = pygame.font.SysFont('consolas', 40, bold=True)
        self.clock = pygame.time.Clock()
        
        # TRẠNG THÁI GAME: "START" | "PLAYING" | "GAMEOVER"
        self.state = "START"
        
        # UI Rects (Nút bấm)
        self.start_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 65, 200, 50) 
        self.tutorial_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50) 
        self.back_btn_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 100, 120, 40)      
        self.home_btn_rect = pygame.Rect(WIDTH - 140, 30, 100, 40) 
        
        # Các biến trong game
        self.score = 0
        self.time_limit = 120
        self.time_left = self.time_limit
        self.last_tick = 0
        self.grid = []
        self.prefix_sum = []
        
        # Biến xử lý sự kiện chuột
        self.dragging = False
        self.start_pos = None
        self.current_pos = None
        
        # Biến hệ thống gợi ý
        self.current_hint = None  
        self.hint_delay = 10000  
        self.last_eat_tick = 0   

    def reset_game(self):
        """Hàm khởi tạo lại toàn bộ dữ liệu bộ nhớ (Lưới, Prefix Sum, Bộ đếm) 
        để bắt đầu một ván chơi hoàn toàn mới, tránh rò rỉ dữ liệu cũ."""
        self.score = 0
        self.time_left = self.time_limit
        self.last_tick = pygame.time.get_ticks()
        
        # Khởi tạo mảng 2 chiều bằng thuật toán sinh mảng
        self.grid = self.generate_grid()
        
        # Khởi tạo Mảng cộng dồn 2D (Prefix Sum)
        self.prefix_sum = [[0] * (COLS + 1) for _ in range(ROWS + 1)]
        self.build_prefix_sum()
        
        self.dragging = False
        self.current_hint = None  
        # Bắt đầu game sẽ làm mới bộ chờ của tính năng gợi ý
        self.last_eat_tick = pygame.time.get_ticks()

    # THUẬT TOÁN SINH TÁO (HYBRID GENERATION)
    def generate_grid(self):
        """
        Hàm Sinh bản đồ 10x15 táo kết hợp 3 tầng thuật toán để cân bằng game và giúp giảm bí nước cục bộ ban đầu:
        1. Gieo cặp nghiệm cha bị ngăn cách bởi nghiệm con.
        2. Gom cụm các ô gần nhau theo khoảng cách Manhattan.
        3. Rejection Sampling: Đổ nhiễu và lọc để tổng ma trận chia hết cho 10.
        
        Returns:
            list: Ma trận 2 chiều 10x15 chứa các giá trị từ 1 đến 9.
        """

        grid = [[0] * COLS for _ in range(ROWS)]
        available_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
        random.shuffle(available_cells)
        
        # GIEO CẶP NGHIỆM CHA BỊ NGĂN CÁCH BỞI NGHIỆM CON
        num_chains = 4
        for _ in range(num_chains):
            # chọn cặp "Cha" (có tổng bằng 10) nằm ở 2 đầu
            parent_pairs = [(9, 1), (8, 2), (7, 3), (6, 4), (5, 5)]
            p1, p2 = random.choice(parent_pairs)
            if random.random() < 0.5: p1, p2 = p2, p1 # Xáo vị trí trái/phải
            
            # chọn ngẫu nhiên độ dài cụm "Con" cản đường ở giữa (2, 3, hoặc 4 táo)
            child_len = random.choice([2, 3, 4])
            
            # Tự động sinh ngẫu nhiên các giá trị cho cụm Con sao cho tổng đúng bằng 10
            child_vals = [1] * child_len
            target = 10 - child_len
            while target > 0:
                idx = random.randint(0, child_len - 1)
                if child_vals[idx] < 9:
                    child_vals[idx] += 1
                    target -= 1
            
            # Tổng số táo của cả chuỗi 
            total_len = 2 + child_len
            is_horizontal = random.random() < 0.5 # 50% nằm ngang, 50% nằm dọc
            
            if is_horizontal:
                r = random.randint(0, ROWS - 1)
                c = random.randint(0, COLS - total_len)
                chain_cells = [(r, c + i) for i in range(total_len)]
                
                if all(cell in available_cells for cell in chain_cells):
                    grid[r][c] = p1
                    grid[r][c + total_len - 1] = p2
                    for i in range(child_len):
                        grid[r][c + 1 + i] = child_vals[i]
                        
                    for cell in chain_cells: available_cells.remove(cell)
            else: # Bố trí theo chiều dọc
                r = random.randint(0, ROWS - total_len)
                c = random.randint(0, COLS - 1)
                chain_cells = [(r + i, c) for i in range(total_len)]
                
                if all(cell in available_cells for cell in chain_cells):
                    grid[r][c] = p1
                    grid[r + total_len - 1][c] = p2
                    for i in range(child_len):
                        grid[r + 1 + i][c] = child_vals[i]
                        
                    for cell in chain_cells: available_cells.remove(cell)

        # GOM CỤM CÁC Ô GẦN NHAU THEO KHOẢNG CÁCH MANHATTAN.
        num_clusters = 4
        for _ in range(num_clusters):
            if len(available_cells) < 4: break
            
            k = random.choices([2, 3, 4], weights=[50, 30, 20], k=1)[0]
            group_coords = [available_cells.pop(0)]
            center_r, center_c = group_coords[0]
            
            available_cells.sort(key=lambda pos: abs(pos[0] - center_r) + abs(pos[1] - center_c) + random.uniform(0, 3))
            
            for _ in range(k - 1):
                group_coords.append(available_cells.pop(0))
                
            vals = [1] * k
            target = 10 - k
            while target > 0:
                idx = random.randint(0, k - 1)
                if vals[idx] < 9:
                    vals[idx] += 1
                    target -= 1
                    
            for i, (r, c) in enumerate(group_coords):
                grid[r][c] = vals[i]
                
                

        # REJECTION SAMPLING: ĐỔ NHIỄU VÀ LỌC ĐỂ TỔNG MA TRẬN CHIA HẾT CHO 10.
        noise_population = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        noise_weights = [14, 13, 12, 11, 10, 10, 10, 10, 10] 
        
        while True:
            noise_vals = random.choices(noise_population, weights=noise_weights, k=len(available_cells))
            if sum(noise_vals) % 10 == 0:
                break
                
        # Đổ mảng nhiễu đã hợp lệ vào các ô trống trên bàn cờ
        for i, (r, c) in enumerate(available_cells):
            grid[r][c] = noise_vals[i]
            
        return grid


    # MẢNG CỘNG DỒN 2 CHIỀU (2D PREFIXSUM)
    def build_prefix_sum(self):
        """
        Xây dựng mảng cộng dồn 2 chiều
        Độ phức tạp: O(ROWS * COLS).
        Áp dụng thêm kỹ thuật đặt lính canh ở vùng ranh để tránh bị lỗi tràn mảng (Out of bounds) 
        và giúp giảm thiểu sử dụng câu lệnh if/e;se rối rắm.
        """
        for r in range(1, ROWS + 1):
            for c in range(1, COLS + 1):
                self.prefix_sum[r][c] = (self.grid[r-1][c-1] 
                                       + self.prefix_sum[r-1][c] 
                                       + self.prefix_sum[r][c-1] 
                                       - self.prefix_sum[r-1][c-1])

    def query_sum(self, r1, c1, r2, c2):
        """
        Truy vấn tổng các phần tử trong vùng hình chữ nhật (r1, c1) đến (r2, c2).
        Độ phức tạp: O(1) hằng số, thông qua nguyên lý Bù trừ.
        
        Args:
            r1, c1 (int): Tọa độ hàng, cột của góc trên bên trái.
            r2, c2 (int): Tọa độ hàng, cột của góc dưới bên phải.
            
        Returns:
            int: Tổng giá trị các quả táo nằm trong vùng chọn.
        """
        return (self.prefix_sum[r2 + 1][c2 + 1] 
              - self.prefix_sum[r1][c2 + 1] 
              - self.prefix_sum[r2 + 1][c1] 
              + self.prefix_sum[r1][c1])


    # GIẢI THUẬT TÌM KIẾM CẮT TỈA (PRUNING SEARCH)
    def get_hint(self):
        """
        Quét tìm vùng Bounding Box tối ưu có tổng bằng 10 trên lưới.
        Áp dụng kỹ thuật tìm kiếm Cắt tỉa nhánh (Pruning Search): Dừng mở rộng vùng quét
        ngay khi tổng vượt quá 10, loại bỏ không gian tìm kiếm hoang phí.
        
        Returns:
            tuple hoặc None: Bộ tọa độ (r1, c1, r2, c2) nếu tìm thấy nghiệm,
                             ngược lại trả về None (khi không còn nước đi).
        """
        for r1 in range(ROWS):
            for c1 in range(COLS):
                if self.grid[r1][c1] == 0: 
                    continue
                
                for r2 in range(r1, ROWS):
                    for c2 in range(c1, COLS):
                        s = self.query_sum(r1, c1, r2, c2)
                        # (PRUNING): Vì mảng không có số âm, 
                        # nếu tổng > 10 thì việc mở rộng cột tiếp theo sẽ không phải kết quả cần tìm.
                        if s > 10: 
                            break
                        if s == 10:
                            return (r1, c1, r2, c2)
        return None


    # XỬ LÝ SỰ KIỆN GIAO DIỆN CHUỘT
    def get_cell_from_mouse(self, pos):
        """
        Ánh xạ tọa độ điểm ảnh (Pixel) sang chỉ số hàng/cột của Lưới ma trận.
        Áp dụng kỹ thuật kẹp Biên để đảm bảo không bị lỗi Out of Bounds.
        
        Args:
            pos (tuple): Tọa độ (x, y) của con trỏ chuột trên màn hình.
            
        Returns:
            tuple: Chỉ số (row, col) tương ứng trên lưới 10x15.
        """
        x, y = pos
        col = max(0, min((x - GRID_OFFSET_X) // CELL_SIZE, COLS - 1))
        row = max(0, min((y - GRID_OFFSET_Y) // CELL_SIZE, ROWS - 1))
        return row, col

    def check_selection(self):
        """
        Xử lý việc triệt tiêu táo khi người chơi nhả chuột.
        Đồng bộ lại dữ liệu: Cập nhật điểm số, gán ma trận về 0, tái cấu trúc 
        Prefix Sum và kiểm tra cơ chế kết thúc game.
        """
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
                        self.grid[r][c] = 0 
            
            if apples_eaten > 0:
                self.score += apples_eaten
                self.build_prefix_sum()
                self.current_hint = None  
                self.last_eat_tick = pygame.time.get_ticks()
                
            apples_left = sum(1 for r in range(ROWS) for c in range(COLS) if self.grid[r][c] > 0)
            
            # KIỂM TRA ĐIỀU KIỆN KẾT THÚC GAME VÀ TỐI ƯU UX
            if apples_left == 0:
                # Trường hợp 1: Clear toàn bộ táo (Phá đảo tuyệt đối)
                self.state = "GAMEOVER"
            elif self.get_hint() is None:
                # Trường hợp 2: Vẫn còn táo nhưng KHÔNG CÒN NGHIỆM NÀO TỔNG bằng 10
                # Tự động kết thúc game ngay lập tức để tối ưu logic
                self.state = "GAMEOVER"



    # CÁC HÀM VẼ GIAO DIỆN (UI)
    def draw_start_screen(self):
        """Render giao diện Menu Khởi đầu kèm hình ảnh trang trí trực quan."""
        self.screen.fill(WHITE)
        pygame.draw.circle(self.screen, RED, (WIDTH//2, HEIGHT//2 - 60), 70)
        pygame.draw.circle(self.screen, DARK_RED, (WIDTH//2, HEIGHT//2 - 60), 70, 5) 
        pygame.draw.ellipse(self.screen, GREEN, (WIDTH//2 - 10, HEIGHT//2 - 150, 40, 25)) 
        pygame.draw.rect(self.screen, (139, 69, 19), (WIDTH//2 - 5, HEIGHT//2 - 130, 10, 20)) 
        
        title = self.font_title.render("FRUIT BOX DSA", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
        
        mouse_pos = pygame.mouse.get_pos()
        btn_color = GREEN if self.start_btn_rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(self.screen, btn_color, self.start_btn_rect, border_radius=10)
        
        start_text = self.font.render("START", True, WHITE)
        self.screen.blit(start_text, start_text.get_rect(center=self.start_btn_rect.center))

        # 2. [MỚI] Vẽ Nút HOW TO PLAY
        color_t = LIGHT_BLUE if self.tutorial_btn_rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(self.screen, color_t, self.tutorial_btn_rect, border_radius=10)
        tut_txt = self.font.render("HOW TO PLAY", True, WHITE)
        self.screen.blit(tut_txt, tut_txt.get_rect(center=self.tutorial_btn_rect.center))

    def draw_tutorial_screen(self):
        """Render lớp phủ (Overlay) minh họa quy tắc và luật chơi game."""
        self.draw_start_screen()
        
        #Phủ một lớp kính mờ màu đen lên trên
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ bảng thông báo màu trắng bo góc
        box_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 150, 600, 300)
        pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=15)
        pygame.draw.rect(self.screen, LIGHT_BLUE, box_rect, width=5, border_radius=15)
        
        # nội dung Tutorial
        lines = [
            "HOW TO PLAY",
            "",
            "Drag the mouse to exactly enclose some apples",
            "so the numbers in the apples total 10.",
            "",
            "You get 1 point for each apple."
        ]
        
        for i, line in enumerate(lines):
            color = RED if i == 0 else BLACK
            f = self.font if i == 0 else self.font_small
            txt = f.render(line, True, color)
            self.screen.blit(txt, txt.get_rect(center=(WIDTH//2, box_rect.top + 30 + i*30)))
            
        # Vẽ nút BACK
        mouse_pos = pygame.mouse.get_pos()
        btn_color = RED if self.back_btn_rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(self.screen, btn_color, self.back_btn_rect, border_radius=8)
        back_txt = self.font.render("BACK", True, WHITE)
        self.screen.blit(back_txt, back_txt.get_rect(center=self.back_btn_rect.center))

    def draw_gameover_screen(self):
        """Render màn hình Tổng kết điểm số khi ván chơi kết thúc."""
        self.draw_grid()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220)) 
        self.screen.blit(overlay, (0, 0))
        
        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 40
        pygame.draw.circle(self.screen, RED, (center_x, center_y), 90)
        pygame.draw.rect(self.screen, (139, 69, 19), (center_x - 5, center_y - 110, 10, 25)) 
        pygame.draw.ellipse(self.screen, GREEN, (center_x - 15, center_y - 125, 45, 30)) 
        
        score_label = self.font.render("Score", True, WHITE)
        score_val = self.font_large.render(str(self.score), True, WHITE)
        self.screen.blit(score_label, score_label.get_rect(center=(center_x, center_y - 30)))
        self.screen.blit(score_val, score_val.get_rect(center=(center_x, center_y + 20)))

        self.play_again_btn_rect = pygame.Rect(center_x - 100, center_y + 120, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (0, 180, 0) if self.play_again_btn_rect.collidepoint(mouse_pos) else GREEN
        
        pygame.draw.rect(self.screen, btn_color, self.play_again_btn_rect, border_radius=8)
        btn_text = self.font.render("HOME", True, WHITE)
        self.screen.blit(btn_text, btn_text.get_rect(center=self.play_again_btn_rect.center))

    def draw_grid(self):
        """Render các đường kẻ lưới caro và trạng thái hiện tại của các quả táo."""
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
        """Render lớp phủ Bounding Box (vùng kéo chuột) khi kéo chuột và Khung vàng của tính năng Gợi ý."""
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
            
        if self.current_hint:
            hr1, hc1, hr2, hc2 = self.current_hint
            hx = GRID_OFFSET_X + hc1 * CELL_SIZE
            hy = GRID_OFFSET_Y + hr1 * CELL_SIZE
            hw = (hc2 - hc1 + 1) * CELL_SIZE
            hh = (hr2 - hr1 + 1) * CELL_SIZE
            pygame.draw.rect(self.screen, GOLD, (hx, hy, hw, hh), 4)


    # HÀM VÒNG LẶP CHẠY CỦA GAME
    def run(self):
        """Bắt đầu vòng lặp điều khiển chính của ứng dụng game.
    
    Cập nhật nhịp đếm thời gian, lắng nghe sự kiện ngoại vi và định 
    tuyến render đồ họa theo luồng Máy trạng thái hữu hạn FSM.
    """
        running = True

        while running:
            current_tick = pygame.time.get_ticks()
            
            if self.state == "PLAYING":
                if current_tick - self.last_tick >= 1000: 
                    self.time_left -= 1
                    self.last_tick = current_tick
                    
                    if self.time_left <= 0:
                        self.time_left = 0
                        self.state = "GAMEOVER" 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == "START":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.start_btn_rect.collidepoint(event.pos):
                            self.reset_game()
                            self.state = "PLAYING"
                        elif self.tutorial_btn_rect.collidepoint(event.pos):
                            self.state = "TUTORIAL"
                
                elif self.state == "TUTORIAL":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.state = "START"
     
                elif self.state == "PLAYING":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_h:  
                            if self.current_hint:
                                self.current_hint = None 
                            else:
                                # Tính thời gian tính năng Hint từ lần ăn táo thành công cuối cùng
                                time_since_last_eat = current_tick - self.last_eat_tick
                                if time_since_last_eat >= self.hint_delay:
                                    self.current_hint = self.get_hint()
                                
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.home_btn_rect.collidepoint(event.pos):
                            self.state = "START"
                        else:
                            self.dragging = True
                            self.start_pos = self.current_pos = event.pos
                            self.current_hint = None  
                    
                    elif event.type == pygame.MOUSEMOTION and self.dragging:
                        self.current_pos = event.pos
                    
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if self.dragging:
                            self.dragging = False
                            self.check_selection()

                elif self.state == "GAMEOVER":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.play_again_btn_rect.collidepoint(event.pos):
                            self.state = "START"

            if self.state == "START":
                self.draw_start_screen()

            elif self.state == "TUTORIAL":        
                self.draw_tutorial_screen()       
                
            elif self.state == "PLAYING":
                self.screen.fill(WHITE)
                self.draw_grid()
                self.draw_selection()
                
                score_text = self.font.render(f"🍎 SCORE: {self.score}", True, BLACK)
                time_color = RED if self.time_left <= 15 else BLACK
                time_text = self.font.render(f"⏱ TIME: {self.time_left}s", True, time_color)
                
                time_since_last_eat = current_tick - self.last_eat_tick
                if self.current_hint:
                    hint_str = "[H] Hinting"
                    hint_color = GOLD
                elif time_since_last_eat < self.hint_delay:
                    wait_left = (self.hint_delay - time_since_last_eat + 999) // 1000
                    hint_str = f"[H] Hint: {wait_left}s"
                    hint_color = RED
                else:
                    hint_str = "[H]: (Ready)"
                    hint_color = GREEN

                hint_text = self.font.render(hint_str, True, hint_color)
                
                self.screen.blit(score_text, (GRID_OFFSET_X, 40))
                self.screen.blit(time_text, (GRID_OFFSET_X + 250, 40))
                self.screen.blit(hint_text, (GRID_OFFSET_X + 430, 40))
                
                mouse_pos = pygame.mouse.get_pos()
                btn_color = RED if self.home_btn_rect.collidepoint(mouse_pos) else DARK_GRAY
                pygame.draw.rect(self.screen, btn_color, self.home_btn_rect, border_radius=5)
                home_text = self.font.render("HOME", True, WHITE)
                self.screen.blit(home_text, home_text.get_rect(center=self.home_btn_rect.center))

            elif self.state == "GAMEOVER":
                self.draw_gameover_screen()

            pygame.display.flip()
            self.clock.tick(60) 
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FruitBoxDSA()
    game.run()
