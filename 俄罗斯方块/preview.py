import pygame
from constants import WHITE, GRAY, BLACK


class NextPiecePreview:
    def __init__(self, x, y, width, height, block_size, label_font):
        self.rect = pygame.Rect(x, y, width, height)
        self.block_size = block_size
        self.label_font = label_font

    def draw(self, surface, piece, color):
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

        label = self.label_font.render("NEXT", True, WHITE)
        surface.blit(label, (self.rect.x + 10, self.rect.y + 10))

        if not piece:
            return

        preview_area = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 40,
            self.rect.width - 20,
            self.rect.height - 50
        )
        pygame.draw.rect(surface, GRAY, preview_area)

        total_width = len(piece[0]) * self.block_size
        total_height = len(piece) * self.block_size
        offset_x = preview_area.x + (preview_area.width - total_width) // 2
        offset_y = preview_area.y + (preview_area.height - total_height) // 2

        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        offset_x + col_idx * self.block_size,
                        offset_y + row_idx * self.block_size,
                        self.block_size - 2,
                        self.block_size - 2
                    )
                    pygame.draw.rect(surface, color, rect)
                    pygame.draw.rect(surface, WHITE, rect, 2)
