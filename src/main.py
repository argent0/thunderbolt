#!/usr/bin/python2
import pygame,sys
import math, random
pygame.init()
rng = random.Random()

size = width, height = 640, 480
tile_side = 32
max_droplets = 100
max_fps = 40
max_droplets_per_second = 2
air_conductivity_loss_factor = 0.95
air_conductivity_loss_linear_term = 0.01
energy_leaks_fps = 1
game_initial_speed = 5
game_max_speed = 50

images_path = "../images/"

#Load the images

class Vector:
	def __init__(self,_tup):
		self.x = float(_tup[0])
		self.y = float(_tup[1])
		pass

	def mod2(self):
		return self.x**2+self.y**2

	def mod(self):
		return math.sqrt(self.mod2())

	def versor(self):
		mod = self.mod()
		return Vector((self.x/mod, self.y/mod))

	def __mul__(self,other):
		return Vector((self.x*other,self.y*other))

	def set(self,_tup):
		self.x = float(_tup[0])
		self.y = float(_tup[1])

if __name__ == "__main__":
	vec = Vector((1,2))
	print vec.x
	pass

class Particle:
	def __init__(self,_rect,_velocity):
		self.velocity=_velocity
		self.rect = _rect

	def actualize(self):
		self.rect.x += self.velocity.x
		self.rect.y += self.velocity.y

class Actor(Particle):
	def __init__(self, _image,_velocity):
		Particle.__init__(self,_image.get_rect(),_velocity)
		self.image = _image

	def moveLeft(self,_delta):
		self.rect.x += _delta

	def limitPosition(self):
		if (self.rect.x < 0 ):
			self.rect.x = 0
		if (self.rect.x > width-tile_side ):
			self.rect.x = width-tile_side
		if (self.rect.y < 0 ):
			self.rect.y = 0
		if (self.rect.y > height-tile_side ):
			self.rect.y = height-tile_side

	def draw(self,surface):
		surface.blit(self.image,self.rect)

class HeroLighning(Actor):
	def __init__(self,_image):
		self.maxspeed = 400
		Actor.__init__(self,_image, Vector((0,0)))
		self.energy = 1 #this is %

	def limitSpeed(self):
		if ( self.velocity.mod() > self.maxspeed ):
			self.velocity = self.velocity.versor() * self.maxspeed

	def actualize(self):

		self.limitSpeed()
		Particle.actualize(self)
		self.limitPosition()

		print self.energy

class Droplet(Actor):
	def __init__(self,_image,_x, _speed):
		Actor.__init__(self,_image,Vector((0,_speed)))
		self.rect.x = _x
		self.rect.y = height

	def actualize(self):
		Actor.actualize(self)
		pass

class Background:
	def __init__(self,_image, _scrollspeed):
		self.scrollspeed = _scrollspeed
		self.image = _image
		self.pos = 100;
		self.area_up = pygame.Rect(0,0,width,height)
		self.area_down = pygame.Rect(0,0,width,height)
		self.imageRect = _image.get_rect()
	
	def actualize(self):
		self.pos = (self.scrollspeed + self.pos) % (height)

		self.area_up.y = self.imageRect.height - self.pos
		self.area_up.height = self.pos
		self.area_down.y = 0
		self.area_down.height = self.imageRect.height-self.pos

class HUD:
	def __init__(self):
		self.font = pygame.font.Font(None, 36)
		self.text = self.font.render("Press 'q' to leave", 1, (10, 10, 10))
		self.textpos = self.text.get_rect(centerx=width/2)

	def draw(self,surface,_points,_energy):
		points = self.font.render("Points:"+ str(_points),1,(100,100,100))
		pos = points.get_rect(bottomleft=(0,height))
		surface.blit(points, pos)
		surface.fill((100,0,0), pygame.Rect(0,0,width*_energy,20) )
		surface.blit(self.text, self.textpos)

def quit():
	print "OK, bye."
	sys.exit()

if __name__ == "__main__":
		
	pygame.font.init()

	screen = pygame.display.set_mode(size,pygame.DOUBLEBUF )
	clock = pygame.time.Clock()

	#image loading
	lightningImage = pygame.image.load(images_path+'lightning.png')#.convert()
	backgroundImage = pygame.image.load(images_path+'sky.png').convert()
	dropletImage = pygame.image.load(images_path+'drop.png')#.convert()

	#game data
	gameSpeed = game_initial_speed;
	nCollisions = 0; #how many collisions have ocurred

	#some background
	background = Background(backgroundImage,-gameSpeed)

	#Lightning lightning (lightningImage)
	lightning = HeroLighning(lightningImage)

	#HUD
	hud =HUD()
	leaksClock = 0

	#droplets
	droplets = []
	nDroplets = 0;
	dropletsClock = 0

	pygame.event.set_grab(True)
	pygame.mouse.set_visible(False)

	while (lightning.energy > 0 ):
		clock.tick(max_fps)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			elif event.type == pygame.MOUSEMOTION:
				lightning.velocity.set(event.rel)
			elif event.type == pygame.KEYDOWN:
				if event.unicode == 'q':
					quit()

		leaksClock += clock.get_time()
		if (leaksClock > 1000/energy_leaks_fps):
			leaksClock = 0
			lightning.energy *= air_conductivity_loss_factor
			lightning.energy -= air_conductivity_loss_linear_term

		lightning.actualize()
		background.actualize()

		###################################################################
		# Droplets System
		# Add droplet system
		if (nDroplets < max_droplets):
			dropletsClock += clock.get_time()
			if ( dropletsClock  > 1000/max_droplets_per_second/gameSpeed ):
				dropletsClock = 0
				droplets.append(Droplet(dropletImage, rng.randint(0,width),
					-gameSpeed))
				nDroplets += 1
		#######################
		# Remove droplet system
		if (nDroplets > 0):
			if ( droplets[0].rect.y < 0 ):
				del droplets[0]
				nDroplets -= 1

		##################################################################
		# Collisions with droplets

		for droplet in droplets:
			if lightning.rect.colliderect(droplet.rect):
				droplet.rect.y = -tile_side;
				nCollisions += 1
				gameSpeed = game_initial_speed+(game_max_speed-game_initial_speed)*(1.-math.exp(-nCollisions*0.005))


		#screen.fill( (0,0,0) )
		screen.blit(background.image, (0,0),background.area_up ) 
		screen.blit(background.image, (0,background.pos),background.area_down ) 
		background.scrollspeed = -gameSpeed*0.5

		# draw droplets system
		for droplet in droplets:
			droplet.velocity.set((0,-gameSpeed)) #droplet speed actualization
			droplet.actualize()
			droplet.draw(screen)
		#######################

		##################################################################
		# HUD update 
		hud.draw(screen,nCollisions,lightning.energy)
		#screen.blit(lightning.image, lightning.rect)
		lightning.draw(screen)
		pygame.display.flip()
