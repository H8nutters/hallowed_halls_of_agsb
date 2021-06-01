import pygame, random, noise, json, sys, time, math
import data.engine as e
from pygame.locals import *
clock = pygame.time.Clock()
pygame.init()
pygame.display.set_icon(pygame.image.load("data/images/icon.png"))
WINDOW_SIZE = (1200, 700)

screen = pygame.display.set_mode((WINDOW_SIZE), pygame.RESIZABLE)
display =  pygame.Surface((1200,700))
FPS_font = pygame.font.Font("data/fonts/Little Orion.ttf", 80)

while True: 
  
  FPS = clock.get_fps()
  dt = clock.tick(FPS) * .001 * 60
  for event in pygame.event.get():
    if event.type == QUIT:  # closes pygame if the x button is pressed
      pygame.quit()
      sys.exit()
      
  screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))  
  display.fill((0,0,0))
  display.blit(FPS_font.render(f"FPS {str(int(FPS))}", True, (255,255,255)), (500, 300)) 
  
  pygame.display.update()  
  