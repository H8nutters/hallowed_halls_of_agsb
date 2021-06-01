import pygame, random, math, time
import data.modules.noise as noise
from pygame.locals import *
from abc import ABC, abstractmethod


#-------------class for objects that use physics------------#
class physics_obj:

  def __init__(self, rect):
    self.rect = rect
    self.collision_types = {"top":False,
                            "bottom":False,
                            "right":False, 
                            "left":False}

  #-------------positions the object as per its collisions-------------#
  def collisions(self, movement, platforms, entity_move_x, entity_move_y, display, scroll, dt, assign_self, assign_rect, set_onground):
    entity_move_x(dt)
    assign_rect()
    collision_list = self.collision_test(platforms)
    self.collision_types = {"top": False,
                            "bottom": False, 
                            "right": False,                               #rect at last ground pos(assign self issue) DT BREAKS PHYSICS
                            "left": False}
    for block in collision_list:
      if movement[0] > 0:
        self.rect.right = block.left
        self.collision_types["right"] = True
      elif movement[0] < 0:
        self.rect.left = block.right
        self.collision_types["left"] = True
      assign_self()
    entity_move_y(dt)
    assign_rect()
    self.collision_list = self.collision_test(platforms)
    self.collision_types = {"top": False,
                            "bottom": False, 
                            "right": False, 
                            "left": False}
    for block in collision_list:
      if movement[1] > 0:
        self.rect.bottom = block.top
        self.collision_types["bottom"] = True
      elif movement[1] < 0:
        self.rect.top = block.bottom
        self.collision_types["top"] = True
      assign_self()
    pygame.draw.rect(display, (200,0,0), (self.rect.x-scroll[0], self.rect.y-scroll[1], self.rect.w, self.rect.h), 10)
    
  #-------------checks for collisions---------------#
  def collision_test(self, obj_list):
    collision_list = []
    for obj in obj_list:
      if obj.colliderect(self.rect):
        collision_list.append(obj)
    return collision_list

#-------------class for entities------------#
class entity:

  def __init__(self, x, y, w, h, e_type, hp):
    self.position = pygame.math.Vector2(x,y)
    self.rect = pygame.Rect(self.position.x, self.position.y, w, h)
    self.type = e_type  # used for animations
    self.action = "idle"
    self.img = None
    self.isflip = False
    self.animation_frame = 0
    self.obj = physics_obj(self.rect)
    self.animation_frames = {}
    self.animation_database = {}
    self.particle_colour = None
    self.particle_timer = 0
    self.particles = []
    self.direction = "left"
    self.hp = hp
    
  #----------gathers entity animation frames and processes them----------#
  def load_animation(self, animation_name, frame_durations):
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
      animation_frame_id = animation_name + "_" + str(n)
      img_loc = "data/entities/" + self.type + "/" + \
          animation_name + "/" + animation_frame_id + ".png"
      animation_image = pygame.image.load(img_loc).convert_alpha()
      self.animation_frames[animation_frame_id] = animation_image.copy()
      for i in range(frame):
        animation_frame_data.append(animation_frame_id)
      n += 1
    return animation_frame_data

  #-----------assigns entity animations to a term for them in a dictionary----------#
  def animations(self, **animation):
    for animation, duration in animation.items():
      self.animation_database[animation] = self.load_animation(
          animation, duration)
      
  #----------sets entity animation to what needed if entity is not already in the middle of that animation---------#
  def set_action(self, new_action):
    if self.action != new_action:
      self.action = new_action
      self.animation_frame = 0

  #------------update entity rects-----------#
  def update_rects(self):
    self.rect = self.obj.rect
    self.position.x, self.position.y = self.rect.x, self.rect.y 
    
  #---------updates the entity animation by changing the frame----------#
  def change_frame(self, amount):
    self.animation_frame += amount
    if self.animation_frame >= len(self.animation_database[self.action]):
      self.animation_frame = 0

  #----------updates entity dimensions as per frame---------#
  def set_dimensions(self):
    self.rect.w, self.rect.h = self.img.get_size()
  
  #--------------updates particle timer------------#
  def change_particle_timer(self): 
    if self.particle_timer > 0:
      self.particle_timer -= 1
      
  #-----------handles entity movement + particles on feet----------#
  def move(self, movement, platforms, scroll, display, entity_move_x, entity_move_y, dt, assign_self, assign_rect, set_onground):
    collision_types = self.obj.collisions(movement, platforms, entity_move_x, entity_move_y, display, scroll, dt, assign_self, assign_rect, set_onground)
    self.update_rects()
    self.change_particle_timer()
    render_particles(display, self.particles, movement)
    if self.obj.collision_types["bottom"] == True:
      if movement[0] != 0:
        if self.particle_timer == 0:
          generate_particles(self.particles, 7, self.rect.x-scroll[0], self.rect.y-scroll[1]+self.rect.h, -1, -2, self.particle_colour, self.direction, self.rect.w)
          self.particle_timer = 15

  #---------handles entity flipping---------#
  def set_flip(self, boolean):
    self.isflip = boolean  # used in game code to change flip status
    self.set_direction()

  def flip(self, img, boolean=True):
    return pygame.transform.flip(img, boolean, False)   # used in engine to flip entity img

  #--------handles which direction an entity is facing---------#
  def set_direction(self):
    if self.isflip:
      self.direction = "right"
    else:
      self.direction = "left"

  #----------displays entity-----------#
  def display(self, surface, scroll):
    img = self.animation_database[self.action][self.animation_frame]
    self.img = self.flip(self.animation_frames[img], self.isflip).copy()
    self.set_dimensions()
    surface.blit(self.img, ((int(self.position.x)-scroll[0]), int(self.position.y)-scroll[1]))
    pygame.draw.rect(surface, (255,0,255), (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h), 4)
    
