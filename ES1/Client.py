import truco
from PodSixNet.Connection import ConnectionListener, connection 

class Client(ConnectionListener):

	def __init__(self):

		self.me = truco.Player()
		self.board_cards = []
		self.turned_card = None
		self.num = None
		self.running = False
		self.received_cards = False

		print('conectando')
		self.Connect()
		while True:
			connection.Pump()
			self.Pump()
			if self.running:
				if self.received_cards:
					print("CARTAS: 	")
					print(self.me.hand)
					print("CARTA QUE VIROU: ")
					print(self.turned_card)
					self.running = False

	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]

	def Network_win(self, data):
		self.me.score += 1

	def Network_lose(self, data):
		pass

	def Network_receive_board_card(self, data):
		card = truco.Card(data["card"]["rank"], data["card"]["suit"], data["card"]["isJoker"])
		self.board_cards.append(card)

	def Network_dealCards(self, data):
		if data["player"] == self.num:
			cards = self.prepare_received_cards(data["cards"])
			self.me.setHand(cards)
			self.turned_card = truco.Card(data["turned_card"]["rank"], data["turned_card"]["suit"], data["turned_card"]["isJoker"])
			self.received_cards = True

	def prepare_received_cards(self, cards):
		l = [ truco.Card(i["rank"], i["suit"], i["isJoker"]) for i in cards ] 
		return l

	def play_card(self, card_index):
		if self.me.turn:
			card = self.me.play_card(card_index)
			self.board_cards.append(card)
			connection.Send({"action": "play_card", "card": card.__dict__, "player": self.num})

if __name__ == "__main__":
	c = Client()



