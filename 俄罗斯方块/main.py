import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 计算游戏区域位置
GAME_AREA_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GAME_AREA_Y = 50

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# 形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, ORANGE, BLUE]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # 游戏状态
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_piece_x = 0
        self.current_piece_y = 0
        self.current_color = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        
        # 计时器
        self.fall_time = 0
        self.fall_speed = 500
        self.key_cooldown = 0  # 按键冷却
        self.key_cooldown_max = 10  # 冷却帧数
        
        # 生成第一个方块
        self.spawn_new_piece()
    
    def spawn_new_piece(self):
        """生成新的方块"""
        shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_piece = [row[:] for row in SHAPES[shape_index]]
        self.current_color = SHAPE_COLORS[shape_index]
        self.current_piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_piece_y = 0
        
        if self.check_collision():
            self.game_over = True
    
    def rotate_piece(self):
        """旋转当前方块"""
        # 顺时针旋转90度
        rotated = [[self.current_piece[y][x] for y in range(len(self.current_piece))] 
                   for x in range(len(self.current_piece[0]) - 1, -1, -1)]
        
        original_piece = self.current_piece
        self.current_piece = rotated
        
        if self.check_collision():
            self.current_piece = original_piece
    
    def move_piece(self, dx, dy):
        """移动当前方块"""
        self.current_piece_x += dx
        self.current_piece_y += dy
        
        if self.check_collision():
            self.current_piece_x -= dx
            self.current_piece_y -= dy
            return False
        return True
    
    def check_collision(self):
        """检查碰撞"""
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece_x + x
                    grid_y = self.current_piece_y + y
                    
                    if (grid_x < 0 or grid_x >= GRID_WIDTH or 
                        grid_y >= GRID_HEIGHT or grid_y < 0):
                        return True
                    
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return True
        return False
    
    def merge_piece(self):
        """固定当前方块"""
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece_x + x
                    grid_y = self.current_piece_y + y
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_color
    
    def clear_lines(self):
        """消除满行"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        
        while y >= 0:
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
                y += 1
            y -= 1
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += scores.get(lines_cleared, 100)
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 30)
    
    def drop_piece(self):
        """快速下落到底"""
        while self.move_piece(0, 1):
            pass
        self.lock_piece()
    
    def lock_piece(self):
        """锁定当前方块"""
        self.merge_piece()
        self.clear_lines()
        self.spawn_new_piece()
    
    def handle_input(self):
        """处理键盘输入 - 使用事件队列"""
        # 按键冷却递减
        if self.key_cooldown > 0:
            self.key_cooldown -= 1
    
    def update(self):
        """更新游戏逻辑"""
        if self.game_over:
            return
        
        # 自动下落
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = current_time
    
    def draw_grid(self):
        """绘制网格"""
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y),
                           (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + GRID_HEIGHT * BLOCK_SIZE), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GAME_AREA_X, GAME_AREA_Y + y * BLOCK_SIZE),
                           (GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE), 1)
    
    def draw_piece(self, piece, x, y, color):
        """绘制方块"""
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GAME_AREA_X + (x + col_idx) * BLOCK_SIZE,
                        GAME_AREA_Y + (y + row_idx) * BLOCK_SIZE,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 2)
    
    def draw(self):
        """绘制所有内容"""
        self.screen.fill(BLACK)
        
        # 绘制已固定的方块
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    rect = pygame.Rect(
                        GAME_AREA_X + x * BLOCK_SIZE,
                        GAME_AREA_Y + y * BLOCK_SIZE,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制当前方块
        if self.current_piece:
            self.draw_piece(self.current_piece, self.current_piece_x, 
                          self.current_piece_y, self.current_color)
        
        # 显示分数等信息
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (10, 90))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def restart(self):
        """重新开始"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_speed = 500
        self.spawn_new_piece()
    
    def run(self):
        """游戏主循环"""
        running = True
        
        while running:
            # 处理事件队列（这是关键修复）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 处理键盘按下事件（而非持续按下）
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.restart()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        # 游戏运行时的按键控制
                        if event.key == pygame.K_a:
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_d:
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_w:
                            self.rotate_piece()
                        elif event.key == pygame.K_s:
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_SPACE:
                            self.drop_piece()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
            
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Tetris()
    game.run()