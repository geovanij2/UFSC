import pygame
import trucoGame
from time import sleep

class App():

	def __init__(self):
		
		pygame.init()
		pygame.font.init()
		(width, height) = (800, 600)
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("Truco")

		self.clock = pygame.time.Clock()

		self.init_graphics()

		#self.truco_game = trucoGame()

	def init_graphics(self):

		card_names = [suit + rank for suit in 'DSHC' for rank in '4567QJK123']
		self.image_dict = {}
		for card in card_names:
			self.image_dict[card] = pygame.image.load(card+'.gif')

	def draw_board(self):
		pass


	def draw_HUD(self):
		pass	


	def update(self):

		self.screen.fill((0,255,0))
		pygame.display.flip()


a = App()
while True:
	a.update()
	sleep(0.1)