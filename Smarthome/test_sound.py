import pygame
import time

# 초기화
pygame.mixer.init()

# 소리 파일 로드 (여기서는 기본 비프 사운드를 사용합니다)
pygame.mixer.Sound('path/to/your/soundfile.wav').play()

# 잠시 대기
time.sleep(2)  # 2초 동안 소리 재생

# 종료
pygame.mixer.quit()
