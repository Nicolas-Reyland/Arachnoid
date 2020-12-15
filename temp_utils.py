SERVER_OUT = 'server out.txt'
SERVER_IN = 'server in.txt'

CLIENT_OUT = 'client out.txt'
CLIENT_IN = 'client in.txt'

def clear_s():
	global SERVER_OUT
	open(SERVER_OUT, 'w').write('')
	global SERVER_IN
	open(SERVER_IN, 'w').write('')

def clear_c():
	global CLIENT_OUT
	open(CLIENT_OUT, 'w').write('')
	global CLIENT_IN
	open(CLIENT_IN, 'w').write('')

def clear_so():
	global SERVER_OUT
	open(SERVER_OUT, 'w').write('')

def clear_si():
	global SERVER_IN
	open(SERVER_IN, 'w').write('')

def clear_co():
	global CLIENT_OUT
	open(CLIENT_OUT, 'w').write('')

def clear_ci():
	global CLIENT_IN
	open(CLIENT_IN, 'w').write('')

def send_c(s):
	global CLIENT_OUT
	file = open(CLIENT_OUT, 'a')
	file.write(s)
	file.close()

def send_s(s):
	global SERVER_OUT
	file = open(SERVER_OUT, 'a')
	file.write(s)
	file.close()
