# Arachnoid Client Shell - Version 2 : Usage
'''
This version of the client brings enormous speed optimization
(in comparaison with Arachnoid Shell Version 1 <- see interpreter.py)

The thing about Shell 2 (shot for Arachnoid Client Shell - Version 2),
is that the shell function, which is found in interpreter.py, is nto that easy to implement.
At least, not easy if you don't want to touch to the Spider class (from arachnoid.py) itself.

Therefore, a special, ugraded version of Spider.loop has been created:
Spider.loop2 (very original, I know). Spider.loop2 works with interpreter.shell2 (WOW)!
You can also use the interpreter.message_printer if you want the messages
from the server to be shown (very useful ;-}).

All this is shown in this script: shellv2 (so fking incredible).

Although, this is subject to A LOT of change...
'''

import arachnoid as ara
import interpreter as inter

IP_ADDR = '192.168.43.33'
PORT_NUMBER = 1234

for arg in ara.sys.argv:
	if arg.startswith('ip='):
		IP_ADDR = arg[3:]
		print('ip: {}'.format(IP_ADDR))
	elif arg.startswith('port='):
		PORT_NUMBER = int(arg[5:])
		print('port: {}'.format(PORT_NUMBER))

PID = ara.get_pid()
open(ara.os.path.join(ara.ROOT_DIR, 'shell v2 pid.txt'), 'w').write(str(PID))
print('PID: {}'.format(PID))

def main():
	client = ara.Spider(ip=IP_ADDR,
						port=PORT_NUMBER,
						client_in_file='client in v2.txt',
						verbose=inter.ENV_VARS['VERBOSE']
						)
	client.connect()
	thread = ara.Thread(target=client.loop2)
	thread.start()

	thread2 = ara.Thread(target=lambda : inter.message_printer(file_path=ara.os.path.join(ara.ROOT_DIR, 'client in v2.txt')))
	thread2.start()

	thread3 = ara.Thread(target=lambda : inter.interpreter(file_path=ara.os.path.join(ara.ROOT_DIR, 'client in v2.txt'), announce=False, ignores=['restart', 'shutdown']))
	thread3.start()

	inter.client_stop_function = client.tasks.clear
	inter.shell2(client, inter)

	thread.join()
	thread2.join()

if __name__ == '__main__':
	main()