#----------------------child class of entity 'player' for further physics-------------------------#
class player(entity):
  
  def __init__(self, x, y, w, h, e_type, hp):
    self.moving = {"right":False,
                   "left":False,}
    self.state = {"is_jumping":False,
                  "on_ground":False}
    self.gravity = .35
    self.friction = -.14            #negative to simulate opposite force on player
    self.position = pygame.math.Vector2(0,0)            #store position seperately so that calculations do not mess up in making it int every frame (blit pos requires int)
    self.velocity = pygame.math.Vector2(0,0)
    self.acceleration = pygame.math.Vector2(0, self.gravity)
    super().__init__(self.position.x, self.position.y, w, h, e_type, hp)       
      
  def horizontal_movement(self, dt):
    self.position.x = self.rect.x
        
    self.acceleration.x = 0
    if self.moving["left"]:
      self.acceleration.x -= 1
    elif self.moving["right"]:
      self.acceleration.x += 1
    self.acceleration.x += self.velocity.x * self.friction          #multiplied by friction (-number) to simulate a force on the opposite direction
    self.velocity.x += self.acceleration.x * dt           #newton's equations of motion (v = u + at)
    self.limit_velocity(4)
    self.position.x += self.velocity.x * dt + (self.acceleration.x * .5) * (dt * dt)          #newton's equations of motion (s = ut + 1/2(at ^ 2))
    self.rect.x = int(self.position.x)

  def vertical_movement(self, dt):
    self.position.y = self.rect.y
    self.velocity.y += self.acceleration.y * dt   #newton's equations of motion (v = u + at)
    if self.velocity.y > 7:
      self.velocity.y = 7
    self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)          #newton's equations of motion (s = ut + 1/2(at ^ 2))
    if self.state["on_ground"]:
      self.velocity.y = 0    
    self.rect.y = int(self.position.y)

  def limit_velocity(self, max_vel):
    min(-max_vel, max(self.velocity.x, max_vel))
    if abs(self.velocity.x) < .01:
      self.velocity.x = 0

  def move_x(self, dt):
    self.horizontal_movement(dt)
        
  def move_y(self, dt):
    self.vertical_movement(dt)

  def assign_rect(self):
    self.obj.rect = self.rect
    
  def assign_self(self):
    self.rect = self.obj.rect  
    if self.obj.collision_types["bottom"]:
      self.state["on_ground"] = True
      self.velocity.y = 0        
    self.set_onground()
    #print(self.state["on_ground"], self.obj.collision_types["bottom"])
    if self.obj.collision_types["right"]:
      self.moving["right"] = False
      self.velocity.x = 0
    if self.obj.collision_types["left"]:
      self.moving["left"] = False
      self.velocity.x = 0
        
  def set_onground(self):
    self.state["on_ground"] = self.obj.collision_types["bottom"]
    
  def jump(self):
    if self.state["on_ground"]:
      self.state["is_jumping"] = True
      self.velocity.y -= 8
      self.state["on_ground"] = False
      
  def assign(self):
    self.position.x = self.rect.x
    self.position.y = self.rect.y

  def update(self, dt, platforms, scroll, display):
    super().move(self.velocity, platforms, scroll, display, self.move_x, self.move_y, dt, self.assign_self, self.assign_rect, self.set_onground)
    

#-----------------class for camera------------------#
class camera:
  def __init__(self, player, display):
    self.player = player
    self.offset = pygame.math.Vector2(0,0)
    self.offself_float = pygame.math.Vector2(0,0)
    self.display = display
    self.constant = pygame.math.Vector2(0,0)
    
    def set_method(self, method):
      self.method = method
      
    def scroll(self):
      self.method.scroll()
    
