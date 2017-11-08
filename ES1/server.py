import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
import truco

class ClientChannel(PodSixNet.Channel.Channel):

	def Network(self, data):
		print(data)

	# é chamado sempre que algum client envia uma mensagem com a keyword 
	# 'playCard'
	def Network_play_card(self, data):
		card_dict = data["card"]
		player = data["player"]
		self._server.play_card(card_dict, player)

	def Close(self):
		self._server.close()

class TrucoServer(PodSixNet.Server.Server):

	def __init__(self, *args, **kwargs):
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.game = None
		self.currentIndex = 0

	channelClass = ClientChannel

	def Connected(self, channel, addr):
		print('new connection: ', channel)
		
		if self.game == None:
			self.game = Game(channel)
		elif self.currentIndex < 4:
			self.game.players_list.append(channel)
			if self.currentIndex == 3:
				self.game.start_game()

		self.currentIndex += 1

	def play_card(self, card_dict, player):
		self.game.send_card_to_other_players(card_dict, player)
		card = self.game.prepare_card(card_dict)
		self.game.play_card(card, player)

	def tick(self):
		if self.game != None:

			# primeira rodada
			if self.game.played_cards == 4:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
					else:
						self.game.pair2_rounds += 1
				else:
					self.game.pair1_rounds += 1
					self.game.pair2_rounds += 1

			self.game.prepare_for_next_round()

			# segunda rodada
			if self.game.played_cards == 8:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
					else:
						self.game.pair2_rounds += 1
				else:
					if self.game.pair1_rounds > self.game.pair2_rounds:
						self.game.pair1_wins()
					elif self.game.pair2_rounds > self.game.pair1_rounds:
						self.game.pair2_wins()

				if self.game.pair1_rounds == self.game.pair2_rounds:
					self.game.prepare_for_next_round()

				if self.game.pair1_rounds == 2:
					self.game.pair1_wins()
				elif self.game.pair2_rounds == 2:
					self.game.pair2_wins()
			
			# terceira rodada
			if self.game.played_cards == 12:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
					else:
						self.game.pair2_rounds += 1

				if self.game.pair1_rounds == 2:
						self.game.pair1_wins()
				elif self.game.pair2_rounds == 2:
						self.game.pair2_wins()

		self.Pump()

	def close(self):
		pass

class Game:

	START_CARDS_LEN = 3

	def __init__(self, player0):
		self.turn = 0
		self.hand_starting_player: 0

		self.pair1_rounds = 0
		self.pair2_rounds = 0

		self.turned_card = None
		self.winning_player = None
		self.winning_card = None
		self.played_cards = 0
		self.drawing = False

		self.players_list = [player0]
		self.deck = truco.Deck().shuffle()


	def dealCards(self):
		self.turned_card = self.deck.pop()
		for i, p in enumerate(self.players_list):
			cards = [ self.deck.pop() for j in range(self.START_CARDS_LEN) ]
			self.set_to_joker(cards)
			cards_dict = self.prepare_to_send(cards)
			p.Send({"action":"dealCards", "cards": cards_dict, "turned_card": self.turned_card.__dict__, "player": i})
	
	def set_to_joker(self, cards):
		for card in cards:
			if card.greater_by_one_rank(self.turned_card):
				card.isJoker = True

	def get_strongest_card_index(self):
		index = 0
		greater = self.table_cards[index]
		for i, card in enumerate(self.table_cards):
			if card > greater:
				greater = card
				index = i
		return index

	def prepare_to_send(self, cards):
		cards_dict = [ card.__dict__ for card in  cards ]
		return cards_dict

	def prepare_card(self, card_dict):
		card = truco.Card(card_dict["rank"], card_dict["suit"], card_dict["isJoker"])
		return card

	def clear_card(self, card):
		card.isJoker = False

	def play_card(self, card, player):
		if self.winning_card == None:
			self.winning_card = card
			self.winning_player = player
		else:
			if card > self.winning_card:
				self.clear_card(self.winning_card)
				self.deck.append(self.winning_card)
				self.winning_card = card
				self.winning_player = player
				self.drawing = False
			if card == self.winning_card:
				self.deck.append(self.winning_card)
				self.winning_card = card
				self.winning_player = player
				self.drawing = True
			else:
				self.deck.append(card)

		self.played_cards += 1
		self.turn = (self.turn + 1) % 4  

	def pair1_wins(self):
		self.players_list[0].Send({"action": "win"})
		self.players_list[2].Send({"action": "win"})		
		self.players_list[1].Send({"action": "lose"})
		self.players_list[3].Send({"action": "lose"})
		self.prepare_for_next_hand()

	def pair2_wins(self):
		self.players_list[1].Send({"action": "win"})
		self.players_list[3].Send({"action": "win"})		
		self.players_list[0].Send({"action": "lose"})
		self.players_list[2].Send({"action": "lose"})
		self.prepare_for_next_hand()

	def prepare_for_next_round(self):
		self.turn = self.winning_player
		self.clear_card(self.winning_card)
		self.deck.append(self.winning_card)
		self.winning_card = None
		self.winning_player = None
		self.drawing = False

	def prepare_for_next_hand(self):
		self.hand_starting_player = (self.hand_starting_player + 1) % 4
		self.turn = self.hand_starting_player
		self.clear_card(self.winning_card)
		self.deck.append(self.winning_card)
		self.deck.append(self.turned_card)
		self.winning_card = None
		self.winning_player = None
		self.drawing = False
		self.played_cards = 0

	def send_card_to_other_players(self, card_dict, player):
		for i, p in enumerate(self.players_list):
			if i != player:
				p.Send({"action": "receive_board_card", "card": card_dict})


	def start_game(self): 
		for i, p in enumerate(self.players_list):
			p.Send({"action": "startgame", "player": i})
		self.dealCards()


print('STARTING SERVER ON LOCALHOST')
truco_server = TrucoServer()
while True:
	truco_server.Pump()
	sleep(0.01)