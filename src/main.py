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

	def limitSpeed(self):
		if ( self.velocity.mod() > self.maxspeed ):
			self.velocity = self.velocity.versor() * self.maxspeed

	def actualize(self):

		self.limitSpeed()
		Particle.actualize(self)
		self.limitPosition()

class Droplet(Actor):
	def __init__(self,_image,_x):
		Actor.__init__(self,_image,Vector((0,-1)))
		self.rect.x = _x
		self.rect.y = height

	def actualize(self):
		Actor.actualize(self)
		pass

class Background:
	def __init__(self,_image):
		self.scrollspeed = -1
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

	def draw(self,surface):
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

	#some background
	background = Background(backgroundImage)

	#Lightning lightning (lightningImage)
	lightning = HeroLighning(lightningImage)

	#HUD
	hud =HUD()

	#droplets
	droplets = []
	nDroplets = 0;
	dropletsClock = 0
	dropletesInitialSpeed = -1; # increaes like the thunder speed

	pygame.event.set_grab(True)
	pygame.mouse.set_visible(False)

	while 1:
		clock.tick(max_fps)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			elif event.type == pygame.MOUSEMOTION:
				#print "Mouse Motion", event.rel
				lightning.velocity.set(event.rel)
			elif event.type == pygame.KEYDOWN:
				if event.unicode == 'q':
					quit()

		lightning.actualize()
		background.actualize()

		###################################################################
		# Droplets System
		# Add droplet system
		if (nDroplets < max_droplets):
			dropletsClock += clock.get_time()
			if ( dropletsClock  > 1000/max_droplets_per_second ):
				dropletsClock = 0
				droplets.append(Droplet(dropletImage, rng.randint(0,width)))
				nDroplets += 1
		#######################
		# Remove droplet system
		if (nDroplets > 0):
			if ( droplets[0].rect.y < 0 ):
				print "Removing"
				del droplets[0]
				nDroplets -= 1

		##################################################################
		# Collisions with droplets

		for droplet in droplets:
			if lightning.rect.colliderect(droplet.rect):
				print "Droplet collision"


		#screen.fill( (0,0,0) )
		screen.blit(background.image, (0,0),background.area_up ) 
		screen.blit(background.image, (0,background.pos),background.area_down ) 

		# draw droplets system
		for droplet in droplets:
			droplet.actualize()
			droplet.draw(screen)
		#######################

		hud.draw(screen)
		#screen.blit(lightning.image, lightning.rect)
		lightning.draw(screen)
		pygame.display.flip()
