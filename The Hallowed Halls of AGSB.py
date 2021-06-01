#-------------import and init--------------#
import pygame, random, json, sys, time, math
import data.modules.noise as noise
import data.engine as e
from pygame.locals import *
clock = pygame.time.Clock()
pygame.init()

#------------reads and writes game data----------#
with open("data/data.json") as f:     #opens and closes file
  data = json.load(f)             #stores game data in dictionary 'data'

def save_data():
  with open("data/data.json", "w") as f:
    json.dump(data, f)        #overwrites old data with new data 
    
#------------make pygame window and set basics----------#
pygame.display.set_caption("The Hallowed Halls of AGSB")
pygame.display.set_icon(pygame.image.load("data/images/icon.png"))
WINDOW_SIZE = (1200, 700)

screen = pygame.display.set_mode((WINDOW_SIZE), pygame.RESIZABLE)
display =  pygame.Surface((1200,700))

#-------------variables----------------#
FPS_font = pygame.font.Font("data/fonts/Little Orion.ttf", 32)
CHUNK_SIZE = 8
true_scroll = [0, 0]
clock = pygame.time.Clock()
transition = e.transitions(display, WINDOW_SIZE, (0,0,0))
particle_colour = (0, 0, 0)
h_bar_colours = [(83,15,31), (97,18,37), (122,21,46), (143,28,56), (159,34,64), (181,44,77)]  #health bar colours 
name = data["name"]

#--------------load background images---------------#
cloud_1 = pygame.transform.scale((pygame.image.load("data/images/south_yard/cloud_1.png")), (180, 58)).convert_alpha()
school = pygame.image.load("data/images/south_yard/school.png").convert_alpha()
text_box = pygame.image.load("data/images/text_box.png").convert_alpha()
door = pygame.image.load("data/images/south_yard/door.png").convert_alpha()
science_background = pygame.image.load("data/images/science_block/background.png").convert_alpha()

#--------South Yard variables-------#
tim_speaking = False
text_timer = [0, 0]
south_yard_barriers = [[-1079, 0, 10, 10000], [1150, 0, 10, 10000]]
south_yard_door = e.interactable_door(908, 332, 75, 100, door, 5, (0,255,0))

#--------Hallway variables--------#
s_y_return_door = e.interactable_door(0, 330, 75, 100, door, 5, (0,255,0))
science_door = e.interactable_door(400, 330, 75, 100, door, 5, (0,0,255))

#--------Science block variables--------#
science_hallway_return_door = e.interactable_door(0, 330, 75, 100, door, 5, (74, 74, 74))

#-------------creates player using engine and makes variables for it-------------#
player = e.player(100, 0, 43, 64, "player", 6)
player.animations(run=[4, 4, 4, 4, 4, 4], idle=[40, 8, 8, 8, 8])
moving = {"right": False,
          "left": False,
          "jump": False
          }

#------------------handles health and health bar------------------#
def change_hp_bar(colour, new_c = None):
  img_copy = pygame.Surface(health_bar.get_size())
  if new_c:                                           #changes/removes colours from health bar
    img_copy.fill(new_c)
  health_bar.set_colorkey(colour)
  img_copy.set_colorkey((0,0,0))
  img_copy.blit(health_bar, (0, 0))
  return img_copy
  
def update_hp():
  health_bar = pygame.image.load("data/gui/health_bar.png").convert_alpha()
  if player.hp >= 0:
    colorkey_list = [i for i in h_bar_colours[player.hp:]]        #handles what the health bar shouls show depending on player hp
  else:
    colorkey_list = []
    print("out of health")
    player.hp = 6
  return colorkey_list, health_bar

#------------creates npc using engine------------#
npc = e.entity(-1085, 325, 50, 37, "npc", 0)
npc.animations(idle=[8, 8, 8, 8, 8, 8, 8, 8])


#----randomly generates clouds for south yard----#
clouds = []
for i in range(10):
  cloud = [random.randint(-1000, 1200), random.randint(10, 100)]  #randomly generates clouds
  clouds.append(cloud)

#----------loads tiles and puts them into an index----------#
game_map = {}

concrete_1_img = pygame.transform.scale((pygame.image.load("data/images/south_yard/terrain/concrete_1.png").convert_alpha()), (48, 48))
concrete_2_img = pygame.transform.scale((pygame.image.load("data/images/south_yard/terrain/concrete_2.png").convert_alpha()), (48, 48))
concrete_3_img = pygame.transform.scale((pygame.image.load("data/images/south_yard/terrain/concrete_3.png").convert_alpha()), (48, 48))
wood_floor_img = pygame.transform.scale((pygame.image.load("data/images/hallway/terrain/wooden_floor.png").convert_alpha()), (48, 48))
tile_index = {1: concrete_1_img,
              2: concrete_2_img,
              3: concrete_3_img,
              4: wood_floor_img
              }

