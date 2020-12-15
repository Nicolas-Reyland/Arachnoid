# Trying server.start(custom_read_f-> tasks.append etc.)
import arachnoid as ara
import interpreter as inter

print('PID: {}'.format(ara.get_pid()))

def main():
	server = ara.Web('192.168.43.33', 1234)
	server.init()
	thread = ara.Thread(target=server.start(read_f))
	thread.start()

	inter.interpreter()

if __name__ == '__main__':
	main()

