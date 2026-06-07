import pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # 打印按下的按键名称
            print(f"按下了: {pygame.key.name(event.key)}")
            
            screen.fill((0,0,0))
            text = font.render(f"Pressed: {pygame.key.name(event.key)}", True, (255,255,255))
            screen.blit(text, (50, 100))
            pygame.display.flip()

pygame.quit()