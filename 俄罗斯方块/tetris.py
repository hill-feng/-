import os
import pygame
import random
import sys
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT,
    GAME_AREA_X, GAME_AREA_Y,
    BLACK, WHITE, GRAY, CYAN, ORANGE, YELLOW, GREEN, PURPLE, RED,
    LIGHT_GREEN, DARK_GRAY,
    SHAPES, SHAPE_COLORS
)
from leaderboard import Leaderboard
from button import Button


class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = self.load_font(36)
        self.small_font = self.load_font(24)
        self.large_font = self.load_font(48, bold=True)

        self.leaderboard = Leaderboard()

        self.start_button = Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "开始游戏", self.font)
        self.leaderboard_button = Button(SCREEN_WIDTH // 2 - 100, 380, 200, 50, "排行榜", self.font)
        self.quit_button = Button(SCREEN_WIDTH // 2 - 100, 460, 200, 50, "退出", self.font)
        self.restart_button = Button(SCREEN_WIDTH // 2 - 100, 550, 200, 50, "返回菜单", self.font)

        self.game_state = "menu"
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_piece_x = 0
        self.current_piece_y = 0
        self.current_color = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

        self.player_name = ""
        self.input_active = False
        self.name_input_text = ""

        self.fall_time = 0
        self.fall_speed = 500
        self.key_cooldown = 0
        self.key_cooldown_max = 10

    def load_font(self, size, bold=False):
        font_paths = [
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\simsunb.ttf",
            r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
            r"C:\Windows\Fonts\NotoSerifSC-VF.ttf"
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = pygame.font.Font(font_path, size)
                    font.set_bold(bold)
                    return font
                except Exception:
                    continue
        try:
            return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.SysFont(None, size)

    def reset_game(self):
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
        shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_piece = [row[:] for row in SHAPES[shape_index]]
        self.current_color = SHAPE_COLORS[shape_index]
        self.current_piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_piece_y = 0

        if self.check_collision():
            self.game_over = True

    def rotate_piece(self):
        rotated = [[self.current_piece[y][x] for y in range(len(self.current_piece))]
                   for x in range(len(self.current_piece[0]) - 1, -1, -1)]
        original_piece = self.current_piece
        self.current_piece = rotated

        if self.check_collision():
            self.current_piece = original_piece

    def move_piece(self, dx, dy):
        self.current_piece_x += dx
        self.current_piece_y += dy

        if self.check_collision():
            self.current_piece_x -= dx
            self.current_piece_y -= dy
            return False
        return True

    def check_collision(self):
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
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece_x + x
                    grid_y = self.current_piece_y + y
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_color

    def clear_lines(self):
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
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        self.merge_piece()
        self.clear_lines()
        self.spawn_new_piece()

    def draw_grid(self):
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                             (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y),
                             (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + GRID_HEIGHT * BLOCK_SIZE), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                             (GAME_AREA_X, GAME_AREA_Y + y * BLOCK_SIZE),
                             (GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE), 1)

    def draw_piece(self, piece, x, y, color):
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
        title_text = self.large_font.render("俄罗斯方块", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.leaderboard_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)

        self.start_button.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        help_text = self.small_font.render("A/D: Move | W: Rotate | S: Down | Space: Drop", True, GRAY)
        self.screen.blit(help_text, (10, 650))

    def draw_leaderboard(self):
        title_text = self.large_font.render("排行榜", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(title_text, title_rect)

        top_scores = self.leaderboard.get_top(10)
        header = self.font.render("等级  名字  分数  级别", True, WHITE)
        self.screen.blit(header, (20, 70))

        y_offset = 110
        if not top_scores:
            empty_text = self.small_font.render("没有分数记录", True, GRAY)
            self.screen.blit(empty_text, (SCREEN_WIDTH // 2 - 60, y_offset))
        else:
            for idx, entry in enumerate(top_scores[:10], 1):
                score_text = self.small_font.render(
                    f"{idx:2d}.  {entry['name']:<7s}  {entry['score']:>5d}  {entry['level']:>2d}",
                    True, WHITE if idx % 2 == 0 else GRAY
                )
                self.screen.blit(score_text, (20, y_offset))
                y_offset += 35

        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        self.restart_button.draw(self.screen)

        hint_text = self.small_font.render("Press ESC to return", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 110, 670))

    def draw_game(self):
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

        self.draw_grid()

        if self.current_piece:
            self.draw_piece(self.current_piece, self.current_piece_x,
                            self.current_piece_y, self.current_color)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))

        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (10, 90))

    def draw_game_over(self):
        self.draw_game()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)

        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)

        hint_text = self.small_font.render("Press SPACE to save score", True, YELLOW)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)

        return_text = self.small_font.render("Press ESC to return to menu", True, GRAY)
        return_rect = return_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(return_text, return_rect)

    def draw_name_input(self):
        self.screen.fill(BLACK)

        title_text = self.large_font.render("保存分数", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        score_info = self.font.render(f"Score: {self.score} | Level: {self.level}", True, WHITE)
        score_rect = score_info.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(score_info, score_rect)

        label_text = self.font.render("Player Name:", True, WHITE)
        self.screen.blit(label_text, (SCREEN_WIDTH // 2 - 170, 280))

        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 320, 300, 50)
        pygame.draw.rect(self.screen, WHITE, input_rect, 2)
        pygame.draw.rect(self.screen, DARK_GRAY, input_rect)

        input_text = self.font.render(self.name_input_text + ("|" if self.input_active else ""), True, WHITE)
        self.screen.blit(input_text, (input_rect.x + 10, input_rect.y + 10))

        mouse_pos = pygame.mouse.get_pos()
        save_button = Button(SCREEN_WIDTH // 2 - 160, 420, 140, 40, "Save", self.font)
        skip_button = Button(SCREEN_WIDTH // 2 + 20, 420, 140, 40, "Skip", self.font)

        save_button.check_hover(mouse_pos)
        skip_button.check_hover(mouse_pos)

        save_button.draw(self.screen)
        skip_button.draw(self.screen)

        hint_text = self.small_font.render("输入你的名字", True, GRAY)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 130, 250))

    def restart(self):
        self.reset_game()
        self.game_state = "playing"

    def update(self):
        if self.game_state != "playing" or self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = current_time

    def run(self):
        running = True
        self.game_state = "menu"

        while running:
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
                        elif event.key == pygame.K_r:
                            self.restart()
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"

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

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
