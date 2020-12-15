# Project Arachnoid
import socket, sys
from threading import Thread
from traceback import print_exc
from datetime import datetime
import time
import hashlib
import json
import os

'''
#TODO:
 - server and client, none are the rooter				- DONE
 - check if client dead from time to time
 - using hashing
 - encryption
 - being able to close the server in a controlled way	- let's say this is controlled
 - something incredible
 - sync mouse/keyboard									- IN PROGRESS

 - run process in parallel
 - clone a process
 	(first start with: close Chrome tabs,
 	then whole process etc.)

#QUICK TODO:
 - get a remote shell
 - new tag, saying command ran good & such.
 	So input() in shell is delayed until we know
 	command passed through and something happened 
 	SAFE MODE only, tho)
 -

'''


ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
KILL_TASK_ON_CLOSE = True
_LEVEL_TAGS = {'info' : '!', 'msg': '-', 'unexpected': '?', 'warning': 'W', 'error': 'E'}
hashlib_vars = vars(hashlib)
hash_func_struct = lambda name: lambda x: hashlib_vars[name](x).hexdigest()
HASHING_DICT = {
				'none': lambda x: x.decode('utf8'),
				'md5': hash_func_struct('md5'),
				'sha1': hash_func_struct('sha1'),
				'sha224': hash_func_struct('sha224'),
				'sha256': hash_func_struct('sha256'),
				'sha384': hash_func_struct('sha384'),
				'sha3_224': hash_func_struct('sha3_224'),
				'sha3_256': hash_func_struct('sha3_256'),
				'sha3_384': hash_func_struct('sha3_384'),
				'sha3_512': hash_func_struct('sha3_512'),
				'sha512': hash_func_struct('sha512')
				}



