from collections import deque
import random
'''
Naipes e ranks ordenados por força
'''		
SUITS = 'DSHC'
RANKS = '4567QJK123'

class Card(object):

	def __init__(self, rank, suit):
		super(Card, self).__init__()
		self.rank = rank
		self.suit = suit
		self.isJoker = False

	def __str__(self):
		return "%s%s" % (self.rank, self.suit)

	def __repr__(self):
		return self.__str__()

	def __gt__(self, other):
		if self.isJoker and other.isJoker:
			for i, s in enumerate(SUITS):
				if s == self.suit:
					a_power = i
				if s == other.suit:
					b_power = i
			return a_power > b_power
		elif self.isJoker:
			return True
		elif other.isJoker:
			return False
		else:
			for i, r in enumerate(RANKS):
				if r == self.rank:
					a_power = i
				if r == other.rank:
					b_power = i
			return a_power > b_power

	def __eq__(self, other):
		if self.isJoker or other.isJoker:
			return False
		else:
			return self.rank == other.rank


	def __ge__(self, other):
		return self > other or self == other



class Deck(deque):

	def __init__(self):
		super(Deck, self).__init__()
		self.generate()

	def generate(self):
		self.clear()
		for s in SUITS:
			for r in RANKS:
				self.append(Card(r, s))

	def shuffle(self):
		random.shuffle(self)
		return self

	def get_turned_card(self):
		turned_card = self.pop()	
		return turned_card



class Player(object):
	
	def __init__(self):
		super(Player, self).__init__()
		self.hand = []

	def setHand(self, cards):
		self.hand.extend(cards)

	def playCard(self, card):
		for i, c in enumerate(self.hand):
			if c is card:
				return self.hand.pop(i)

	def __repr__(self):
		return str(self.hand)


		
'''
d = Deck()
p = Player()
for _ in range(3):
	p.hand.append(d.popleft())
print('------DECK------')
for i in d:
	print(i)
print('------HAND-------')
print(p.hand)
print("----teste-----")
print(p.playCard(p.hand[0]))
print('------HAND-------')
print(p.hand)


g = Game()
for i in g.players:
	print(i)
	i.playCard(input("rank: "), input("suit: "))
	print(i)
'''