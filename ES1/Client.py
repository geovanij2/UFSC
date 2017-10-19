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
					print(self.turned_card)
					self.running = False

	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]

	def Network_dealCards(self, data):
		if data["player"] == self.num:
			self.me.setHand(data["cards"])
			self.turned_card = truco.Card(data["turned_card"]["rank"], data["turned_card"]["suit"], data["turned_card"]["isJoker"])
			self.received_cards = True

c = Client()



