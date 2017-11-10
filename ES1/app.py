import pygame
import Client
from time import sleep

class App():

	def __init__(self):
		
		pygame.init()
		pygame.font.init()
		(width, height) = (800, 600)
		self.white = (255, 255, 255)
		self.bg_green = (0,100,0)
		self.light_blue = (29,231,241)
		self.screen = pygame.display.set_mode((width, height))
		pygame.display.set_caption("Truco")

		self.clock = pygame.time.Clock()

		self.init_graphics()

		(self.card_width, self.card_height) = self.faced_down_card.get_size()
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
		# my hand
		for i, card in enumerate(self.truco_game.me.hand):
			self.card_button(i*80 + 285, 475, self.card_width, self.card_height, self.light_blue, self.image_dict[card.suit + card.rank], i)

		if self.truco_game.running:
			# oposite players hand
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+2)%4]):
				self.screen.blit(self.faced_down_card, (i*80 + 285, 29))
			# player to the right
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+1)%4]):
				self.screen.blit(self.hor_faced_down_card, (675, i*80 +185))
			# player to the left
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+3)%4]):
				self.screen.blit(self.hor_faced_down_card, (29, i*80 + 185))

		if turned_card is not None:
			self.screen.blit(self.image_dict[turned_card.suit + turned_card.rank], (405, 250))
		self.screen.blit(self.faced_down_card, (325, 250))


	def draw_HUD(self):
		if self.truco_game.me.turn:
			# create font
			my_font_64 = pygame.font.SysFont(None, 64)
			# create text surface
			label = my_font_64.render("Your turn!", 1, self.white)
			# draw surface
			self.screen.blit(label, (40,500))
		if self.truco_game.running:
			my_font_32 = pygame.font.SysFont(None, 32)

			my_team_score = my_font_32.render("Your team: " + str(self.truco_game.me.score), 1, self.white)
			other_team_score = my_font_32.render("Other team: " + str(self.truco_game.other_team_score), 1, self.white)

			self.screen.blit(my_team_score, (50, 40))
			self.screen.blit(other_team_score, (50, 70))

	def card_button(self, x, y, width, height, color, card_image, index):
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		if x + width > mouse[0] > x and y + height > mouse[1] > y:
			pygame.draw.rect(self.screen, color, (x-3, y-3, width+6, height+6))
			if click[0] == 1:
				self.truco_game.play_card(index)
		self.screen.blit(card_image, (x, y))

	def update(self):

		self.truco_game.just_placed -= 1
		# pumps client and server so it looks for new events/messages
		self.truco_game.read_network()
		# 60 FPS
		self.clock.tick(60)
		# clear the screen
		self.screen.fill((0,100,0))
		# draw cards
		self.draw_board()
		# draw HUD
		self.draw_HUD()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()

		mouse = pygame.mouse.get_pos()
		
		# update the screen
		pygame.display.flip()


a = App()
while True:
	a.update()