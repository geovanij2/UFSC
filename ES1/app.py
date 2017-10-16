import pygame
import Client
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

		self.truco_game = Client.Client()

	def init_graphics(self):

		card_names = [suit + rank for suit in 'DSHC' for rank in '4567QJK123']
		self.image_dict = {}
		for card in card_names:
			self.image_dict[card] = pygame.image.load(card+'.gif').convert()

	def draw_board(self):
		pass


	def draw_HUD(self):
		pass	


	def update(self):

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			print(pygame.QUIT)

		self.screen.fill((0,63,0))
		pygame.display.flip()


a = App()
while True:
	a.update()