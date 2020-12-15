# Trying server.start(custom_read_f-> tasks.append etc.)
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
open(ara.os.path.join(ara.ROOT_DIR, 'inter v2 pid.txt'), 'w').write(str(PID))
print('PID: {}'.format(PID))

def main():
	server = ara.Web(IP_ADDR, PORT_NUMBER, verbose=0)
	server.df_client_thread = server.client_thread2
	server.init()

	thread = ara.Thread(target=server.start)
	thread.start()

	inter.VERBOSE = server.verbose
	inter.interpreter2(server, additional_data={'inter': inter, 'arachnoid': server})

if __name__ == '__main__':
	main()

