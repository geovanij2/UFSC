import truco

class Game(object):

	START_CARDS_LEN = 3
	START_PLAYERS_LEN = 4
	
	def __init__(self):
		super(Game, self).__init__()
		self.deck = Deck().shuffle()
		self.players = [ Player() for i in range(self.START_PLAYERS_LEN) ]
		self.dealCards()

	def dealCards(self):
		for i in self.players:
			c = [ self.deck.pop() for j in range(self.START_CARDS_LEN) ]
			i.setHand(c)		


'''with open("aaaaaaaaaaaa.txt", "a") as f:
	for i in range(10):
		f.write("teste %s" % (i) + "\n")'''