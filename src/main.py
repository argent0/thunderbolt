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

#penalties & boni
energy_bonus_amount = 0.10
leaf_speed_penalty = -2

#probabilities
energyBonusProbability = 5
leaf_probability = 47

images_path = "../images/"
sfx_path = "../sounds/"

#Load the images

def quit():
	print "OK, bye."
	sys.exit()

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
		if self.energy > 1.:
			self.energy = 1.

		print self.energy

class Droplet(Actor):
	def __init__(self,_image,_x, _speed,_name):
		Actor.__init__(self,_image,Vector((0,_speed)))
		self.rect.x = _x
		self.rect.y = height
		self.name = _name

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

	def draw(self,surface,_points,_speed,_energy):
		points = self.font.render("Points: {0:4.0f} (x{1:2.0f})".format(_points,_speed),1,(100,0,0))
		pos = points.get_rect(bottomleft=(0,height))
		surface.blit(points, pos)
		surface.fill((100,0,0), pygame.Rect(0,0,width*_energy,20) )
		surface.blit(self.text, self.textpos)

class FlashyFont:
	def __init__(self,_clock,_colorA,_colorB,_surface,_text,_y_pos,_flash_delay=100,_flick=2):
		self.clock = _clock
		self.A = _colorA
		self.B = _colorB
		self.surface = _surface
		self.timer = 0
		self.text = _text
		self.font = pygame.font.Font(None, 36)
		self.cColor = _colorA #current color
		self.yPos = _y_pos

		self.flashDelay = _flash_delay
		self.flick = _flick
		self.flickSign = 1

	def draw(self):
		rText = self.font.render(self.text, 1, self.cColor)
		tPos = rText.get_rect(centerx=width/2)
		tPos.top = self.yPos+self.flick*self.flickSign
		self.surface.blit(rText, tPos)

	def actualize(self):
		self.timer += self.clock.get_time()
		if ( self.timer > self.flashDelay ):
			if self.cColor == self.A:
				self.cColor = self.B
			else:
				self.cColor = self.A

			self.flick *= -1

			self.timer = 0

			return True

		else:
			return False

class DropletSyste:
	""" This is the class tha makes rain upwards """
	def __init__(self, _dlist, _clock):
		self.dlist = _dlist
		self.nDroplets = 0
		self.dropletsClock = 0
		self.clock = _clock

	def add(self,gameSpeed):
		###################################################################
		# Droplets System
		# Add droplet system
		if (self.nDroplets < max_droplets):
			self.dropletsClock += self.clock.get_time()
			if ( self.dropletsClock  > 1000/max_droplets_per_second/gameSpeed ):
				self.dropletsClock = 0
				tempRN = rng.randint(0,100)
				if ( tempRN < energyBonusProbability ):
					tempDropImage = smallLightningImage
					tempName = "bonus"
				elif ( tempRN < leaf_probability ):
					tempDropImage = leafImage
					tempName = "leaf"
				else:
					tempDropImage = dropletImage
					tempName = "water"
				self.dlist.append(Droplet(tempDropImage, rng.randint(0,width),
					-gameSpeed,tempName))
				self.nDroplets += 1

	def remove(self):
		#######################
		# Remove droplet system
		if (self.nDroplets > 0):
			if ( self.dlist[0].rect.y < 0 ):
				del self.dlist[0]
				self.nDroplets -= 1

	def draw(self,surface,gameSpeed):
		# draw droplets system
		for droplet in self.dlist:
			droplet.velocity.set((0,-gameSpeed)) #droplet speed actualization
			droplet.actualize()
			droplet.draw(surface)
		#######################



class Slide:
	def __init__(self, _filename,_surface):
		self.image = pygame.image.load(images_path+_filename).convert()
		self.surface = _surface

	def run(self):
		clock = pygame.time.Clock()
		sfx = pygame.mixer.music.load(sfx_path+'LRStorm 01 by Teza.ogg')
		#sfx = pygame.mixer.music.load(sfx_path+'water2.wav')

		ff = FlashyFont(clock, (200,200,200),(200,200,0),self.surface,"Press spacebar to start",height*3/4)
		ff2 = FlashyFont(clock, (200,200,200),(200,200,0),self.surface,"<ESC> To exit",height*3/4+50)
		screen.blit(self.image, (0,0) ) 
		ff.draw()
		ff2.draw()
		pygame.display.flip()

		droplets = []
		ds = DropletSyste(droplets,clock)
		speed = 10

		pygame.mixer.music.play(-1)

		while 1:
			clock.tick(max_fps)
			ff.actualize()
			ff2.actualize()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.unicode == ' ':
						return
					if event.key == 27:
						quit()

			ds.add(speed)
			ds.remove()

			screen.blit(self.image, (0,0) ) 
			ds.draw(self.surface,speed)


			ff.draw()
			ff2.draw()
			pygame.display.flip()

if __name__ == "__main__":
		
	pygame.font.init()

	screen = pygame.display.set_mode(size,pygame.DOUBLEBUF )
	clock = pygame.time.Clock()

	#image loading
	lightningImage = pygame.image.load(images_path+'lightning.png')#.convert()
	backgroundImage = pygame.image.load(images_path+'sky.png').convert()
	dropletImage = pygame.image.load(images_path+'drop.png')#.convert()
	leafImage = pygame.image.load(images_path+'leaf.png')
	smallLightningImage = pygame.transform.scale(lightningImage,(tile_side/2,tile_side/2))

	#sound loading
	waterSound = pygame.mixer.Sound(sfx_path+'drip.ogg')
	thunderSound = pygame.mixer.Sound(sfx_path+'thunder.ogg')

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
	points = 0;

	#droplets
	droplets = []
	ds = DropletSyste(droplets,clock)

	pygame.event.set_grab(True)
	pygame.mouse.set_visible(False)

	slide = Slide('front.png',screen)
	slide.run()
		
	while ( (lightning.energy > 0 ) and ( gameSpeed >= 0 ) ):
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

		ds.add(gameSpeed)
		ds.remove()

		##################################################################
		# Collisions with droplets

		for droplet in droplets:
			if lightning.rect.colliderect(droplet.rect):
				droplet.rect.y = -tile_side;
				if droplet.name == "water":
					tempBonus = 1
					waterSound.play()
				elif droplet.name == "leaf":
					tempBonus = leaf_speed_penalty
				elif droplet.name == "bonus":
					tempBonus = 0;
					thunderSound.play()
					lightning.energy += energy_bonus_amount

				nCollisions += tempBonus
				gameSpeed = game_initial_speed+(game_max_speed-game_initial_speed)*(1.-math.exp(-nCollisions*0.005))


		#screen.fill( (0,0,0) )
		screen.blit(background.image, (0,0),background.area_up ) 
		screen.blit(background.image, (0,background.pos),background.area_down ) 
		background.scrollspeed = -gameSpeed*0.5

		ds.draw(screen,gameSpeed)

		##################################################################
		# HUD update 
		points += gameSpeed*clock.get_time()*0.01
		hud.draw(screen,points,gameSpeed,lightning.energy)
		#screen.blit(lightning.image, lightning.rect)
		lightning.draw(screen)
		pygame.display.flip()