class camscroll(ABC):
  def __init__(self, camera, player):
    self.camera = camera
    self.player = player
    
  @abstractmethod
  def scroll(self):
    pass
#------------------handles particles-------------------#   
def render_particles(display, particles, e_movement):
    for particle in particles:
      particle.change_particle(display, e_movement)
      if particle.radius <= 0:
        particles.remove(particle)

def generate_particles(particles_list, particle_amount, x, y, x_change, y_change, colour, direction, w):
  for particle in range(particle_amount):
    particle = particles(x + random.randint(1,12), y, x_change, y_change, colour)
    if direction == "left":
      particle.position.x += w
    particles_list.append(particle)

class particles:

  def __init__ (self, x, y, x_change, y_change, colour):
    self.position = pygame.math.Vector2(0,0)
    self.x_change = int(x_change)
    self.y_change = int(y_change)
    self.radius = random.randint(0,40)/10
    self.colour = colour

  def draw(self, display):
    pygame.draw.circle(display, self.colour, (self.position.x, self.position.y), int(self.radius))

  def change_particle(self, display, e_movement):
    if e_movement[0] < 0:
      self.position.x -= self.x_change
    elif e_movement[0] > 0:
      self.position.x += self.x_change
    
    self.position.y += self.y_change
    self.radius -= 0.1
    self.y_change += 0.1
    
    self.draw(display)

#-------------------handles glowing doors-----------------------#
class interactable_door:

  def __init__(self, x, y, w, h, img, glow_width, glow_colour):
    self.rect = pygame.Rect(x, y, w, h)
    self.glow_width = glow_width
    self.glow_colour = glow_colour
    self.size_change = 0
    self.add_to_change = 1
    self.rects = []
    self.img = img

  def update_rect(self):
    self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)

  def glow_surf(self, display):
    self.size_change += self.add_to_change
    surf = pygame.Surface((self.rect.w+27, self.rect.h+15))
    rect = [45 + self.rect.w/2, 60 + self.rect.h/2]
    pygame.draw.rect(surf, self.glow_colour, (rect[0] - (self.rect.w + self.size_change/2), rect[1] - (self.rect.h + self.size_change/2), self.rect.w + 10+ self.size_change, self.rect.h + 10+self.size_change), self.glow_width+self.size_change)
    if self.size_change == 15 or self.size_change == 0:
      self.add_to_change *= -1    
    surf.set_colorkey((0, 0, 0))
    return surf

  def draw(self, scroll, display):
    pygame.draw.rect(display, (20, 20, 20), (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h), self.glow_width)
    display.blit(self.glow_surf(display), (self.rect.x - 13 - scroll[0], self.rect.y - 13 - scroll[1]),special_flags=BLEND_RGBA_ADD)

  def display(self, scroll, display):
    display.blit(self.img, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
    self.draw(scroll, display)

def run_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

#-------------randomly generates terrain--------------#
def generate_chunk(CHUNK_SIZE, x, y, index_1, index_2, flat = True):
  chunk_data = []
  #gets co-ordinates of each tile#
  for y_pos in range(CHUNK_SIZE):
    for x_pos in range(CHUNK_SIZE):
      target_x = x * CHUNK_SIZE + x_pos
      target_y = y * CHUNK_SIZE + y_pos     # gets tile position based off of what chunk it is - e.g chunk is (2,2)(second chunk on both x and y) so it finds co-ords
      tile_type = 0  # nothing
      if not flat:
        height = int(noise.pnoise1(target_x * 0.1, repeat=99999999)*1.75)   # 1d noise multiplied by 0.1 to spread the bumps out # noise gives small value so *5 make larger to get nicer mountains/hills
        if target_y > 9 - height:
          #if random.randint(1,10) == 1:
            #tile_type = 3       #concrete with bones
          #else:
          tile_type = index_2  # darker concrete
        elif target_y == 9 - height:
          tile_type = index_1  # lighter concrete
      elif flat:
        if target_y > 9:
          tile_type = index_2
        elif target_y == 9:
          tile_type = index_1
          
      if tile_type != 0:
        chunk_data.append([[target_x, target_y], tile_type])

  return chunk_data

  #--------------loads terrain in----------------#
def infinite_terrain(display, scroll, tile_index, CHUNK_SIZE, tile_size, index_1, index_2, flat = True):
  tile_rects = []
  game_map = {}
  for y in range(6):  # 6 chunks in display (rounded up) at a time
    for x in range(10):  # 10 chunk in display (rounded up) at a time
        target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*tile_size)))
        target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*tile_size)))  # what is on the display/pixels in chunk
        target_chunk = str(target_x) + ";" + str(target_y)  # puts the chunk in form (chunk number (x));(chunk number(y))
        if target_chunk not in game_map:
          game_map[target_chunk] = generate_chunk(CHUNK_SIZE, target_x, target_y, index_1, index_2, flat) # adds a keyword "target_chunk"(chunk_x;chunk_y):[[(tile_in_chunk_x),(tile_in_chunk_y)], tile_type] with the second value being repeated for every tile in the chunk
        for tile in game_map[target_chunk]:
          display.blit(tile_index[tile[1]], (tile[0][0]*tile_size-scroll[0], tile[0][1]*tile_size-scroll[1]))  # renders the tile image with the x co-ord being the target_x and the y being the target_y 
          if tile[1] in [index_1, index_2]:
            tile_rects.append(pygame.Rect(tile[0][0]*tile_size, tile[0][1]*tile_size, tile_size, tile_size))  # adds a rect to the tile_rects list with the x being target_x * tile_size, y being target_y * tile_size
  return tile_rects

