import truco
from PodSixNet.Connection import ConnectionListener, connection 

class Client(ConnectionListener):

	def __init__(self):

		self.me = truco.Player()
		self.board_cards = []
		self.turned_card = None
		self.num = None

		print('conectando')
		self.Connect()
		while True:
			connection.Pump()
			self.Pump()

c = Client()



