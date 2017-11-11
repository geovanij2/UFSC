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

	def Network_retrieve_card(self, data):
		card_dict = data["card"]
		self._server.retrieve_card(card_dict)

	def Network_ask_truco(self, data):
		player = data["player"]
		self._server.ask_truco(player)

	def Network_accept_truco(self, data):
		player = data["player"]
		self._server.accept_truco(player)

	def Network_refuse_truco(self, data):
		player = data["player"]
		self._server.refuse_truco(player)

	def Network_show_team_mate(self, data):
		cards_dict = data["cards"]
		player = data["player"]
		self._server.show_team_mate(cards_dict, player)

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

	def ask_truco(self, player):
		self.game.ask_truco(player)

	def accept_truco(self, player):
		self.game.truco_response_dict[player] = True

	def refuse_truco(self, player):
		self.game.truco_response_dict[player] = False

	def show_team_mate(self,cards_dict, player):
		self.game.show_team_mate(cards_dict, player)

	def retrieve_card(self, card_dict):
		card = self.game.prepare_card(card_dict)
		self.game.clear_card(card)
		self.game.deck.append(card)
		if len(self.game.deck) == 40:
			self.game.dealCards()

	def play_card(self, card_dict, player):
		self.game.send_card_to_other_players(card_dict, player)
		card = self.game.prepare_card(card_dict)
		self.game.play_card(card, player)

	def tick(self):
		if self.game != None:

			self.game.check_for_truco()
			# primeira rodada
			if self.game.played_cards == 4 and not self.game.done_round1:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
						self.game.won_first_round = 0
					else:
						self.game.pair2_rounds += 1
						self.game.won_first_round = 1
				else:
					self.game.pair1_rounds += 1
					self.game.pair2_rounds += 1

				self.game.prepare_for_next_round()
				self.game.done_round1 = True
				print("TIME 1: ", self.game.pair1_rounds)
				print("TIME 2: ", self.game.pair2_rounds)
			# segunda rodada
			if self.game.played_cards == 8 and not self.game.done_round2:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
					elif self.game.winning_player == 1 or self.game.winning_player == 3:
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

				self.game.done_round2 = True
				print("TIME 1: ", self.game.pair1_rounds)
				print("TIME 2: ", self.game.pair2_rounds)
			# terceira rodada
			if self.game.played_cards == 12:
				if not self.game.drawing:
					if self.game.winning_player == 0 or self.game.winning_player == 2:
						self.game.pair1_rounds += 1
					else:
						self.game.pair2_rounds += 1
				else:
					if self.game.won_first_round == 0:
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
		self.hand_starting_player = 0
		# 0 for pair1/ 1 for pair2
		self.won_first_round = 0

		self.pair1_rounds = 0
		self.pair2_rounds = 0

		self.done_round1 = False
		self.done_round2 = False

		self.turned_card = None
		self.winning_player = None
		self.winning_card = None
		self.played_cards = 0
		self.drawing = False

		self.score_multiplier = 0
		self.truco_asked = False
		self.truco_asking_player = None
		self.truco_response_dict = {}

		self.players_list = [player0]
		self.deck = truco.Deck()


	def dealCards(self):
		print("NUMERO DO CARTAS NO BARALHO: ", len(self.deck))
		self.deck.shuffle()
		self.turned_card = self.deck.pop()
		for i, p in enumerate(self.players_list):
			cards = [ self.deck.pop() for j in range(self.START_CARDS_LEN) ]
			self.set_to_joker(cards)
			cards_dict = self.prepare_to_send(cards)
			p.Send({"action":"dealCards", "cards": cards_dict, "turned_card": self.turned_card.__dict__, "player": i})
		print("NUMERO DO CARTAS NO BARALHO: ", len(self.deck))

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
		if self.winning_card is None:
			self.winning_card = card
			self.winning_player = player
		else:
			if card > self.winning_card:
				self.clear_card(self.winning_card)
				self.deck.append(self.winning_card)
				self.winning_card = card
				self.winning_player = player
				self.drawing = False
			elif card == self.winning_card:
				if (player + 2) % 4 != self.winning_player:
					self.drawing = True 
				self.deck.append(self.winning_card)
				self.winning_card = card
				self.winning_player = player
			elif self.winning_card > card:
				self.deck.append(card)

		print("JOGADOR VENCENDO: ", self.winning_player)
		self.played_cards += 1
		self.turn = (self.turn + 1) % 4
		self.send_yourturn_message()

	def check_for_truco(self):
		if self.truco_asked and len(self.truco_response_dict) == 2:
			if self.truco_asking_player == 0 or self.truco_asking_player == 2:
				if not self.truco_response_dict[1] and not self.truco_response_dict[3]:
					print("cheguei aqui")
					self.pair1_wins()
				else:
					self.score_multiplier += 1

			elif self.truco_asking_player == 1 or self.truco_asking_player == 3:
				if not self.truco_response_dict[0] and not self.truco_response_dict[2]:
					print("cheguei aqui")
					self.pair2_wins()
				else:
					self.score_multiplier += 1

			self.truco_asking_player = None
			self.truco_asked = False
			self.truco_response_dict = {}

	def ask_truco(self, player):
		self.truco_asked = True
		self.truco_asking_player = player
		self.send_your_team_asked_truco_msg(player)
		self.players_list[(player+1)%4].Send({"action": "truco_asked"})
		self.players_list[(player+3)%4].Send({"action": "truco_asked"})

	def pair1_wins(self):
		if self.score_multiplier == 0:
			score = 1
		else:
			score = self.score_multiplier * 3

		self.players_list[0].Send({"action": "win", "score": score})
		self.players_list[2].Send({"action": "win", "score": score})		
		self.players_list[1].Send({"action": "lose", "score": score})
		self.players_list[3].Send({"action": "lose", "score": score})

		self.prepare_for_next_hand()

	def pair2_wins(self):
		if self.score_multiplier == 0:
			score = 1
		else:
			score = self.score_multiplier * 3

		self.players_list[1].Send({"action": "win", "score": score})
		self.players_list[3].Send({"action": "win", "score": score})		
		self.players_list[0].Send({"action": "lose", "score": score})
		self.players_list[2].Send({"action": "lose", "score": score})

		self.prepare_for_next_hand()

	def prepare_for_next_round(self):
		self.turn = self.winning_player
		self.clear_card(self.winning_card)
		self.deck.append(self.winning_card)
		self.winning_card = None
		self.winning_player = None
		self.drawing = False
		self.send_prepare_for_next_round_msg()
		self.send_yourturn_message()

	def prepare_for_next_hand(self):
		self.hand_starting_player = (self.hand_starting_player + 1) % 4
		self.turn = self.hand_starting_player
		if self.winning_card is not None:
			self.clear_card(self.winning_card)
			self.deck.append(self.winning_card)
		self.deck.append(self.turned_card)
		self.winning_card = None
		self.winning_player = None
		self.drawing = False
		self.played_cards = 0
		self.done_round1 = False
		self.done_round2 = False
		self.pair1_rounds = 0
		self.pair2_rounds = 0
		self.score_multiplier = 0
		self.send_prepare_for_next_hand_msg()
		if len(self.deck) == 40:
			self.dealCards()
		self.send_yourturn_message()

	def send_prepare_for_next_round_msg(self):
		for p in self.players_list:
			p.Send({"action": "prepare_for_next_round"})

	def send_prepare_for_next_hand_msg(self):
		for p in self.players_list:
			p.Send({"action": "prepare_for_next_hand"})

	def send_card_to_other_players(self, card_dict, player):
		for i, p in enumerate(self.players_list):
			if i != player:
				p.Send({"action": "receive_board_card", "card": card_dict, "player": player})

	def send_yourturn_message(self):
		for i, p in enumerate(self.players_list):
			if i == self.turn:
				p.Send({"action": "yourturn", "torf": True})
			else:
				p.Send({"action": "yourturn", "torf": False})

	def show_team_mate(self, cards_dict, player):
		self.players_list[(player+2)%4].Send({"action": "receive_team_mate_cards", "cards": cards_dict})

	def send_your_team_asked_truco_msg(self, player):
		partner = (player+2)%4
		self.players_list[partner].Send({"action": "your_team_mate_asked_truco"})

	def start_game(self): 
		for i, p in enumerate(self.players_list):
			p.Send({"action": "startgame", "player": i})
		self.dealCards()
		self.send_yourturn_message()


print('STARTING SERVER ON LOCALHOST')
address = input('Host:Port (localhost:8000): ')
if not address:
	host, port = 'localhost', 8000
else:
	host, port = address.split(':')
truco_server = TrucoServer(localaddr=(host, int(port)))

while True:
	truco_server.tick()
	sleep(0.01)