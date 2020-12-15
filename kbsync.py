# Keyboard Synchronization
import arachnoid as ara
#import win32api, win32con
from pynput import keyboard
import os, sys

print('PID: {}'.format(ara.get_pid()))

IP_ADDR = '192.168.1.94'#'43.33'
PORT_NUMBER = 5555
#KB_LAYOUT = win32api.GetKeyboardLayout()
'''
def get_key_strokes(from_=0, to=250):
	return list(filter(lambda key: win32api.GetAsyncKeyState(key), range(from_, to)))

def simple_key_press(key):
	win32api.keybd_event(key, 0, 0, 0)
	ara.time.sleep(.05)
	win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

def hold_key_press(keys):
	# press keys in order (e.g. control + shift + a)
	for key in keys:
		win32api.keybd_event(key, 0, 0, 0)
		ara.time.sleep(.05)
	# release keys in reverse order
	for key in keys[::-1]:
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
		ara.time.sleep(.1)

def change_keyboard_layout(layout):
	win32api.LoadKeyboardLayout(layout, 1)
'''

def on_press(key):
	global server
	if type(key) == keyboard.Key:
		key_code = key.value.vk
	else:
		assert type(key) == keyboard.KeyCode
		key_code = key.vk
	server.tasks.append(b'<KEY-PRESS %i>' % key_code)
	#print('pressed {}'.format(key_code))

def on_release(key):
	global server
	if key == keyboard.Key.esc:
		return False
	#key_code = key.vk
	#server.tasks.append(b'<KEY-RELEASE %i>' % key_code)
	if not server.alive:
		return False

def simple_key_press(key_code):
	key = keyboard.KeyCode(key_code)
	controller.press(key)

def sync_keyboard_client(client):
	open('OK Flag.txt', 'w').write('1')
	special_values = vars(keyboard.Key)

	while client.alive and 'OK Flag.txt' in os.listdir():
		if client.tasks:
			msg = client.tasks[0]
			client.tasks.pop(0)
		else:
			msg = client.bempty_flag

		client.client.sendall(b'<>')

		response = client.client.recv(client.max_buffer_size)

		if response != client.bempty_flag:
			response = response.decode('utf8')
			tag = response[1:response.index(' ')]
			if tag == 'KEY-PRESS':
				key_code = int(response[10:-1])
				simple_key_press(key_code)
				#print('pressing key {}'.format(key_code))
			# elif tag == 'KEY-COMBO': ...
			else:
				print('Unkown tag: {}'.format(tag))

def client_side():
	client = ara.Spider(ip=IP_ADDR, port=PORT_NUMBER, verbose=1)
	client.connect()
	thread = ara.Thread(target=client.loop2)
	thread.start()

	thread2 = ara.Thread(target=sync_keyboard_client, args=(client,))
	thread2.start()

	input('stop')

	thread.join()
	thread2.join()

	os.system('taskkill /f /pid {}'.format(ara.get_pid()))

def server_side():
	global server
	server = ara.Web(host=IP_ADDR, port=PORT_NUMBER, verbose=1)
	server.tasks = []
	server.init()

	def read_keyboard_info(server):
		if server.tasks:
			return server.tasks.pop(0)
		else:
			None

	'''
	def send_keyboard_info(server): # send mouse info to server
		global last_pos
		MAX_KEY_CHUNK_SIZE = 30 # one key is defined by a group of n key, up to MAX_KEY_CHUNK_SIZE times the same key
		while True:
			key_strokes = get_key_strokes()
			if key_strokes:

				chunk_size = 0
				last_key_stroke = key_strokes[0]
				server.tasks.append(b'<KEY-PRESS %i>' % last_key_stroke)
				print('counted {} times {} key'.format(key_strokes.count(last_key_stroke), last_key_stroke))

				for key in key_strokes:
					if key == last_key_stroke:
						chunk_size += 1
					else:
						server.tasks.append(b'<KEY-PRESS %i>' % key)
						last_key_stroke = key
						chunk_size = 0
					if chunk_size >=  MAX_KEY_CHUNK_SIZE: # >= because if the next one is not last_key_stroke, the ky won't repeat. So, the key repeats only if chunk_size > MAX_KEY_CHUNK_SIZE (next iteration, if key == last_key_stroke)
						chunk_size = 0
				ara.time.sleep(.01)
	'''

	def send_keyboard_info():
		with keyboard.Listener(
				on_press=on_press,
				on_release=on_release) as listener:
			listener.join()

	thread = ara.Thread(target=lambda : server.start(read_f=lambda : read_keyboard_info(server)))
	thread2 = ara.Thread(target=send_keyboard_info)

	thread.start()
	thread2.start()

	input('stop')

	os.system('taskkill /f /pid {}'.format(ara.get_pid()))

if __name__ == '__main__':
	if sys.argv[-1] == 'server':
		server_side()
	elif sys.argv[-1] == 'client':
		controller = keyboard.Controller()
		client_side()
	else:
		raise ValueError('Unkown value for mouse sync role...')