#--------------South Yard-------------#
def south_yard():
  
  global tim_speaking, text_timer
  
  #-----------calculates floor level-------------#
  floor_level = e.get_floor_level(1, 48)
 
  #------------makes display move with player-------------#
  if (player.rect.x+(WINDOW_SIZE[0]/2+4)) > 1260 or (player.rect.x-(WINDOW_SIZE[0]/2+4)) < -1175:
    true_scroll[1] += (player.rect.y-true_scroll[1]-(WINDOW_SIZE[1]/2+4 + floor_level))/20
  else:
    true_scroll[0] += (player.rect.x-true_scroll[0]-(WINDOW_SIZE[0]/2+4))/20
    true_scroll[1] += (player.rect.y-true_scroll[1]-(WINDOW_SIZE[1]/2+4 + floor_level))/20
  scroll = true_scroll.copy()
  # copy of true scroll in int form as some movements don't work well with decimals
  scroll[0] = int(scroll[0])
  scroll[1] = int(scroll[1])

  #-----------displays all images---------#
  display.fill((118, 156, 164))
  for i in clouds:
    display.blit(cloud_1, (i[0]-scroll[0]*0.5, i[1]-scroll[1]*0.5))
  display.blit(school, (450-scroll[0], -40-scroll[1]))

  #--------------loads terrain in----------------#
  tile_rects = e.infinite_terrain(display, scroll, tile_index, CHUNK_SIZE, 48, 1, 2, flat = False)

  #----------loads South Yard barriers in-----------#
  for i in south_yard_barriers:
    barrier_rect = pygame.Rect(i[0], i[1], i[2], i[3])
    tile_rects.append(barrier_rect)
    
  #----------handles interactions----------#
  if player.rect.x + (WINDOW_SIZE[0] + 100) >= south_yard_door.rect.x or player.rect.x - (WINDOW_SIZE[0] + 100) <= south_yard_door.rect.x:
    south_yard_door.display(scroll, display)
    #-----------calculates floor level-------------#
  floor_level = e.get_floor_level(9, 48)
  
  #-----------handles help messages------------#
  if player.rect.x - 250 <= npc.rect.x:
    e.basic_text(display, "data/fonts/Little Orion.ttf", (212, 175, 94),
                 40, [-1000, 198], scroll, "Press 'E' to interact with NPCs!", 3)

  if player.rect.x + 250 >= south_yard_door.rect.x:
    e.basic_text(display, "data/fonts/Little Orion.ttf", (31, 19, 37), 40,
                 [south_yard_door.rect.x - 25, south_yard_door.rect.y - 150], scroll, "Press 'E' to interact with doors!", 3)
    
  if tim_speaking:
    tim_speaking, text_timer = e.dialogue(display, tim_speaking, "data/fonts/04B_30__.TTF",(98, 19, 19), (0, 0, 0), FPS, 1.75, text_timer, "Tim", [f"Hi there {name}, I'm Tim", "Are you heading over to the grammar?",
                "I wouldn't go over there if I were you", "*whispers* I heard the year 7's are doing PE"], text_box)
    
  npc.set_action("idle")
  npc.change_frame(1)
  npc.display(display, scroll)
  
  return scroll, tile_rects

#-------------Hallway--------------#
def hallway():
  
  #-----------calculates floor level-------------#
  floor_level = e.get_floor_level(3, 48)
  
  #------------makes display move with player-------------#
  if (player.rect.x-(WINDOW_SIZE[0]/2+4)) < -504:
    true_scroll[1] += (player.rect.y-true_scroll[1]-(WINDOW_SIZE[1]/2+4 + floor_level))/20
  else:
    true_scroll[0] += (player.rect.x-true_scroll[0]-(WINDOW_SIZE[0]/2+4))/20
    true_scroll[1] += (player.rect.y-true_scroll[1]-(WINDOW_SIZE[1]/2+4 + int(floor_level)))/20
  scroll = true_scroll.copy()   # copy of true scroll in int form as some movements don't work well with decimals
  scroll[0] = int(scroll[0])
  scroll[1] = int(scroll[1])

  #-----------displays all images------------#
  display.fill((45, 44, 48))

  #----------handles doors-----------#
  if player.rect.x + (WINDOW_SIZE[0] + 100) >= s_y_return_door.rect.x or player.rect.x - (WINDOW_SIZE[0] + 100) <= s_y_return_door.rect.x:    #checks if door is in frame 
    s_y_return_door.display(scroll, display)
  if player.rect.x + (WINDOW_SIZE[0] + 100) >= science_door.rect.x or player.rect.x - (WINDOW_SIZE[0] + 100) <= science_door.rect.x:    #checks if door is in frame 
    science_door.display(scroll, display)
    
  #---------handles door text---------#
  e.basic_text(display, "data/fonts/Little Orion.ttf", (31, 19, 37), 40, [s_y_return_door.rect.x-30, s_y_return_door.rect.y-115], scroll, "Return to South Yard", 2)    
  e.basic_text(display, "data/fonts/Little Orion.ttf", (31, 19, 37), 40, [science_door.rect.x-30, science_door.rect.y-150], scroll, "Go to the science block", 2)    
  
  #--------------loads terrain in----------------#
  tile_rects = e.infinite_terrain(display, scroll, tile_index, CHUNK_SIZE, 48, 4, 4)
  return scroll, tile_rects

