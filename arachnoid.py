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
 - being able to close the server in a controlled way
 - something incredible
 -

'''


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

	def __init__(self, host, port, max_clients=10, max_buffer_size=5120, server_in_file='server in.txt', server_out_file='server out.txt', hashing='none', verbose=1):

		# Server Info
		self.host = host
		self.port = port
		self.max_clients = max_clients
		self.max_buffer_size = max_buffer_size

		# Server File Handler
		self.server_in_file = server_in_file
		open(self.server_in_file, 'wb').write(b'')
		self.file_in_handler = open(self.server_in_file, 'ab')

		self.server_out_file = server_out_file
		open(self.server_out_file, 'wb').write(b'')
		self.file_out_handler = open(self.server_out_file, 'rb')

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

		# lambdas
		self.cprint = lambda s, level='info': print('[{}] {}'.format(self._level_tags[level], s)) if self.verbose else None
		self.df_read_f = self.file_out_handler.read

	def write_in(self, s):
		if type(s) == str:
			s = s.encode('utf8')
		self.file_in_handler.write(s)
		self.file_in_handler.close()
		self.file_in_handler = open(self.server_in_file, 'ab')

	def err_exit(self):
		print_exc()
		sys.exit()

	def init(self):
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.cprint('Socket created.')
		self._init_done = True

	def start(self, read_f):
		try:
			self.soc.bind((self.host, self.port))
		except:
			self.err_exit()

		self.soc.listen(self.max_clients)
		self.cprint('Listening...')

		self._started = True
		open('OK Flag.txt', 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir():
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
				self.connections[ip]['thread'] = Thread(target=self.client_thread, args=(connection, ip, port, self.max_buffer_size, self.df_read_f))
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

		while self.alive and 'OK Flag.txt' in os.listdir():
			client_input = connection.recv(max_buffer_size)
			client_input_size = len(client_input)

			if client_input_size > max_buffer_size:
				self.cprint('Input greater than max buffer size: {}>{}. Exiting'.format(client_input_size, max_buffer_size), 'error')
				break

			client_input = client_input.rstrip()

			if client_input == self.bexit_flag:
				self.cprint('Client is requesting to exit.')
				break

			elif client_input == '<STOP>':
				self.close()
				break

			else:
				if client_input != self.bempty_flag:
					timestamp = str(datetime.now().timestamp()).encode('utf8')
					self.write_in(b'<<RECV>> %b - %b,%b: %b\n' % (timestamp, ip.encode('utf8'), str(port).encode('utf8'), client_input))
					self.cprint('recv: {} bytes -> {}'.format(len(client_input), client_input[:15]), 'msg')

				msg = read_f()
				if not msg:
					msg = self.bempty_flag
				else:
					self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:15]), 'msg')
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
	'''

	def __init__(self , ip, port, max_buffer_size=5120, client_in_file='client in.txt', client_out_file='client out.txt', additional_info={'name': '', 'purpose': ''}, verbose=1):

		# Client Info
		self.ip = ip
		self.port = port
		self.max_buffer_size = max_buffer_size
		self.additional_info = additional_info
		if not 'name' in self.additional_info.keys():
			self.additional_info['name'] = ''

		# Client File Handler
		self.client_in_file = client_in_file
		open(self.client_in_file, 'wb').write(b'')
		self.file_in_handler = open(self.client_in_file, 'ab')

		self.client_out_file = client_out_file
		open(self.client_out_file, 'wb').write(b'')
		self.file_out_handler = open(self.client_out_file, 'rb')

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
		self.file_in_handler = open(self.client_in_file, 'ab')

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
		open('OK Flag.txt', 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir():
			msg = self.file_out_handler.read()
			if not msg:
				msg = self.bempty_flag
			else:
				self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:15]), 'msg')

			self.client.sendall(msg)

			if msg == self.bexit_flag:
				self.cprint('Closing Connection.')
				break

			response = self.client.recv(self.max_buffer_size)
			if response != self.bempty_flag :
				timestamp = str(datetime.now().timestamp()).encode('utf8')
				self.write_in(b'<<RECV>> %b: %b\n' % (timestamp, response))
				self.cprint('recv: {} bytes -> {}'.format(len(response), response[:15]), 'msg')

	def loop2(self):
		open('OK Flag.txt', 'w').write('1')

		while self.alive and 'OK Flag.txt' in os.listdir():
			if self.tasks:
				msg = self.tasks[0]
				self.tasks.pop(0)
				self.cprint('sent: {} bytes -> {}'.format(len(msg), msg[:15]), 'msg')
			else:
				msg = self.bempty_flag

			self.client.sendall(msg)

			if msg == self.bexit_flag:
				self.cprint('Closing Connection.')
				break

			response = self.client.recv(self.max_buffer_size)
			if response != self.bempty_flag :
				timestamp = str(datetime.now().timestamp()).encode('utf8')
				self.write_in(b'<<RECV>> %b: %b\n' % (timestamp, response))
				self.cprint('recv: {} bytes -> {}'.format(len(response), response[:15]), 'msg')


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