#----------calculates floor level---------#
def get_floor_level(floor_level, tile_size):
  return floor_level * tile_size

#--------------handles transitions between scenes-----------#
class transitions:
  
  def __init__(self,display, WINDOW_SIZE, colour_to_fade_into):
    self.display = display
    self.WINDOW_SIZE = WINDOW_SIZE
    self.transition = None
    self.alpha = 1
    self.alpha_change = 3
    self.colour = colour_to_fade_into
    self.surface = pygame.Surface((self.WINDOW_SIZE))
    self.surface.fill(self.colour)


  def set_transition(self):
    if not self.transition:
      self.alpha = 1      
      self.transition = "out"

  def update_change(self):
    if self.alpha <= 0:
      self.alpha_change *= -1      
      self.transition = None
    elif self.alpha >= 255:
      self.transition = "in"
      self.alpha_change *= -1
          
  def run(self, display):
    if self.transition:
      self.update_change()
      self.alpha += self.alpha_change 
      self.surface.set_alpha(self.alpha)
      display.blit(self.surface, (0,0))
      pygame.display.update()
      pygame.time.delay(13)
      
#----------handles speech with text box-----------#
def dialogue(display, speaking, font, name_colour, text_colour, FPS, time, text_timer, name, text, text_box, text_box_pos = (100,480)):
  name_font = pygame.font.Font(font, 30)
  text_font = pygame.font.Font(font, 24)
  name = name_font.render(str(name), True, name_colour)
  display.blit(text_box, text_box_pos)

  if text_timer[0] != time*60:  # timer in seconds for how long text should stay on screen for
    # render text based on where it is in the list (text_timer[1] starts at 0)
    speech = text_font.render(text[text_timer[1]], True, text_colour)
    text_timer[0] += 1  # adds to timer every iteration
    speaking = True

    text_box_rect = text_box.get_rect(topleft=(100, 480))
    display.blit(name, (text_box_rect.x+40, text_box_rect.y+12))
    display.blit(speech, (text_box_rect.x+30, text_box_rect.y+90))
  else:
    text_timer[0] = 0
    # if the amount of seconds that a line has to be displayed for is up, it resets the timer and adds to the list number
    text_timer[1] += 1

  # if you get to the end of the list the list number gets reset to zero and the speech stops using speaking var
  if text_timer[1] >= len(text):
    text_timer[1] = 0
    speaking = False
  else:
    speaking = True

  return speaking, text_timer


def basic_text(display, font, colour, size, loc, scroll, text, lines):
  new_text = text.split(" ")
  length_to_split = (len(new_text))//lines
  split_text = []
  length_remainder = (len(new_text)) % lines

  while len(new_text) != 0:
    text_to_append = []
    for i in range(length_to_split):
      text_to_append.append(new_text[0])
      new_text.remove(new_text[0])
    split_text.append(text_to_append)

    if len(new_text) == length_remainder:
      text_to_append = []
      for i in range(length_remainder):
        text_to_append.append(new_text[0])
        new_text.remove(new_text[0])
      split_text.append(text_to_append)

  font = pygame.font.Font(font, size)
  x = 0
  for i in split_text:
    if i != []:
      text_to_render = str(i)
      text_to_render = text_to_render.replace("[", "")
      text_to_render = text_to_render.replace("]", "")
      text_to_render = text_to_render.replace("'", "")
      text_to_render = text_to_render.replace(",", "")
      render_text = font.render(text_to_render, True, colour)
      loc[1] += x*size
      display.blit(render_text, (loc[0]-scroll[0], loc[1]-scroll[1]))
      if x == 0:
        x += 1

