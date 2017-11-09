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

		self.faced_down_card = pygame.image.load("Deck3.gif").convert()
		self.hor_faced_down_card = pygame.transform.rotate(self.faced_down_card, -90)

		card_names = [suit + rank for suit in 'DSHC' for rank in '4567QJK123']
		self.image_dict = {}
		for card in card_names:
			self.image_dict[card] = pygame.image.load(card+'.gif').convert()

	def draw_board(self):
		turned_card = self.truco_game.turned_card
		for i, card in enumerate(self.truco_game.me.hand):
			self.screen.blit(self.image_dict[card.suit + card.rank], (i*80 + 285, 475))
		if turned_card is not None:
			self.screen.blit(self.image_dict[turned_card.suit + turned_card.rank], (405, 250))
		self.screen.blit(self.faced_down_card, (325, 250))


	def draw_HUD(self):
		pass	


	def update(self):

		# pumps client and server so it looks for new events/messages
		self.truco_game.read_network()
		# 60 FPS
		self.clock.tick(60)
		# clear the screen
		self.screen.fill((0,100,0))
		# draw cards
		self.draw_board()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			print(pygame.QUIT)
		# update the screen
		pygame.display.flip()


a = App()
while True:
	a.update()