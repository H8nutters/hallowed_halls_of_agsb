#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys

# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((500, 500),0,32)

tree_img = pygame.image.load('tree.png').convert()

def palette_swap(surf, old_c, new_c):
    img_copy = pygame.Surface(tree_img.get_size())
    img_copy.fill(new_c)
    surf.set_colorkey(old_c)
    img_copy.blit(surf, (0, 0))
    return img_copy

tree_img = palette_swap(tree_img, (11, 70, 97), (17, 11, 96))
tree_img = palette_swap(tree_img, (15, 106, 99), (83, 32, 145))
tree_img = palette_swap(tree_img, (35, 152, 77), (167, 65, 131))
tree_img = palette_swap(tree_img, (154, 209, 59), (205, 124, 97))
tree_img.set_colorkey((0, 0, 0))

# Loop ------------------------------------------------------- #
while True:
    
    # Background --------------------------------------------- #
    screen.fill((0,0,0))

    screen.blit(pygame.transform.scale(tree_img, (tree_img.get_width() * 3, tree_img.get_height() * 3)), (50, 50))
    
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
                
    # Update ------------------------------------------------- #
    pygame.display.update()
    mainClock.tick(60)
    