class Web:
	'''
	'''

	def __init__(self, host, port, max_clients=10, max_buffer_size=5120, server_in_file='server in.txt', server_out_file='server out.txt', hashing='none', verbose=0):

		# Server Info
		self.host = host
		self.port = port
		self.max_clients = max_clients
		self.max_buffer_size = max_buffer_size

		# Server File Handler
		self.server_in_file = server_in_file
		open(os.path.join(ROOT_DIR, self.server_in_file), 'wb').write(b'')
		self.file_in_handler = open(os.path.join(ROOT_DIR, self.server_in_file), 'ab')

		self.server_out_file = server_out_file
		open(os.path.join(ROOT_DIR, self.server_out_file), 'wb').write(b'')
		self.file_out_handler = open(os.path.join(ROOT_DIR, self.server_out_file), 'rb')

		# variables & flags
		self.soc = None
		self.alive = True
		self.connections = {}
		self._init_done = False
		self._started = False
		self.empty_flag = '<>'
		self.bempty_flag = self.empty_flag.encode('utf8')
		self.exit_flag = '<EXIT>'
		self.bexit_flag = self.exit_flag.encode('utf8')
		self.verbose = verbose
		global _LEVEL_TAGS
		self._level_tags = _LEVEL_TAGS
		self.in_tasks, self.out_tasks = [], []
		self.df_client_thread = self.client_thread

		# lambdas
		self.cprint = lambda s, level='info': print('[{}] {}'.format(self._level_tags[level], s)) if self.verbose else None
		self.df_read_f = self.file_out_handler.read

	def write_in(self, s):
		if type(s) == str:
			s = s.encode('utf8')
		self.file_in_handler.write(s)
		self.file_in_handler.close()
		self.file_in_handler = open(os.path.join(ROOT_DIR, self.server_in_file), 'ab')

	def err_exit(self):
		print_exc()
		sys.exit()

	def init(self):
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.cprint('Socket created.')
		self._init_done = True

	def start(self, read_f='default'):
		if read_f == 'default':
			read_f = self.df_read_f
		try:
			self.soc.bind((self.host, self.port))
		except:
			self.err_exit()

		self.soc.listen(self.max_clients)
		self.cprint('Listening...')

		self._started = True
		open(os.path.join(ROOT_DIR, 'OK Flag.txt'), 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir(ROOT_DIR):
			connection, addr = self.soc.accept()
			ip, port = addr[0], addr[1]
			self.cprint('Connection recieved with ip: {} port: {}'.format(ip, port))

			self.connections[ip] = {
									'connection': connection,
									'ip': ip,
									'port': port,
									'name': '',
									'thread': None,
									'timer': 0,
									'info': {}
									}

			try:
				self.cprint('Sending Server info...')
				server_info = json.dumps({'exit flag': self.exit_flag, 'empty flag' : self.empty_flag, 'host': self.host, 'port': self.port, 'max buffer size': self.max_buffer_size})
				server_info = server_info.encode('utf8')
				connection.sendall(server_info)
				self.connections[ip]['thread'] = Thread(target=self.df_client_thread, args=(connection, ip, port, self.max_buffer_size, read_f))
				self.connections[ip]['thread'].start()
				self.cprint('Client Thread started')
			except:
				self.err_exit()

	def client_thread(self, connection, ip, port, max_buffer_size, read_f):
		client_info = connection.recv(max_buffer_size)
		client_info = client_info.decode('utf8').rstrip()
		print('raw client info', client_info)
		if client_info[-1] != '}':
			client_info = client_info[:-list(client_info)[::-1].index('}')]
		print('client info', client_info)
		client_info = json.loads(client_info)
		name = client_info['name']
		self.connections[ip]['name'] = name
		self.connections[ip]['info'] = client_info # yep, copy of name in this dict (bc why not ?)

		while self.alive and 'OK Flag.txt' in os.listdir(ROOT_DIR):
			client_input = connection.recv(max_buffer_size)
			client_input_size = len(client_input)

			if client_input_size > max_buffer_size:
				self.cprint('Input greater than max buffer size: {}>{}. Exiting'.format(client_input_size, max_buffer_size), 'error')
				break

			client_input = client_input.rstrip()

			if client_input == self.bexit_flag:
				self.cprint('Client is requesting to exit.')
				break

			elif client_input == b'<STOP>':
				self.close()
				break

			else:
				if client_input != self.bempty_flag:
					timestamp = str(datetime.now().timestamp()).encode('utf8')
					self.write_in(b'<<RECV>> %b - %b,%b: %b\n' % (timestamp, ip.encode('utf8'), str(port).encode('utf8'), client_input))
					self.cprint('recv: {} bytes -> {}'.format(len(client_input), client_input[:30]), 'msg')

				msg = read_f()
				if not msg:
					msg = self.bempty_flag
				else:
					self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:30]), 'msg')
				connection.sendall(msg)

		connection.close()
		self.cprint('Connection ip: {} port: {} closed.'.format(ip, port))
		sys.exit()
		return

	def client_thread2(self, connection, ip, port, max_buffer_size, *args):
		client_info = connection.recv(max_buffer_size)
		client_info = client_info.decode('utf8').rstrip()
		print('raw client info', client_info)
		if client_info[-1] != '}':
			client_info = client_info[:-list(client_info)[::-1].index('}')]
		print('client info', client_info)
		client_info = json.loads(client_info)
		name = client_info['name']
		self.connections[ip]['name'] = name
		self.connections[ip]['info'] = client_info # yep, copy of name in this dict (bc why not ?)

		while self.alive and 'OK Flag.txt' in os.listdir(ROOT_DIR):
			client_input = connection.recv(max_buffer_size)
			client_input_size = len(client_input)

			if client_input_size > max_buffer_size:
				self.cprint('Input greater than max buffer size: {}>{}. Exiting'.format(client_input_size, max_buffer_size), 'error')
				break

			client_input = client_input.rstrip()

			if client_input[-1] != 62: #! 62 -> b'>'
				print('Got corrupted data. Trying to catch the rest')

				print('command input base', client_input)

				connection.sendall(self.bempty_flag)
				client_input2 = connection.recv(max_buffer_size)

				print('command input2 base', client_input2)

				counter = 0
				while client_input2[-1] != 62:
					if len(client_input) + len(client_input2) > max_buffer_size:
						raise Exception('Recovery of corrupted data failed. buffer_size > max_buffer_size')
					# assuming this is absolutely the end and not a whole new packet...
					client_input += client_input2

					connection.sendall(self.bempty_flag)
					client_input2 = connection.recv(max_buffer_size)

					print('client input2', counter, client_input2)

					counter += 1
					if counter == 10:
						raise Exception('Tried {} times to recover corrupted data. Stopping. I sense fear.'.format(counter))

				client_input += client_input2

			if client_input == self.bexit_flag:
				self.cprint('Client is requesting to exit.')
				break

			elif client_input == b'<STOP>':
				self.close()
				break

			else:
				if client_input != self.bempty_flag:
					self.in_tasks.append(client_input) # in_tasks: recv, send to interpreter
					self.cprint('recv: {} bytes -> {}'.format(len(client_input), client_input[:30]), 'msg')

				if self.out_tasks: # out_tasks: to send, from interpreter
					msg = self.out_tasks.pop(0)
					self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:30]), 'msg')
				else:
					msg = self.bempty_flag
				connection.sendall(msg)

		connection.close()
		self.cprint('Connection ip: {} port: {} closed.'.format(ip, port))
		sys.exit()
		return

	def close(self):
		self.alive = False
		for conn in self.connections.items():
			conn['connection'].close()
			conn['thread'].join()
		self.file_in_handler.close()
		self.file_out_handler.close()
		if KILL_TASK_ON_CLOSE:
			os.system('taskkill /f /pid {}'.format(os.getpid()))


