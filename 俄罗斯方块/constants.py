import pygame

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
