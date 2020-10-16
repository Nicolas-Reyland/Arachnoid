# Trying client.loop2
import arachnoid as ara
import interpreter as inter

print('PID: {}'.format(ara.get_pid()))

def main():
	client = ara.Spider('192.168.43.33', 1234)
	client.connect()
	thread = ara.Thread(target=client.loop2)
	thread.start()

	thread2 = ara.Thread(target=lambda : inter.message_printer(file_path='client in.txt'))
	thread2.start()

	inter.shell2(client)

	thread.join()
	thread2.join()

if __name__ == '__main__':
	main()

