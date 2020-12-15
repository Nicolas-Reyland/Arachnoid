# Mouse Syncronization
import arachnoid as ara
import win32api, win32con, os, sys

IP_ADDR = '192.168.43.33'
PORT_NUMBER = 5555
SCREEN_WIDTH = win32api.GetSystemMetrics(0) # used for mapping all mouse coords to 1920/1080.
SCREEN_HEIGHT = win32api.GetSystemMetrics(1) # used for mapping all mouse coords to 1920/1080.

print('PID: {}'.format(ara.get_pid()))

def map_mouse_pos(pos):
	x,y = pos
	if SCREEN_WIDTH != 1920:
		x = int(x * SCREEN_WIDTH/1920)
	if SCREEN_HEIGHT != 1080:
		y = int(y * SCREEN_HEIGHT/1080)
	return (x,y)

def set_mouse_pos(pos):
	win32api.SetCursorPos(pos)
	# win32api.SetCursorPos((x,y)) is better to be replaced by win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))

def get_mouse_pos():
	return win32api.GetCursorPos()

def mouse_left_click(pos):
	x,y = pos
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def mouse_right_click(pos):
	x,y = pos
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)

def sync_mouse_client(client):
	open('OK Flag.txt', 'w').write('1')

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
			if tag == 'MOUSE-POS':
				pos = response[11:-1].split('-')
				pos = (int(pos[0]), int(pos[1]))
				mapped_pos = map_mouse_pos(pos)
				set_mouse_pos(mapped_pos)
			elif tag == 'MOUSE-PRESS':
				value = int(response[13])
				if value == 1:
					pos = get_mouse_pos()
					mouse_left_click(pos)
				elif value == 2:
					pos = get_mouse_pos()
					mouse_right_click(pos)
				else:
					print('Unkown mouse press value {}'.format(value))
			else:
				print('Unkown tag: {}'.format(tag))


def client_side():
	client = ara.Spider(IP_ADDR, PORT_NUMBER, verbose=0)
	client.connect()
	thread = ara.Thread(target=client.loop2)
	thread.start()

	thread2 = ara.Thread(target=sync_mouse_client, args=(client,))
	thread2.start()

	input('stop')

	thread.join()
	thread2.join()

	os.system('taskkill /f /pid {}'.format(ara.get_pid()))


def server_side():
	server = ara.Web(IP_ADDR, PORT_NUMBER, verbose=0)
	server.tasks = []
	server.init()

	global last_pos
	last_pos = get_mouse_pos()

	def read_mouse_info(server):
		if server.tasks:
			return server.tasks.pop(0)
		else:
			None

	def send_mouse_info(server): # send mouse info to server
		global last_pos
		WAIT_TIME = int(sys.argv[-2]) / 1000
		while True:
			cur_pos = get_mouse_pos()
			if last_pos != cur_pos:
				mapped_pos = map_mouse_pos(cur_pos)
				server.tasks.append(b'<MOUSE-POS %i-%i>' % (mapped_pos[0], mapped_pos[1]))
				last_pos = cur_pos[:]
				ara.time.sleep(WAIT_TIME)
			left_state = win32api.GetKeyState(0x01)
			right_state = win32api.GetKeyState(0x02)
			if left_state not in [0,1]:
				server.tasks.append(b'<MOUSE-PRESS 1>')
			if right_state not in [0,1]:
				server.tasks.append(b'<MOUSE-PRESS 2>')


	thread = ara.Thread(target=lambda : server.start(read_f=lambda : read_mouse_info(server)))
	thread2 = ara.Thread(target=send_mouse_info, args=(server,))

	thread.start()
	thread2.start()

	input('stop')

	os.system('taskkill /f /pid {}'.format(ara.get_pid()))

if __name__ == '__main__':
	if sys.argv[-1] == 'server':
		server_side()
	elif sys.argv[-1] == 'client':
		client_side()
	else:
		raise ValueError('Unkown value for mouse sync role...')


