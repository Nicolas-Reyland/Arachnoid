# Arachnoid - Usage script
import arachnoid
from argparse import ArgumentParser

print(f'PID: {arachnoid.os.getpid()}')

parser = ArgumentParser(description='Quick & basic use of Arachnoid')

parser.add_argument('-r'
					'--role',
					metavar='r__role',
					type=str,
					help='role: [server, client]')

parser.add_argument('-ip',
					'--ip-address',
					metavar='ip-address',
					type=str,
					help='host/ip address',
					default='127.0.0.1')

parser.add_argument('-p',
					'--port',
					metavar='port',
					type=int,
					help='port number',
					default=1234)

parser.add_argument('-m',
					'--max-clients',
					metavar='max-clients',
					type=int,
					help='max clients for server',
					default=10)

parser.add_argument('-b',
					'--max-buffer-size',
					metavar='max-buffer-size',
					type=int,
					help='max buffer size for sockets',
					default=5120)

parser.add_argument('-i',
					'--input-file',
					metavar='input-file',
					type=str,
					help='input file',
					default='input.txt')

parser.add_argument('-o',
					'--output-file',
					metavar='output-file',
					type=str,
					help='output file',
					default='output.txt')

parser.add_argument('-v',
					'--verbose',
					metavar='verbose',
					type=int,
					help='verbose [0, 1]',
					default=1)

args = vars(parser.parse_args())
print(args)

open('pid.txt', 'w').write(str(arachnoid.get_pid()))

if args['r__role'] == 'server':
	server = arachnoid.Web(
							host=args['ip_address'],
							port=args['port'],
							max_clients=args['max_clients'],
							max_buffer_size=args['max_buffer_size'],
							server_in_file=args['input_file'],
							server_out_file=args['output_file'],
							verbose=args['verbose']
						)
	server.init()
	server.start(server.df_read_f)
	server.close()

elif args['r__role'] == 'client':
	client = arachnoid.Spider(
							ip=args['ip_address'],
							port=args['port'],
							max_buffer_size=args['max_buffer_size'],
							client_in_file=args['input_file'],
							client_out_file=args['output_file'],
							verbose=args['verbose']
						)
	client.connect()
	client.loop()
	client.close()

else:
	raise ValueError('role must be "server" or "client"')



r'''
cd c:\Documents\python\networking\Arachnoid
python use.py -r server
python use.py -r client

'''

# yup

