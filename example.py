# Online Rock Paper Scissors
import arachnoid

class Game:
	def __init__(self):
		self.points = 0
		self.state = -1
		self.ennemy = None

	def setup(self, ennemy):
		self.ennemy = ennemy

	def set_state(self, index):
		assert 0 <= index <= 2
		self.state = index

	def play(self):
		'''
		sign:
		0 -> Rock
		1 -> Paper
		2- > Scissors

		win:
		-1 -> draw
		0 -> loose
		1 -> win
		'''
		my_sign = self.state
		ennemy_sign = self.ennemy.state
		win = -1
		if my_sign == 0:
			if ennemy_sign == 0:
				win = -1
			elif ennemy_sign == 1:
				win = 0
			else:
				win = 1
		elif my_sign == 1:
			if ennemy_sign == 0:
				win = 1
			elif ennemy_sign == 1:
				win = -1
			else:
				win = 0
		else:
			if ennemy_sign == 0:
				win = 1
			elif ennemy_sign == 1:
				win = -1
			else:
				win = 0

def player1_server():
	server = arachnoid.Web('127.0.0.1', 1234, 2)
	server.init()
	server.start()

def player2_client():
	client = arachnoid.Spider('127.0.0.1', 1234)
	client.connect()
	client.loop()

def player1():
	arachnoid.Thread(target=player1_server).start()
	

	move = input('R,P,S: ')
	move = ['R', 'P', 'S'].index(move)

	while True:
		data = open('server in.txt', 'r').read()
		if data != '':
			break

	print('move, data', move, data)

def player2():
	arachnoid.Thread(target=player2_client).start()

	move = input('R,P,S: ')
	move = ['R', 'P', 'S'].index(move)

	file = open('server out.txt', 'a')
	file.write(str(move))
	file.close()

	print('move p2', move)
