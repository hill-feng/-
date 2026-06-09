import pygame
from constants import WHITE, LIGHT_GREEN


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
        color = (255, 255, 0) if self.hover else self.color
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
