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
		self.team_mate_asked_truco = False
		self.other_team_score = 0
		self.just_played = 300
		self.just_asked = False
		self.number_of_trucos_asked = 0
		self.team_mate_cards = []

		print('conectando')
		self.start_connection_to_server()

	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]

	def Network_win(self, data):
		self.me.score += data["score"]
		if self.me.score >= 12:
			self.me.won = True

	def Network_lose(self, data):
		self.other_team_score += data["score"]

	def Network_yourturn(self, data):
		self.me.turn = data["torf"]

	def Network_truco_asked(self, data):
		self.truco_asked = True
		self.just_asked = False
		self.team_mate_asked_truco = False
		cards = self.prepare_to_send_cards(self.me.hand)
		connection.Send({"action": "show_team_mate", "cards": cards, "player": self.num})

	def Network_receive_team_mate_cards(self, data):
		cards = self.prepare_received_cards(data["cards"])
		self.team_mate_cards = cards

	def Network_your_team_mate_asked_truco(self, data):
		self.team_mate_asked_truco = True

	def Network_prepare_for_next_round(self, data):
		self.board_cards = {}
		self.team_mate_cards = []

	def Network_prepare_for_next_hand(self, data):
		self.board_cards = {}
		self.team_mate_cards = []
		self.just_asked = False
		self.turned_card = None
		self.team_mate_asked_truco = False
		self.number_of_trucos_asked = 0
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

	def prepare_to_send_cards(self, cards):
		cards_dict = [ card.__dict__ for card in cards ]
		return cards_dict

	def read_network(self):
		connection.Pump()
		self.Pump()

	def get_board_card(self, key):
		try:
			return self.board_cards[key]
		except:
			return None

	def play_card(self, card_index):
		if self.me.turn and self.just_played <= 0:
			self.just_played = 300
			self.me.turn = False
			card = self.me.playCard(card_index)
			self.board_cards[self.num] = card
			connection.Send({"action": "play_card", "card": card.__dict__, "player": self.num})

	def ask_truco(self):
		if self.me.turn and not self.just_asked and self.number_of_trucos_asked < 2 and not self.team_mate_asked_truco:
			connection.Send({"action": "ask_truco", "player": self.num})
			self.number_of_trucos_asked += 1
		self.just_asked = True

	def accept_truco(self):
		if self.truco_asked:
			connection.Send({"action": "accept_truco", "player": self.num})
		self.truco_asked = False

	def refuse_truco(self):
		if self.truco_asked:
			connection.Send({"action": "refuse_truco", "player": self.num})
		self.truco_asked = False

	def start_connection_to_server(self):
		address = input("Address fo server: ")
		try:
			if not address:
				host, port = 'localhost', 8000
			else:
				host, port = address.split(':')
			self.Connect((host, int(port)))
		except:
			print('Error connecting to server')
			print('Usage:', 'host:port')
			print('e.g.', 'localhost:31425')
			exit()
		print('Truco client started')

if __name__ == "__main__":
	c = Client()



