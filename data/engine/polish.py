import pygame, random
from pygame.locals import *



#------------------handles particles-------------------#   
def render_particles(display, particles, e_movement):
    for particle in particles:
      particle.change_particle(display, e_movement)       #updates particles in particle list
      if particle.radius <= 0:
        particles.remove(particle)                        #removes unseeable particles from list

def generate_particles(particles_list, particle_amount, x, y, x_change, y_change, colour, direction, w):
  for particle in range(particle_amount):
    particle = particles(x + random.randint(1,12), y, x_change, y_change, colour)       #appends data for small circles into particle list
    if direction == "left":                   
      particle.position.x += w      #if entity is moving left, changes where particles blit to other side of player
    particles_list.append(particle)

class particles:

  def __init__ (self, x, y, x_change, y_change, colour):
    self.position = pygame.math.Vector2(0,0)
    self.x_change = int(x_change)             
    self.y_change = int(y_change)
    self.radius = random.randint(0,40)/10
    self.colour = colour

  def draw(self, display):
    pygame.draw.circle(display, self.colour, (self.position.x, self.position.y), int(self.radius))    #blits particles based on data

  def change_particle(self, display, e_movement):
    if e_movement[0] < 0:
      self.position.x -= self.x_change             
    elif e_movement[0] > 0:
      self.position.x += self.x_change             #moves particles left/right based on entity location
    
    self.position.y += self.y_change
    self.radius -= 0.1                        #makes particle smaller every iteration
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
    self.rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)     #displays glowing rect

  def glow_surf(self, display):
    self.size_change += self.add_to_change
    surf = pygame.Surface((self.rect.w+27, self.rect.h+15))       #creates surface slightly bigger than rect to blend onto
    rect = [45 + self.rect.w/2, 60 + self.rect.h/2]             #gets rect centre with an offset
    pygame.draw.rect(surf, self.glow_colour, (rect[0] - (self.rect.w + self.size_change/2), rect[1] - (self.rect.h + self.size_change/2), self.rect.w + 10+ self.size_change, self.rect.h + 10+self.size_change), self.glow_width+self.size_change)   
    if self.size_change == 15 or self.size_change == 0:                                                                                           #displays rect based off centre point with offset. Changes width to make it bob back and forth
      self.add_to_change *= -1                              #flips the width change the other way if it gets too small/too big
    surf.set_colorkey((0, 0, 0))
    return surf

  def draw(self, scroll, display):
    pygame.draw.rect(display, (20, 20, 20), (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h), self.glow_width)    #adds dark grey border rect for nice effect
    display.blit(self.glow_surf(display), (self.rect.x - 13 - scroll[0], self.rect.y - 13 - scroll[1]),special_flags=BLEND_RGBA_ADD)           #blits rect on surface with blend flag to give glow effect

  def display(self, scroll, display):
    display.blit(self.img, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
    self.draw(scroll, display)                  #displays all images

#----------------decorators---------------#
def run_once(func):
    def wrapper(*args, **kwargs):               
        if not wrapper.has_run:
            wrapper.has_run = True                #checks if a function has run and allows/disallows it to run based on that
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


#--------------handles transitions between scenes-----------#
class transitions:
  
  def __init__(self,display, WINDOW_SIZE, colour_to_fade_into):
    self.display = display
    self.WINDOW_SIZE = WINDOW_SIZE
    self.delay = 2.5
    self.delay_timer = 0                            #creates small delay between updates for better effect
    self.transition = None
    self.alpha = 1
    self.alpha_change = 3
    self.colour = colour_to_fade_into
    self.init_surf()

  def init_surf(self):
    self.surface = pygame.Surface((self.WINDOW_SIZE))
    self.surface.fill(self.colour)

  def set_transition(self):
    if not self.transition:                                                                                
      self.alpha = 1                #sets transition to 'out' by default
      self.transition = "out"
      self.init_surf()
      
  def update(self):
    self.alpha += self.alpha_change   #updates alpha value
    self.surface.set_alpha(self.alpha)    #uses alpha value to create a degree of transparency on surf
    
    if self.alpha <= 0:
      self.alpha_change *= -1      #flips alpha value if it gets too small
      self.transition = None
      self.delay_timer = 0
      del self.surface
    elif self.alpha >= 255:
      self.transition = "in"      #if surf is black it turns transition to 'in'
      self.alpha_change *= -1
      self.delay_timer = 0
          
  def run(self, display):                       #FIX TRANSITIONS
    if self.transition:
      self.delay_timer += 1 
      
      if self.delay_timer >= self.delay or self.transition == "out":  
        self.update()
      display.blit(self.surface, (0,0))
      pygame.display.update()
      
      if self.transition == "out":
        pygame.time.delay(13)
        
      if self.delay_timer >= self.delay:  
        self.delay_timer = 0    