def science_block():
  
  #-------------calculates floor level--------------#
  floor_level = e.get_floor_level(3, 48)
  
    #------------makes display move with player-------------#
  true_scroll[0] += (player.rect.x-true_scroll[0]-(WINDOW_SIZE[0]/2+4))/20
  true_scroll[1] += (player.rect.y-true_scroll[1]-(WINDOW_SIZE[1]/2+4 + int(floor_level)))/20
  scroll = true_scroll.copy()   # copy of true scroll in int form as some movements don't work well with decimals
  scroll[0] = int(scroll[0])
  scroll[1] = int(scroll[1])

  #-----------displays all images------------#
  display.fill((85, 100, 104))
  
  #-----------handles doors-----------#
  if player.rect.x + (WINDOW_SIZE[0] + 100) >= science_hallway_return_door.rect.x or player.rect.x - (WINDOW_SIZE[0] + 100) <= science_hallway_return_door.rect.x:    #checks if door is in frame 
    science_hallway_return_door.display(scroll, display)
  #----------loads terrain in----------#
  tile_rects = e.infinite_terrain(display, scroll, tile_index, CHUNK_SIZE, 48, 1, 2)
  
  return scroll, tile_rects

#--------------main loop----------------#
while True:
  
  
  
  #-------------handles time/fps-------------#
  FPS = clock.get_fps()
  dt = clock.tick(FPS) * .001 * 60

  player.particle_colour = (44, 33, 35)

  #------------determines what stage player is on----------#
  if data["current_stage"] == "south_yard":
    scroll, tile_rects = south_yard()
  
  elif data["current_stage"] == "hallway":
    scroll, tile_rects = hallway()
    
  elif data["current_stage"] == "science_block":
    scroll, tile_rects = science_block()
  
  mx, my = pygame.mouse.get_pos()

  #--------------checks for certain events------------#
  
  for event in pygame.event.get():
    if event.type == QUIT:  # closes pygame if the x button is pressed
      save_data()
      pygame.quit()
      sys.exit()
    if event.type == VIDEORESIZE:
      display = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

  #------------player movements true/false------------#
    if event.type == KEYDOWN:

      if event.key == K_d:
        player.moving["right"] = True
      if event.key == K_a:
        player.moving["left"] = True
      if event.key == K_w:
        player.jump()
      if event.key == K_e:
        if data["current_stage"] == "south_yard":
          if player.rect.x - 250 <= npc.rect.x:
            tim_speaking = True           # activates speaking
          if player.obj.rect.colliderect(south_yard_door.rect):
            transition.set_transition()
            data["current_stage"] = "hallway"
            
        elif data["current_stage"] == "hallway":
          if player.obj.rect.colliderect(s_y_return_door.rect):
            transition.set_transition()
            data["current_stage"] = "south_yard"
            
          if player.obj.rect.colliderect(science_door.rect):
            transition.set_transition()
            data["current_stage"] = "science_block"
            
        elif data["current_stage"] == "science_block":
          if player.obj.rect.colliderect(science_hallway_return_door):
            transition.set_transition()
            data["current_stage"] = "hallway"
            
            
      
      if event.key == K_f:
        player.hp -= 1 
      if event.type == pygame.KEYDOWN:
        if event.unicode.isprintable():
          print(event.unicode)
      if event.key == K_t:
        player.hp += 1
    if event.type == KEYUP:
      if event.key == K_d:
        player.moving["right"] = False
      if event.key == K_a:
        player.moving["left"] = False
      if event.key == K_w:
        player.jump()
    if event.type == MOUSEBUTTONDOWN:
      print(mx,my) 

  #-------------handles player movement-----------#
  if player.velocity.x == 0:
    player.set_action("idle")
  if player.velocity.x > 0:
    player.set_flip(True)
  if abs(player.velocity.x) > 1:
    player.set_action("run")
  if player.velocity.x < 0:
    player.set_flip(False)
  
  #-----------handles gui-----------#
  colorkey_list, health_bar = update_hp()
  for i in colorkey_list:
    health_bar = change_hp_bar(i)
  display.blit(health_bar, (10,10)) 
  display.blit(FPS_font.render(f"FPS {str(round(FPS))}", True, (0,0,0)), (1115, 10)) 

  #--------handles entity update features-------#
  player.update(dt, tile_rects, scroll, display)
  player.change_frame(1)
  player.display(display, scroll)
  
  #-------------updates display---------------#
  screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    
  #--------handles transitions-------#  
  if transition.transition:
    while transition.transition == "out":
      transition.run(screen) 
    transition.run(screen)
    
  pygame.display.update()  
 
