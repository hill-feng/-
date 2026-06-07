import pygame
import sys

# 初始化
pygame.init()

# 设置窗口
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("简单键盘测试")

# 字体
font = pygame.font.Font(None, 48)

print("简单键盘测试程序")
print("请点击窗口，然后按任意键")
print("按 ESC 退出程序")

clock = pygame.time.Clock()
last_key = None
running = True

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            else:
                key_name = pygame.key.name(event.key)
                print(f"检测到按键: {key_name}")
                last_key = key_name
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("鼠标点击检测到")
    
    # 绘制
    screen.fill((0, 0, 0))
    
    # 标题
    title = font.render("键盘测试", True, (255, 255, 255))
    screen.blit(title, (320, 100))
    
    # 提示
    if last_key:
        result = font.render(f"按下了: {last_key}", True, (0, 255, 0))
        screen.blit(result, (280, 250))
    else:
        prompt = font.render("请按任意键", True, (255, 255, 0))
        screen.blit(prompt, (300, 250))
    
    # 说明
    info = font.render("ESC 退出", True, (128, 128, 128))
    screen.blit(info, (340, 500))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()