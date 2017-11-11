import truco
from PodSixNet.Connection import ConnectionListener, connection 

class Client(ConnectionListener):

	def __init__(self):

		self.me = truco.Player()
		self.players_number_of_cards = {0: 0, 1: 0, 2: 0, 3: 0}
		self.board_cards = {}
		self.turned_card = None
		self.num = None
		self.running = False
		self.received_cards = False
		self.truco_asked = False
		self.other_team_score = 0
		self.just_placed = 300
		self.just_asked = False

		print('conectando')
		self.Connect()
		"""
		while True:
			self.read_network()
			if self.running:
				if self.received_cards:
					print("CARTAS: 	")
					print(self.me.hand)
					print("CARTA QUE VIROU: ")
					print(self.turned_card)
					self.running = False
		"""

	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]

	def Network_win(self, data):
		self.me.score += 1

	def Network_lose(self, data):
		self.other_team_score += 1

	def Network_yourturn(self, data):
		self.me.turn = data["torf"]

	def Network_truco_asked(self, data):
		self.truco_asked = True

	def Network_prepare_for_next_round(self, data):
		self.board_cards = {}

	def Network_prepare_for_next_hand(self, data):
		self.board_cards = {}
		self.turned_card = None
		for card in self.me.hand:
			connection.Send({"action": "retrieve_card", "card": card.__dict__})
		self.me.hand = []

	def Network_receive_board_card(self, data):
		card = truco.Card(data["card"]["rank"], data["card"]["suit"], data["card"]["isJoker"])
		self.players_number_of_cards[data["player"]] -= 1
		self.board_cards[data["player"]] = card

	def Network_dealCards(self, data):
		if data["player"] == self.num:
			cards = self.prepare_received_cards(data["cards"])
			self.me.setHand(cards)
			self.turned_card = truco.Card(data["turned_card"]["rank"], data["turned_card"]["suit"], data["turned_card"]["isJoker"])
			self.players_number_of_cards = {0:3, 1:3, 2:3, 3:3}

	def prepare_received_cards(self, cards):
		l = [ truco.Card(i["rank"], i["suit"], i["isJoker"]) for i in cards ] 
		return l

	def read_network(self):
		connection.Pump()
		self.Pump()

	def play_card(self, card_index):
		if self.me.turn and self.just_placed <= 0:
			self.me.turn = False
			card = self.me.playCard(card_index)
			self.board_cards[self.num] = card
			connection.Send({"action": "play_card", "card": card.__dict__, "player": self.num})

	def ask_truco(self):
		if self.me.turn and not self.just_asked:
			connection.Send({"action": "ask_truco", "player": self.num})
		self.just_asked = True

	def accept_truco(self):
		if self.truco_asked:
			connection.Send({"action": "accept_truco", "player": self.num})
		self.truco_asked = False

if __name__ == "__main__":
	c = Client()



