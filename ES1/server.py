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
		pass

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

	def play_card(self):
		pass

	def tick(self):
		if len(self.game.table_cards) == 4:
			index = self.game.get_strongest_card_index()
			if index == 0 or index == 2:
				self.game.pair1_rounds += 1
			else:
				self.game.pair2_rounds += 1

			self.game.deck.extend(self.game.table_cards)
			self.game.deck = []
			self.game.turn = index
			
			if self.game.pair1_rounds == 2:
				self.game.players_list[0].Send({"action": "win"})
				self.game.players_list[2].Send({"action": "win"})
				self.game.players_list[1].Send({"action": "lose"})
				self.game.players_list[3].Send({"action": "lose"})
			elif self.game.pair2_rounds == 2:
				self.game.players_list[1].Send({"action": "win"})
				self.game.players_list[3].Send({"action": "win"})
				self.game.players_list[0].Send({"action": "lose"})
				self.game.players_list[2].Send({"action": "lose"})
		else:
			self.Pump()

	def close(self):
		pass

class Game:

	START_CARDS_LEN = 3

	def __init__(self, player0):
		self.turn = 0
		self.pair1_rounds = 0
		self.pair2_rounds = 0
		self.turned_card = None
		self.player_sequence = []
		self.table_cards = []
		self.players_list = [player0]
		self.deck = Deck().shuffle()


	def dealCards(self):
		for i in self.players_list:
			cards = [ self.deck.pop() for j in range(self.START_CARDS_LEN) ]
			i.Send({"action":"deal_cards", "cards": cards})

	def get_strongest_card_index(self):
		index = 0
		greater = self.table_cards[index]
		for i, card in enumerate(self.table_cards):
			if card > greater:
				greater = card
				index = i
		return index

	def play_card(self):
		pass

	def start_game(self):
		for i, p in enumerate(self.players_list):
			p.Send({"action": "startgame", "player": i})


