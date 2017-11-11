import pygame
import Client
from time import sleep

class App():

	def __init__(self):
		
		pygame.init()
		pygame.font.init()

		(width, height) = (800, 600)

		self.black = (0,0,0)
		self.white = (255, 255, 255)
		self.bg_green = (0,100,0)
		self.blue = (0,255,0)
		self.inactive_blue = (0,180,0)
		self.light_blue = (29,231,241)
		self.light_grey = (192,192,192)
		self.dark_grey = (140,140,140)


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

		if self.truco_game.running:

			player = self.truco_game.num
			turned_card = self.truco_game.turned_card

			team_mate_card = self.truco_game.get_board_card((player+2)%4)
			right_player_card = self.truco_game.get_board_card((player+1)%4)
			left_player_card = self.truco_game.get_board_card((player+3)%4)
			my_card = self.truco_game.get_board_card(player)

			# my hand
			for i, card in enumerate(self.truco_game.me.hand):
				self.card_button(i*80 + 285, 494, self.card_width, self.card_height, self.light_blue, self.image_dict[card.suit + card.rank], i)

			# oposite players hand
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+2)%4]):
				self.screen.blit(self.faced_down_card, (i*80 + 285, 10))
			# player to the right
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+1)%4]):
				self.screen.blit(self.hor_faced_down_card, (694, i*80 +185))
			# player to the left
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+3)%4]):
				self.screen.blit(self.hor_faced_down_card, (10, i*80 + 185))
			# draws thrown cards
			if team_mate_card is not None:
				self.screen.blit(self.image_dict[team_mate_card.suit + team_mate_card.rank], (365, 120))
			if right_player_card is not None:
				self.screen.blit(self.image_dict[right_player_card.suit + right_player_card.rank], (550, 250))
			if left_player_card is not None:
				self.screen.blit(self.image_dict[left_player_card.suit + left_player_card.rank], (180, 250))
			if my_card is not None:
				self.screen.blit(self.image_dict[my_card.suit + my_card.rank], (365, 384))

			if turned_card is not None:
				self.screen.blit(self.image_dict[turned_card.suit + turned_card.rank], (405, 250))
			self.screen.blit(self.faced_down_card, (325, 250))

			self.button("Trucar", 625, 515, 150, 60, self.dark_grey, self.light_grey, self.truco_game.ask_truco)


	def draw_HUD(self):

		if self.truco_game.me.turn:
			# create font
			my_font_64 = pygame.font.SysFont(None, 64)
			# create text surface
			label = my_font_64.render("Sua vez!", 1, self.white)
			# draw surface
			self.screen.blit(label, (40,500))

		if self.truco_game.running:
			my_font_32 = pygame.font.SysFont(None, 32)

			my_team_score = my_font_32.render("Nós: " + str(self.truco_game.me.score), 1, self.white)
			other_team_score = my_font_32.render("Eles: " + str(self.truco_game.other_team_score), 1, self.white)

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

	def button(self, msg, x, y, w, h, ic, ac, action=None):
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		if x+w > mouse[0] > x and y+h > mouse[1] > y:
			pygame.draw.rect(self.screen, ac, (x, y, w, h))
			if click[0] == 1 and action != None:
				action()
		else:
			pygame.draw.rect(self.screen, ic, (x, y, w, h))

		my_font = pygame.font.SysFont(None, 32)
		text_surf, text_rect = self.text_objects(msg, my_font)
		text_rect.center = ((x+(w/2)), (y+(h/2)))
		self.screen.blit(text_surf, text_rect)

	def text_objects(self, text, font):
		textSurface = font.render(text, True, self.black)
		return textSurface, textSurface.get_rect()

	def draw_truco_asked_screen(self):
		if self.truco_game.truco_asked:
			player = self.truco_game.num
			turned_card = self.truco_game.turned_card

			team_mate_card = self.truco_game.get_board_card((player+2)%4)
			right_player_card = self.truco_game.get_board_card((player+1)%4)
			left_player_card = self.truco_game.get_board_card((player+3)%4)
			my_card = self.truco_game.get_board_card(player)

			self.screen.fill((0,100,0))
			# my hand
			for i, card in enumerate(self.truco_game.me.hand):
				self.card_button(i*80 + 285, 494, self.card_width, self.card_height, self.light_blue, self.image_dict[card.suit + card.rank], i)
			# oposite players hand
			for i, card in enumerate(self.truco_game.team_mate_cards):
				self.screen.blit(self.image_dict[card.suit + card.rank], (i*80 + 285, 10))
			# player to the right
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+1)%4]):
				self.screen.blit(self.hor_faced_down_card, (694, i*80 +185))
			# player to the left
			for i in range(self.truco_game.players_number_of_cards[(self.truco_game.num+3)%4]):
				self.screen.blit(self.hor_faced_down_card, (10, i*80 + 185))
			# draws thrown cards
			if team_mate_card is not None:
				self.screen.blit(self.image_dict[team_mate_card.suit + team_mate_card.rank], (365, 120))
			if right_player_card is not None:
				self.screen.blit(self.image_dict[right_player_card.suit + right_player_card.rank], (550, 250))
			if left_player_card is not None:
				self.screen.blit(self.image_dict[left_player_card.suit + left_player_card.rank], (180, 250))
			if my_card is not None:
				self.screen.blit(self.image_dict[my_card.suit + my_card.rank], (365, 384))

			if turned_card is not None:
				self.screen.blit(self.image_dict[turned_card.suit + turned_card.rank], (405, 250))
			self.screen.blit(self.faced_down_card, (325, 250))

			self.button("Cai!", 10, 530, 100, 60, self.inactive_blue, self.blue, self.truco_game.accept_truco)
			self.button("Correr", 130, 530, 100, 60, self.dark_grey, self.light_grey, self.truco_game.refuse_truco)

	def print_test(self):
		print("teste")	

	def update(self):

		if self.truco_game.me.score >= 12 or self.truco_game.other_team_score >= 12:
			return 1

		self.truco_game.just_played -= 1
		# pumps client and server so it looks for new events/messages
		self.truco_game.read_network()
		# 60 FPS
		self.clock.tick(60)
		# clear the screen
		self.screen.fill((0,100,0))
		# draw cards
		self.draw_board()
		# draw truco screen
		self.draw_truco_asked_screen()
		# draw HUD
		self.draw_HUD()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
		
		# update the screen
		pygame.display.flip()

	def finished(self):
		if self.truco_game.me.won:
			self.screen.fill((0,100,0))
			msg = "Você venceu!"
		else:
			self.screen.fill((100,0,0))
			msg = "Você perdeu!"

		my_font = pygame.font.SysFont(None, 64)
		text_surf, text_rect = self.text_objects(msg, my_font)
		text_rect.center = (400,300)
		self.screen.blit(text_surf, text_rect)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					exit()
			pygame.display.flip()



a = App()
while True:
	if a.update() == 1:
		break
a.finished()