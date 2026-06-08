import pygame
import random
import sys
import json
import os
from datetime import datetime

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
LIGHT_GREEN = (0, 200, 0)
DARK_GRAY = (64, 64, 64)

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

# 排行榜数据文件
LEADERBOARD_FILE = "leaderboard.json"

class Leaderboard:
    """排行榜管理"""
    def __init__(self):
        self.scores = self.load()
    
    def load(self):
        """加载排行榜"""
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save(self):
        """保存排行榜"""
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)
    
    def add_score(self, name, score, level, lines):
        """添加分数到排行榜"""
        entry = {
            "name": name if name else "Anonymous",
            "score": score,
            "level": level,
            "lines": lines,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.scores.append(entry)
        # 按分数排序，保留前20名
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:20]
        self.save()
    
    def get_top(self, count=10):
        """获取前N名"""
        return self.scores[:count]


class Button:
    """按钮类"""
    def __init__(self, x, y, width, height, text, font, color=LIGHT_GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover = False
    
    def draw(self, surface):
        """绘制按钮"""
        color = (255, 100, 0) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        """检查是否被点击"""
        return self.rect.collidepoint(pos)
    
    def check_hover(self, pos):
        """检查是否悬停"""
        self.hover = self.rect.collidepoint(pos)


class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # 排行榜
        self.leaderboard = Leaderboard()
        
        # 按钮
        self.start_button = Button(SCREEN_WIDTH // 2 - 75, 300, 150, 50, "Start Game", self.font)
        self.leaderboard_button = Button(SCREEN_WIDTH // 2 - 75, 380, 150, 50, "Leaderboard", self.font)
        self.quit_button = Button(SCREEN_WIDTH // 2 - 75, 460, 150, 50, "Quit", self.font)
        self.restart_button = Button(SCREEN_WIDTH // 2 - 75, 550, 150, 50, "Return", self.font)
        
        # 游戏状态
        self.game_state = "menu"  # menu, playing, game_over, leaderboard, name_input
        
        # 游戏数据
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_piece_x = 0
        self.current_piece_y = 0
        self.current_color = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        
        # 玩家名称输入
        self.player_name = ""
        self.input_active = False
        self.name_input_text = ""
        
        # 计时器
        self.fall_time = 0
        self.fall_speed = 500
        self.key_cooldown = 0
        self.key_cooldown_max = 10
        
    def reset_game(self):
        """重置游戏"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_speed = 500
        self.player_name = ""
        self.name_input_text = ""
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
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "leaderboard":
            self.draw_leaderboard()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "name_input":
            self.draw_name_input()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title_text = self.large_font.render("俄罗斯方块", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.leaderboard_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)
        
        # 绘制按钮
        self.start_button.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        # 绘制简单说明
        help_text = self.small_font.render("A/D: Move | W: Rotate | S: Down | Space: Drop", True, GRAY)
        self.screen.blit(help_text, (10, 650))
    
    def draw_leaderboard(self):
        """绘制排行榜"""
        # 标题
        title_text = self.large_font.render("排行榜", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # 获取前10名
        top_scores = self.leaderboard.get_top(10)
        
        # 列表标题
        header = self.font.render("Rank  Name       Score  Level", True, WHITE)
        self.screen.blit(header, (20, 70))
        
        # 绘制排行榜
        y_offset = 110
        if not top_scores:
            empty_text = self.small_font.render("No scores yet", True, GRAY)
            self.screen.blit(empty_text, (SCREEN_WIDTH // 2 - 60, y_offset))
        else:
            for idx, entry in enumerate(top_scores[:10], 1):
                score_text = self.small_font.render(
                    f"{idx:2d}.  {entry['name']:<7s}  {entry['score']:>5d}  {entry['level']:>2d}",
                    True, WHITE if idx % 2 == 0 else GRAY
                )
                self.screen.blit(score_text, (20, y_offset))
                y_offset += 35
        
        # 返回按钮
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        self.restart_button.draw(self.screen)
        
        # 按ESC返回提示
        hint_text = self.small_font.render("Press ESC to return", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 110, 670))
    
    def draw_game(self):
        """绘制游戏画面"""
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
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        # 先绘制游戏画面
        self.draw_game()
        
        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束文本
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)
        
        # 显示最终分数
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # 提示进行名称输入
        hint_text = self.small_font.render("Press SPACE to save score", True, YELLOW)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)
        
        # 或者返回菜单
        return_text = self.small_font.render("Press ESC to return to menu", True, GRAY)
        return_rect = return_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(return_text, return_rect)
    
    def draw_name_input(self):
        """绘制名称输入界面"""
        # 背景
        self.screen.fill(BLACK)
        
        # 标题
        title_text = self.large_font.render("保存分数", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 分数信息
        score_info = self.font.render(f"Score: {self.score} | Level: {self.level}", True, WHITE)
        score_rect = score_info.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(score_info, score_rect)
        
        # 输入框标签
        label_text = self.font.render("Player Name:", True, WHITE)
        self.screen.blit(label_text, (SCREEN_WIDTH // 2 - 170, 280))
        
        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 320, 300, 50)
        pygame.draw.rect(self.screen, WHITE, input_rect, 2)
        pygame.draw.rect(self.screen, DARK_GRAY, input_rect)
        
        # 输入文本
        input_text = self.font.render(self.name_input_text + ("|" if self.input_active else ""), True, WHITE)
        self.screen.blit(input_text, (input_rect.x + 10, input_rect.y + 10))
        
        # 按钮
        mouse_pos = pygame.mouse.get_pos()
        save_button = Button(SCREEN_WIDTH // 2 - 160, 420, 140, 40, "Save", self.font)
        skip_button = Button(SCREEN_WIDTH // 2 + 20, 420, 140, 40, "Skip", self.font)
        
        save_button.check_hover(mouse_pos)
        skip_button.check_hover(mouse_pos)
        
        save_button.draw(self.screen)
        skip_button.draw(self.screen)
        
        # 提示文本
        hint_text = self.small_font.render("Enter your name (optional)", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 130, 250))
    
    def restart(self):
        """重新开始（保留old方法名以兼容）"""
        self.reset_game()
        self.game_state = "playing"
    
    def update(self):
        """更新游戏逻辑"""
        if self.game_state != "playing" or self.game_over:
            return
        
        # 自动下落
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = current_time
    
    def run(self):
        """游戏主循环"""
        running = True
        self.game_state = "menu"
        
        while running:
            # 处理事件队列
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    
                    if self.game_state == "menu":
                        if self.start_button.is_clicked(pos):
                            self.reset_game()
                            self.game_state = "playing"
                            self.fall_time = pygame.time.get_ticks()
                        elif self.leaderboard_button.is_clicked(pos):
                            self.game_state = "leaderboard"
                        elif self.quit_button.is_clicked(pos):
                            running = False
                    
                    elif self.game_state == "leaderboard":
                        if self.restart_button.is_clicked(pos):
                            self.game_state = "menu"
                    
                    elif self.game_state == "name_input":
                        # 保存按钮
                        save_button = Button(SCREEN_WIDTH // 2 - 160, 420, 140, 40, "Save", self.font)
                        skip_button = Button(SCREEN_WIDTH // 2 + 20, 420, 140, 40, "Skip", self.font)
                        
                        if save_button.is_clicked(pos):
                            self.leaderboard.add_score(
                                self.name_input_text,
                                self.score,
                                self.level,
                                self.lines_cleared
                            )
                            self.game_state = "menu"
                        elif skip_button.is_clicked(pos):
                            self.game_state = "menu"
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    
                    elif self.game_state == "leaderboard":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                    
                    elif self.game_state == "playing":
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
                            self.game_state = "menu"
                        
                        # 检查游戏是否结束
                        if self.game_over:
                            self.game_state = "game_over"
                    
                    elif self.game_state == "game_over":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "name_input"
                            self.input_active = True
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                    
                    elif self.game_state == "name_input":
                        if event.key == pygame.K_BACKSPACE:
                            self.name_input_text = self.name_input_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.leaderboard.add_score(
                                self.name_input_text,
                                self.score,
                                self.level,
                                self.lines_cleared
                            )
                            self.game_state = "menu"
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                        elif len(self.name_input_text) < 15:
                            if event.unicode.isprintable():
                                self.name_input_text += event.unicode
            
            # 更新游戏逻辑
            self.update()
            
            # 绘制
            self.draw()
            
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Tetris()
    game.run()