class Spider:
	'''
	🕷️
	'''

	def __init__(self, ip, port, max_buffer_size=5120, client_in_file='client in.txt', client_out_file='client out.txt', additional_info={'name': '', 'purpose': ''}, verbose=0):

		# Client Info
		self.ip = ip
		self.port = port
		self.max_buffer_size = max_buffer_size
		self.additional_info = additional_info
		if not 'name' in self.additional_info.keys():
			self.additional_info['name'] = ''

		# Client File Handler
		self.client_in_file = client_in_file
		open(os.path.join(ROOT_DIR, self.client_in_file), 'wb').write(b'')
		self.file_in_handler = open(os.path.join(ROOT_DIR, self.client_in_file), 'ab')

		self.client_out_file = client_out_file
		open(os.path.join(ROOT_DIR, self.client_out_file), 'wb').write(b'')
		self.file_out_handler = open(os.path.join(ROOT_DIR, self.client_out_file), 'rb')

		# variables & flags
		self.client = None
		self.alive = True
		self.verbose = verbose
		self._connected = False
		self.server_info = {}
		global _LEVEL_TAGS
		self._level_tags = _LEVEL_TAGS

		# lambdas
		self.cprint = lambda s, level='info': print('[{}] {}'.format(self._level_tags[level], s)) if self.verbose else None

		# alpha
		self.tasks = []

	def write_in(self, s):
		if type(s) == str:
			s = s.encode('utf8')
		self.file_in_handler.write(s)
		self.file_in_handler.close()
		self.file_in_handler = open(os.path.join(ROOT_DIR, self.client_in_file), 'ab')

	def connect(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect((self.ip, self.port))
		self.cprint('Connected to server. Gathering server information...')
		self.server_info = self.client.recv(self.max_buffer_size).decode('utf8').rstrip()
		self.write_in(str(datetime.now().timestamp()) + ' - ' + self.server_info + '\n')
		self.server_info = json.loads(self.server_info)

		self.bempty_flag = self.server_info['empty flag'].encode('utf8')
		self.bexit_flag = self.server_info['exit flag'].encode('utf8')

		self.cprint('Server info: {}'.format(self.server_info))
		self.cprint('Sending own info...')
		info = json.dumps(self.additional_info)
		info = info.encode('utf8')
		self.client.sendall(info)
		self._connected = True

	def loop(self):
		open(os.path.join(ROOT_DIR, 'OK Flag.txt'), 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir(ROOT_DIR):
			msg = self.file_out_handler.read()
			if not msg:
				msg = self.bempty_flag
			else:
				self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:30]), 'msg')

			self.client.sendall(msg)

			if msg == self.bexit_flag:
				self.cprint('Closing Connection.')
				break

			response = self.client.recv(self.max_buffer_size)
			if response != self.bempty_flag :
				timestamp = str(datetime.now().timestamp()).encode('utf8')
				self.write_in(b'<<RECV>> %b: %b\n' % (timestamp, response))
				self.cprint('recv: {} bytes -> {}'.format(len(response), response[:30]), 'msg')

	def loop2(self):
		open(os.path.join(ROOT_DIR, 'OK Flag.txt'), 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir(ROOT_DIR):
			if self.tasks:
				msg = self.tasks[0]
				self.tasks.pop(0)
				self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:30]), 'msg')
			else:
				msg = self.bempty_flag

			self.client.sendall(msg)

			if msg == self.bexit_flag:
				self.cprint('Closing Connection.')
				break

			response = self.client.recv(self.max_buffer_size)
			if response[-1] != 62: #! 62 -> b'>'
				input('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA???\n{}'.format(response))
			if response != self.bempty_flag :
				timestamp = str(datetime.now().timestamp()).encode('utf8')
				self.write_in(b'<<RECV>> %b: %b\n' % (timestamp, response))
				self.cprint('recv: {} bytes -> {}'.format(len(response), response[:30]), 'msg')


	def close(self):
		self.client.close()
		self.file_in_handler.close()
		self.file_out_handler.close()
		if KILL_TASK_ON_CLOSE:
			os.system('taskkill /f /pid {}'.format(os.getpid()))


def get_pid():
	return os.getpid()

def get_ip_address():
	return socket.gethostbyname_ex(socket.gethostname())[2]





