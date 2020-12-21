# Arachnoid - Interpreterimport platformimport osimport sysimport subprocessimport jsonimport timeimport base64import tracebackimport webbrowserimport hashlibfrom string import ascii_letters as alphabetfrom random import choicefrom glob import globfrom shutil import copy as copy_fileimport utilsimport os_utilsfrom map_network import map_local_network'''#TODO 🐝 : - sendfile: see if data received correctly. if not, resend until it has arrived uncorrupted. - sendfile backup system (~redo) - many other things - sync directory - get file explorer via network -emojis: 🐜, 🐛, 🦟, 🦋, 🐝, 🪳, 🪲, 🪲, 🔬, 🦗, 🕷️, 🐞, 🕸️, 🔒, 🔑, 🔓, 🔐, 🔏, 🌐, 📡, 🔗, 📁, 📂emojis+: https://emojipedia.org/search/?q=computer'''ENV_VARS = {			'ROOT DIR': os.getcwd(),			'VERBOSE': 0,			'SHELL VERSION': None,			'INTERPRETER VERSION': None,			'IN SHELL': 0,			'MAX BUFFER SIZE': 5120,			'DF WAIT TIME': 0,			'CORE FILES': ['arachnoid.py', 'use.py', 'interpreter.py', 'interpreterv2.py', 'shellv2.py', 'os_utils.py', 'utils.py'],			'SAFE MODE': 1,			'OS DIFF': None,			'LAST EXC': None,			'SHELL MODE': False,			'PING TIME': None			}MISCELLANEOUS = {}COMMAND_DICT = {'raw-out': [],			# raw-out: the sent commands (in order), as sent				'raw-run': [],			# raw-run: the commands that were ran (locally)				'raw-run-user': [],		# raw-run-user: the commands that were written by the user (no sub-calls)				'writefile-hist': {}	# history of sendfile, for corruption repair				}hashlib_vars = vars(hashlib)hash_func_struct = lambda name: lambda x: hashlib_vars[name](x).hexdigest()HASHING_DICT = {				'none': lambda x: x.decode('utf8'),				'md5': hash_func_struct('md5'),				'sha1': hash_func_struct('sha1'),				'sha224': hash_func_struct('sha224'),				'sha256': hash_func_struct('sha256'),				'sha384': hash_func_struct('sha384'),				'sha3_224': hash_func_struct('sha3_224'),				'sha3_256': hash_func_struct('sha3_256'),				'sha3_384': hash_func_struct('sha3_384'),				'sha3_512': hash_func_struct('sha3_512'),				'sha512': hash_func_struct('sha512')				}FILE_IN_PATH  = 'input.txt'FILE_OUT_PATH = 'output.txt'vprint = lambda *args: print(*args) if ENV_VARS['VERBOSE'] else Nonecommand_dict = {	# A is the current instance of a Web/Spider. B is the other communicator.					# A sends the commands. B runs them					# if a command does not work/is kinda broken when using the a certain shell/interpreter version,					# the "", "" is preceeded by a ("s1" || "s2") ||/&& ("i1" || "i2") ||/&& ("v1" || "v2")					# to show on which versions the command works					# arguments in [brackets] are optional/not needed				'networking/data-transfer': {					'ping':						("ping 						", " A pings B. print the time it took for a request to go to B and back to A."),					'sendfile':					("sendfile path 			", " A send the file using path to B"),					'getfile':					("getfile path 				", " A requests B to send the file at the path"),					'sendfiles':				("sendfiles filter/list 	", """ A sends all the files that correspond to the												unix-like file-filter of filter, or												a list of files given like this: "path-1" "path-2" ... "path-n\""""),					'getfiles':					("getfiles filter/list 		", """ B requests A to send all the files that correspond to the"												unix-like file-filter of filter, or												a list of files given like this: "path-1" "path-2" ... "path-n\""""),					'reset-file':				("reset-file				", " reset last file that was sent to A by B (you often want \"run reset-file\")"),					'sync-dir':					("sync dir1 dir2			", " sync two directories (from dir1 to dir2)"),					'map-local-network':		("map-local-network iface	", " lists all the ip-addresses connected to the local network"),					'get-shell':				("get-shell					", " create a local shell instance on B. interact with it using \"run shell-use\" or \"shell-interactive\""),					'shell-use':				("shell-use function [args] ", """ call the function by name of the Shell utils.instance. If args are give, they are passed too.												Sends the output (if there is) as a message"""),					'shell-interactive':		("shell-interactive 		", " If you have created a shell instance on B using \"get-shell\", get a handle on that shell and interact with it."),				},				'version-sync/error-handlig': {					'shutdown':					("shutdown 					", " shutdown A & B"),					'restart':					("restart 			v1		", " restart A & B (does not work on shell/interpreter version 2)"),					'sync':						("sync 						", " sync the \"CORE FILES\" from ENV_VARS (Arachnoid projects core files) from A to B"),					'synci':					("synci 			v1		", " sync the interpreter.py file (this one) from A to B and restarts (\"restart\")"),					'sync+':					("sync+ 			v1		", " executes \"sync\" then \"restart\""),				},				'basics': {					'run':						("run command 	 			", " B runs the command locally (as if B sent \"command\" to A)"),					'cmd':						("cmd command 				", " B runs \"command\" in a shell (windowns ", " cmd)"),					'clear':					("clear 					", " clears the stdout, leaving only a line displaying the current process' PID"),					'shell-mode':				("shell-mode	broken		", " A gets a shell of B (broken)"),					'cd':						("cd [dir]					", """ change the directory to path."											the "~" is equal to the ENV_ARGS['ROOT DIR']											if no dir is given, it is equal to "cd ~"""),					'ls':						("ls [filter]				", """ prints the content of the current directory."											If filter is given, prints all the files/dirs corresponding to the unix-like filter"""),					'exit':						("exit 						", " exit the program (using strength !)"),					'man':						("man command-name 			", " prints the description of a command, just like here ;-)"),					'help':						("help						", " show this help message"),				},				'miscellaneous': {					'open-tab':					("open-tab url				", " open a chrome tab using url"),					'sync-chrome':				("sync-chrome 				", " sync all the tabs from A to B (Chrome only for now)"),					'send-msg':					("send-msg msg 				", " send a message msg to B"),					'send-raw':					("send-raw b 				", " send b (encodes it to bytes) as it is to B"),					'store':					("store \"key\" \"value\"	", " MISCELLANEOUS[key] = value, vprint if overwriting"),					'miscellaneous':			("miscellaneous key 		", " prints(MISCELLANEOUS[key]) (as in get)"),				},				'debugging': {					'verb':						("verb [value]				", """ set the VERBOSE value to value. if no argument is given,"											it prints the vurrent VERBOSE value"""),					'stop-all':					("stop-all 					", " empties the list of tasks to send (use case: an infinite loop fills th task list)"),					'resend-last':				("resend-last 				", " resend last command that was sent (includes sub-commands)"),					'send-command-from-dict':	("send-command-from-dict i	", " send the command from the command history with index i"),					'corrupt-command':			("corrupt-command			", " {NOT IMPLEMENTED} command to send when some received data has been corrupted (could do differently, more deep in the mode ;-))"),					'get':						("get key 					", " prints the value of ENV_VARS[key]"),					'set':						("set \"key\" \"value\"		", " ENV_VARS[key] = value (cast int to value if it can)"),					'get':						("get key 					", " prints the value of ENV_VARS[key]"),					'list-env-vars':			("list-env-vars				", " prints every key, value from ENV_VARS"),					'last-exc':					("print-exc					", " prints the last error that occured"),					'help-hidden':				("help-hidden				", " show a similar list on hidden commands"),					'print-stdout':				("print-stdout				", " prints the stdout of B. For debugging purposes.")				}			}hidden_command_list = [		# A ", " normally ran locally							# B ", " normally ran on other				'_cmdrun',					# B _cmdrun command 				", " runs the command in local shell				'_writefile',				# B _writefile json 				", " writes a file, given in a json format (or parts of a file)				'_send-dir-hash',			# B _send-dir-hash dir1 dir2		", " send the hash of dir1 and gives dir2 back				'_sync-dir-hash',			# A _sync-dir-hash dir-hash dir2	", " generates a list of changes to be doen on 'other' directory				'_apply-dir-sync'			# B _apply-dir-sync changes			", " apply a list of changes to a directory for it to be synced with a local one			]'''TAGS:	<COMMAND >	<MESSAGE >	<EXIT>	<STOP>	<custom-tags...> (e.g. MOUSE-POS, MOUSE-PRESS)'''r'''file_path = r'C:\Users\Nicolas\AppData\Local\Google\Chrome\User Data\Default\History'bdb = open(file_path, 'rb').read()open('dbcopy', 'wb').write(bdb)conn = sqlite3.connect('dbcopy')cursor = conn.cursor()'''def send_raw(s):	file = open(FILE_OUT_PATH, 'a')	file.write(s)	file.close()def send_out(msg, tag): # send a msg through the OUT_FILE	if tag:		s = '<{} {}>'.format(tag, msg)	else:		s = msg	send_raw(s)def run(command, client_f, additional_data={'sub-command': False}): # run a command (human||machine)	'''	run(command, client_f, additional_data={}) ", " None	gets a command, runs it (arbitrarily)	commands are meant to be run from the user and/or machine.	the commands may be doing stuff that is not implied in the name.	I'm sorry, but this is way too exiting to write correct code (for now, will come sometime)	'''	global ENV_VARS, MISCELLANEOUS	global COMMAND_DICT	COMMAND_DICT['raw-run'].append(command)	if not 'sub-command' in list(additional_data.keys()):		additional_data['sub-command'] = False	elif not additional_data['sub-command']:		COMMAND_DICT['raw-run-user'] = command	command = command.split(' ')	# PRECOMMANDS:	if command[0].startswith('sync'):		TEMP_DIR = os.getcwd()		os.chdir(ENV_VARS['ROOT DIR'])	else:		TEMP_DIR = None	if ENV_VARS['SHELL VERSION'] == 1 and ENV_VARS['VERBOSE']:		vprint('running command: {}'.format(command[0]))	# MAIN COMMANDS:	if command[0] == 'help':		print('Commands:')		for category,command_list in list(command_dict.items()):			print(f'  Category: {category}')			for command_name,_ in list(command_dict[category].items()):				print(f'   - {command_name}')		print('type man "command name" to get a description of the command')	elif command[0] == 'help-hidden':		print('Hidden Commands:\n - {}'.format('\n - '.join(hidden_command_list)))	elif command[0] == 'exit':		# should be handled externally		return	elif command[0] == 'sync-dir': #! NOT TESTED YET sync dir from local to other (overwrite + delete) NOT WORKING NOW		command = ' '.join(command[1:])		_, dir_path_local, _, dir_path_request, _ = command.split('"')		client_f(f'_send-dir-hash "{dir_path_local}" "{dir_path_request}"', 'COMMAND')	elif command[0] == '_send-dir-hash':		command = ' '.join(command[1:])		_, dir_path_local, _, dir_path_request, _ = command.split('"')		dir_hash = dict(utils.hashify_dir(dir_path_request))		filepath = utils.save_obj((dir_hash, len(dir_path_request)))		run(f'sendfile {filepath}', client_f=client_f, additional_data=additional_data)		command = f'_sync-dir-hash "{dir_path_local}" "{filepath}"'		client_f(command, 'COMMAND')	elif command[0] == '_sync-dir-hash':		command = ' '.join(command[1:])		_, dir_path_local, _, filepath, _ = command.split('"')		filepath = filepath.replace('\\', '/') # dont put "\" in your folder names, dude :(		if ENV_VARS['OS DIFF']:			vprint('Changed filepath to current directory due to OS diff')			filepath = os.path.basename(filepath)		hash_dir1 = dict(utils.hashify_dir(dir_path_local, False))		hash_dir2, dir2_path_length = utils.load_obj(filepath)		change_list = utils.compare_dir_hashes(hash_dir1, hash_dir2, len(dir_path_local) + 1, dir2_path_length + 1)		cl_filepath = utils.save_obj(change_list, None)		run(f'sendfile {cl_filepath}', client_f=client_f, additional_data=additional_data)		client_f(f'_apply-dir-sync {cl_filepath}', 'COMMAND')		print('sent _apply-dir-sync', cl_filepath)	elif command[0] == '_apply-dir-sync':		filepath = ' '.join(command[1:])		change_list, _ = utils.load_obj(filepath)		utils.sync_dir(change_list)	elif command[0] == 'git-push': #! NOT TESTED YET & NOT IN COMMAND_DICT		commit_msg = ' '.join(command[1:])		if not commit_msg:			commit_msg = f'automated commit at {time.time()}'		if os_utils.is_win: and_sep = '&'		else: and_sep = '&&'		os.system(f'git add *.py {and_sep} git commit -m "{commit_msg}" {and_sep} git push')	elif command[0] == 'print-stdout': #! NOT TESTED YET		pass	elif command[0] == 'get-shell':		if len(command) > 1:			executable = ' '.join(command[1:])			vprint(f'Using custom executable: {executable}')			client_f(f'_shell-create {executable}', 'COMMAND')		else:			client_f('_shell-create', 'COMMAND')		MISCELLANEOUS['SHELL RUNNING'] = True	elif command[0] == '_shell-create':		if len(command) > 1:			executable = command[1:]		else:			executable = os_utils.get_shell_executable_name()		shell = utils.Shell(executable)		shell.start()		MISCELLANEOUS['SHELL RUNNING'] = shell		client_f(' Shell created.\n Type "shell-interactive" to get an interactive access to the shell.\n Or use manually with the "shell-use" command.', 'MESSAGE')	elif command[0] == 'shell-interactive':		assert 'SHELL RUNNING' in list(MISCELLANEOUS.keys())		assert MISCELLANEOUS['SHELL RUNNING'] == True # want the type to be bool, not bool(value) == True		ENV_VARS['SHELL MODE'] = True		client_f('shell-use read', 'COMMAND')		MISCELLANEOUS['SHELL WAIT'] = False		time.sleep(.5)		try:			while True:				cmd = input(' remote shell > ')				if cmd == '':					continue				if cmd == 'clear':					os_utils.clear_stdout()					continue				if cmd == 'exit':					client_f('shell-use write exit', 'COMMAND')					client_f('shell-use kill', 'COMMAND')					client_f('store "SHELL RUNNING" "none"', 'COMMAND')					vprint('Shell terminated.')					run('send-msg Shell terminated.', client_f=client_f, additional_data=additional_data)					break				open('WAIT FLAG.txt', 'w').write('1')				client_f(f'shell-use write {cmd}', 'COMMAND')				client_f(f'shell-use read', 'COMMAND')				# wait for response from 'other'				while int(open('WAIT FLAG.txt', 'r')): # either '0' or '1'					time.sleep(.1)		except KeyboardInterrupt:			print(' Exiting Shell (KeyboardInterrupt)')		MISCELLANEOUS['SHELL WAIT'] = False		ENV_VARS['SHELL MODE'] = False	elif command[0] == 'shell-use':		function_name = command[1]		if len(command) > 2:			args = ' '.join(command[2:])		else:			args = None		assert 'SHELL RUNNING' in list(MISCELLANEOUS.keys())		assert type(MISCELLANEOUS['SHELL RUNNING']) != bool # using "!= bool" instead of "== utils.Shell" bc of possible version-conflict-errors (python-version/Arachnoid-version)		# run the fonction		print('calling function by name')		if args is None:			result = MISCELLANEOUS['SHELL RUNNING'].__getattribute__(function_name)()		else:			result = MISCELLANEOUS['SHELL RUNNING'].__getattribute__(function_name)(args)		# if there is a result, send it back as a message and stop the waiting of 'other' for thi message with "store"		print(f'I am called with result {result}')		if result is not None:			client_f(f'\n{result}', 'MESSAGE')			client_f('_cmdrun echo 0>"OK FLAG.txt"', 'COMMAND')			print('sent some data :-)')	elif command[0] == 'man':		command_name = '-'.join(command[1:])		found = False		for name, category in list(command_dict.items()):			for c_name, (usage,description) in list(category.items()):				if c_name == command_name:					print(f'  Command: {c_name}')					usage = usage.replace('\t', '').replace('v1', '')					print(f'  Usage: {usage}')					print(' ' + '\n   '.join(description.split('\n')))					found = True					break			if found:				break		if not found:			print(f'Command "{command_name}" not found!')	elif command[0] == 'map-local-network': #! NOT TESTED YET		iface = command[1]		lines = map_local_network(iface)		MISCELLANEOUS['LAST LOCAL NETWORK MAP'] = lines	elif command[0] == 'store':		_, key, _, value, _ = ' '.join(command[1:]).split('"')		if key in list(MISCELLANEOUS.keys()):			vprint('Overwriting old value: {}'.format(MISCELLANEOUS[key]))		if value in ['true', 'True', 'TRUE']: value = True		elif value in ['false', 'False', 'FALSE']: value = False		elif value in ['none', 'None', 'NONE']: value = None		MISCELLANEOUS[key] = value	elif command[0] == 'miscellaneous':		key = ' '.join(command[1:])		assert key in list(MISCELLANEOUS.keys())		print('  Value: "{}" Key: "{}"'.format(key, MISCELLANEOUS[key]))	elif command[0] == 'last-exc':		print(' 🔬 Last Exception:')		if ENV_VARS['LAST EXC']:			for line in ENV_VARS['LAST EXC'].split('\n'):				print('   ' + line)			ENV_VARS['LAST EXC'] = None		else:			print('  Looks like there was no (python) exception since your last "last-exc"...')	elif command[0] == 'reset-file':		# backup file in case...		path = open(os.path.join(ENV_VARS['ROOT DIR'], '__backup_file.path'), 'r').read()		copy_file(os.path.join(ENV_VARS['ROOT DIR'], '__backup_file.file'), path)		vprint('File reset done.')	elif command[0] == 'list-env-vars':		print('  Environment Variables:')		for key, value in list(ENV_VARS.items()):			print('   {} : {}'.format(key, value))	elif command[0] == 'set':		_, key, _, value, _ = ' '.join(command).split('"')		try:			ENV_VARS[key] = int(value)		except:			ENV_VARS[key] = value	elif command[0] == 'get':		key = ' '.join(command[1:])		if key in ENV_VARS.keys():			value = ENV_VARS[key]			print(' Value of "{}": {}'.format(key, value))		else:			raise KeyError('"{}" is not a key of ENV_VARS. To get a list of the keys, type "list-env-vars"'.format(key))	elif command[0] == 'send-msg':		msg = ' '.join(command[1:])		client_f(msg, 'MESSAGE')	elif command[0] == 'send-raw':		msg = ' '.join(command[1:])		client_f(msg, '')	elif command[0] == 'send-command-from-dict':		key = command[1]		index = int(command[2])		old_command = COMMAND_DICT[key][index-1] # index-1 bc the last command is 'send-command-from-dict' (this one, added just before)		print('old command', old_command)		return		client_f(old_command, 'COMMAND')	elif command[0] == 'resend-last':		additional_data['sub-command'] = True		run('send-command-from-dict raw-run -1', client_f, additional_data=additional_data)	elif command[0] == 'corrupt-command':		raise_error(NotImplementedError, 'corrupt-command has not been implemented.\n Thinking about some bit-concatenation right now?')	elif command[0] == 'stop-all':		global client_stop_function		client_stop_function()	elif command[0] == 'ls':		# if only: ls		if len(command) == 1:			path_list = os.listdir()		else: # else, apply unix-like filter			path_list = glob(' '.join(command[1:]))		# output the files, if there are any		if path_list:			print(' - ' + '\n - '.join(path_list))		else:			print(' nothing here...')	elif command[0] == 'cd':		if len(command) == 1:			path = ENV_VARS['ROOT DIR']		else:			path = ' '.join(command[1:])			path = path.replace('~', ENV_VARS['ROOT DIR'])		if os.path.isdir(path):			os.chdir(path)		else:			raise_error(FileNotFoundError, 'Directory does not exist.')	elif command[0] == 'run':		command = ' '.join(command[1:])		client_f(command, 'COMMAND')	elif command[0] == 'open-tab':		url = ' '.join(command[1:])		os_utils.open_url(url)	elif command[0] == 'sync-chrome': # sync own chrome tabs to other		output = os.popen('brotab list').read()		l = list(filter(None, output.split('\n')))		l = [s.split('\t')[-1] for s in l]		for url in l:			client_f('open-tab {}'.format(url), 'COMMAND')	elif command[0] == 'verb':		if len(command) == 1:			print('Verbose Val: {}'.format(ENV_VARS['VERBOSE']))		else:			ENV_VARS['VERBOSE'] = int(command[1])			print('Set verbose to {}'.format(ENV_VARS['VERBOSE'])) # print anyway			if ENV_VARS['SHELL VERSION'] == 2:				additional_data['inter'].VERBOSE = ENV_VARS['VERBOSE']				if 'arachnoid' in list(additional_data.keys()):					additional_data['arachnoid'].verbose = ENV_VARS['VERBOSE']	elif command[0] == 'ping':		client_f('ping ?', 'MESSAGE')		ENV_VARS['PING TIME'] = time.perf_counter()		client_f('_ping-resp', 'COMMAND')	elif command[0] == '_ping-resp':		vprint('ping received')		client_f('ping received', 'MESSAGE')	elif command[0] == 'clear':		os_utils.clear_stdout()		print('PID: {}'.format(os.getpid()))	elif command[0] == 'shutdown':		client_f('_shutdown-self', 'COMMAND')		time.sleep(1)		os_utils.kill_pid(os.getpid())	elif command[0] == '_shutdown-self':		os_utils.kill_pid(os.getpid())		sys.exit('Shutdown.')	elif command[0] == 'sync':		for file in ENV_VARS['CORE FILES']:			additional_data['sub-command'] = True			run('sendfile {}'.format(file), client_f=client_f, additional_data=additional_data)			time.sleep(ENV_VARS['DF WAIT TIME']/1000)	elif command[0] == 'synci':		additional_data['sub-command'] = True		run('sendfile interpreter.py', client_f=client_f, additional_data=additional_data)		time.sleep(1)		run('restart', client_f=client_f, additional_data=additional_data)	elif command[0] == 'sync+': # sync + restart		additional_data['sub-command'] = True		run('sync', client_f=client_f, additional_data=additional_data)		run('restart', client_f=client_f, additional_data=additional_data)	elif command[0] == 'restart':		client_f('restart', 'COMMAND')		if ENV_VARS['SHELL VERSION'] == 1:			if sys.argv[-1] == 'shell':				os.system('echo Restarting & python3 interpreter.py shell')			else:				os.system('echo Restarting & python3 interpreter.py')			sys.exit()		elif ENV_VARS['SHELL VERSION'] == 2:			os.system('echo Restarting Shell v2 & python3 "custom shell client.py"')			os_utils.kill_pid(os.getpid())			sys.exit()		else:			raise_error(ValueError, 'Unkown Shell Version: {}'.format(ENV_VARS['SHELL VERSION']))	elif command[0] == 'cmd':		cmd = ' '.join(command[1:])		# removed the cd os.getcwd() bc of OS DIFF		if ENV_VARS['OS DIFF']:			client_f('_cmdrun {}'.format(cmd), 'COMMAND')		else:			client_f('_cmdrun cd {} &{} {}'.format(os.getcwd(), '&' if os_utils.os_name == 'Linux' else '', cmd), 'COMMAND')	elif command[0] == '_cmdrun':		#proc = subprocess.Popen(command[1:], stdout=subprocess.PIPE, shell=True)		#output = proc.communicate()		output = subprocess.getoutput(' '.join(command[1:]))		vprint('output:\n{}\n'.format(output))		client_f(output, 'MESSAGE')	elif command[0] == '_writefile':		'''		write a file, assuming it is smaller than 5 kb		'''		command = ' '.join(command[1:])		command = command.replace('\\', '\\\\')		try:			file_data = json.loads(command)		except Exception as e:			print('JSON Exception: {}'.format(e))			print('command:', command)			return		transaction_id	=	file_data['transaction id']		index			=	file_data['index']		path 			=	file_data['path'].replace('\\\\', '\\')		opening_mode	=	file_data['opening mode'] # it is assumed there will never be any backslash "\" in the opening mode.		b64file_content =	file_data['content'][2:-1] # removing "b'" and "'" (from "b'these are bytes'")		file_content 	=	base64.b64decode(b64file_content)		file_has_ended	=	bool(int(file_data['end'])) # 0 or 1		os_diff			=	file_data['os diff'] == '1'		if os_diff:			vprint('Changing path to current due to os difference')			path = os.path.join(ENV_VARS['ROOT DIR'], os.path.basename(path))		if index == '0':			if os.path.isfile(path):				# backup file in case...				copy_file(path, os.path.join(ENV_VARS['ROOT DIR'], '__backup_file.file'))				open(os.path.join(ENV_VARS['ROOT DIR'], '__backup_file.path'), 'w').write(path)		if transaction_id not in list(COMMAND_DICT['writefile-hist'].keys()):			COMMAND_DICT['writefile-hist'][transaction_id] = {}			vprint('Writing file with id: {}'.format(transaction_id))		COMMAND_DICT['writefile-hist'][transaction_id][index] = (b64file_content[:25], b64file_content[-25:]) # index is a str, key to a dict.		file = open(path, opening_mode)		file.write(file_content)		file.close()		if file_has_ended:			vprint('Wrote file with id: {}'.format(transaction_id))			client_f('file (transaction id: {}) written.'.format(transaction_id), 'MESSAGE')		return file_has_ended	elif command[0] == 'sendfile':		'''		send a ~large~ file (5 kb +)		'''		path = ' '.join(command[1:])		if ENV_VARS['OS DIFF']:			vprint('Path to abspath not done bc of OS DIFF')		else:			if os_utils.is_win:				if path[1] != ':': # not a absolute windows path					path = os.path.join(os.getcwd(), path)			path = os.path.abspath(path)		if not os.path.isfile(path):			raise_error(FileNotFoundError, 'File not found: {}'.format(path))		transaction_id = ''.join([choice(alphabet) for _ in range(10)])		file_content = open(path, 'rb').read()		file_buffer_list = []		additional_data_length = 57 + len(path.encode('utf8')) + 1 + 256		file_size = len(file_content)		b64_file_size = 4 * file_size / 3 + (4 - (file_size % 4))		b64_file_buffer_size = (ENV_VARS['MAX BUFFER SIZE'] - additional_data_length)		file_buffer_size = int(file_size / (b64_file_size / b64_file_buffer_size))		for buffer_start_index in range(0, file_size, file_buffer_size):			encoded_b64_data = base64.b64encode(file_content[buffer_start_index : buffer_start_index + file_buffer_size])			assert len(encoded_b64_data) < ENV_VARS['MAX BUFFER SIZE'] + additional_data_length			file_buffer_list.append(encoded_b64_data)		last_index = len(file_buffer_list) - 1 # for "end" key in json		for index, file_buffer in enumerate(file_buffer_list):			if index > 0:				time.sleep(ENV_VARS['DF WAIT TIME'] / 1000)			sub_command = r'_writefile {"transaction id": "%s", "index": "%s", "path": "%s", "opening mode": "%s", "content": "%s", "end": "%s", "os diff": "%s"}' % (								transaction_id,								str(index),								path,								'wb' if index == 0 else 'ab',								file_buffer,								'1' if index == last_index else '0',								'1' if ENV_VARS['OS DIFF'] else '0'				)			vprint('path', path)			vprint('size of sub_command: {}'.format(len(sub_command)))			client_f(sub_command, 'COMMAND')		if index > 10:			print('Sent (big?) file {}'.format(path)) # print anyway	elif command[0] == 'sendfiles':		s = ' '.join(command[1:])		if not '"' in s:			path_list = glob(s)		else:			path_list = paths_from_string(s + ' ') # need the ' ' for list[i:j+1 <- the "+1" can go outside the bounds ;-) ]		additional_data['sub-command'] = True		for path in path_list:			run('sendfile {}'.format(path), client_f=client_f, additional_data=additional_data)			time.sleep(ENV_VARS['DF WAIT TIME']/1000)	elif command[0] == 'getfile':		path = ' '.join(command[1:])		'''		path = os.path.abspath(path)		if ENV_VARS['OS DIFF']:			filename = os.path.basename(path)			dirpath = os_utils.complex_path(ENV_VARS['ROOT DIR'], os.path.dirname(path))			path = os.path.join(dirpath, filename)		'''		client_f('sendfile {}'.format(path), 'COMMAND')	elif command[0] == 'getfiles':		s = ' '.join(command[1:])		path_list = paths_from_string(s)		vprint('l', path_list)		additional_data['sub-command'] = True		for path in path_list:			run('getfile {}'.format(path), client_f=client_f, additional_data=additional_data)			time.sleep(ENV_VARS['DF WAIT TIME']/1000)	else:		COMMAND_DICT['raw-run'].pop(-1)		raise_error(print, 'ERROR: Command {} not found.'.format(command[0]), do_raise=False)	# POST-COMMAND	if TEMP_DIR:		os.chdir(TEMP_DIR)def format_string_buffer(s):	replacements = {					'\n': '\\n',					'\\': '\\\\',					'\'': '\\\'',					'\a': '\\a',					'\b': '\\b',					'\f': '\\f',					'\n': '\\n',					'\r': '\\r',					'\t': '\\t',					'\v': '\\v'				   }	for key, item in list(replacements.items()):		s = s.replace(key, item)	return sdef format_buffer(buffer_):	replacements = {					b'\n': b'\\n',					b'\\': b'\\\\',					b'\'': b'\\\'',					b'\a': b'\\a',					b'\b': b'\\b',					b'\f': b'\\f',					b'\n': b'\\n',					b'\r': b'\\r',					b'\t': b'\\t',					b'\v': b'\\v'				   }	for key, item in list(replacements.items()):		buffer_ = buffer_.replace(key, item)	return buffer_def format_command(command):	command = ' '.join(filter(None, command.split(' '))) # remove unneeded spaces	return commanddef handler(content, client_f, ignores=[], additional_data={'sub-command': False}):	global ENV_VARS	if ENV_VARS['INTERPRETER VERSION'] == 1:		content_list = list(filter(None, content.split('<<RECV>>')))		content_list = list(map(lambda c: c[:-1] if c[-1] == '\n' else c, content_list))	else:		content_list = [content]	for msg in content_list:		if ENV_VARS['INTERPRETER VERSION'] == 1:			msg = msg[msg.index(': ') + 2:]		tag = msg[1:-1].split(' ')[0]		if tag in ('EXIT', 'STOP'):			break		elif tag == 'COMMAND':			command = ' '.join(msg[1:-1].split(' ')[1:])			if command.split(' ')[0] in ignores:				vprint('ignored command: {}'.format(command.split(' ')[0]))				return			try:				run(command, client_f=client_f, additional_data=additional_data)			except Exception as e:				exc_file = os.path.join(ENV_VARS['ROOT DIR'],'__temp.exc')				traceback.print_exc(file=open(exc_file, 'w'))				ENV_VARS['LAST EXC'] = open(exc_file, 'r').read()				os.remove(exc_file)				print('    Task failed. For more details, type "last-exc":')		elif tag == 'MESSAGE':			text = ' '.join(msg[1:-1].split(' ')[1:])			if text == 'ping received' and ENV_VARS['PING TIME'] is not None:				ping_time = time.perf_counter() - ENV_VARS['PING TIME']				ping_time *= 1000				print(f'\nping time: {ping_time:.1f} ms', end='')				ENV_VARS['PING TIME'] = None			elif ENV_VARS['SHELL MODE']:				print(text, end='')			else:				print('\nmessage: {}'.format(text))		elif tag != '><':			raise_error(print, 'ERROR: unkown tag "{}"'.format(tag), do_raise=False)		# else: pass # in case tag == '><'def interpreter(file_path=FILE_IN_PATH, announce=True, ignores=[]):	global ENV_VARS	ENV_VARS['INTERPRETER VERSION'] = 1	ENV_VARS['SHELL VERSION'] = 1	file = open(file_path, 'r')	content = file.read()	content = ''	if announce: vprint('Interpreter: Loop started')	while content != '<STOP>':		if content:			handler(content, send_out, ignores=ignores)		content = file.read()	sys.exit('received <STOP> in interpreter')def interpreter2(server, additional_data, announce=True, ignores=[]):	global ENV_VARS	ENV_VARS['INTERPRETER VERSION'] = 2	ENV_VARS['SHELL VERSION'] = 2	# OS DIFF SET BY SHELL	def custom_send_out(msg, tag):		if tag:			s = '<{} {}>'.format(tag, msg)		else:			s = msg		s = s.encode('utf8')		if tag == 'COMMAND':			COMMAND_DICT['raw-out'].append(msg)		server.out_tasks.append(s)	if announce: vprint('Interpreter: Loop started')	content = ''	while content != '<STOP>':		if server.in_tasks:			content = server.in_tasks.pop(0)			try:				content = content.decode('utf8')			except Exception as e:				print('\n[ERROR:Interpreter2:decode-content] could not decode content: {}'.format(content))				custom_send_out('Could not decode some data. Something went really wrong. Please try to revert your action.', 'MESSAGE')				continue			if content.startswith('$'):				print(' 🐝 Executing command directly on the system:')				os.system(content[1:])				continue			if content:				handler(content, custom_send_out, ignores=ignores, additional_data=additional_data)	sys.exit('received <STOP> in interpreter v2')def paths_from_string(s):	num_paths = s.count('"')	assert num_paths % 2 == 0 # there are an even number of '"' signs	path_list = []	for i in range(num_paths//2):		index1 = s.index('"')		index2 = s.index('"', index1+1)		path_list.append(s[index1+1:index2])		s = s[index2+1:]	return path_listdef message_printer(file_path=FILE_IN_PATH):	global ENV_VARS	file_handler = open(file_path)	while ENV_VARS['IN SHELL']:		content = file_handler.read()		if content:			if '<MESSAGE' in content:				msg = content[content.index('<MESSAGE')+9:-1]				print('MSG:\n{}'.format(msg))def shell2(client, inter): # client ", " arachnoid.Spider, inter ", " interpreter.py (module)	global ENV_VARS	global COMMAND_DICT	ENV_VARS['IN SHELL'] = True	ENV_VARS['SHELL VERSION'] = 2	ENV_VARS['OS DIFF'] = client.os_diff	def custom_send_out(msg, tag):		if tag:			s = '<{} {}>'.format(tag, msg)		else:			s = msg		s = s.encode('utf8')		if tag == 'COMMAND':			COMMAND_DICT['raw-out'].append(msg)		client.out_tasks.append(s)	if client._connected:		print('Spider 🕷️ Connected.')	if ENV_VARS['OS DIFF']:		vprint('Setting up OS DIFF of server interpreter')		custom_send_out('set "OS DIFF" "1"', 'COMMAND')	command = ''	while command != 'exit':		try:			raw_command = input(' 🦋 ' + os.getcwd() + ' # ')			command = format_command(raw_command)		except KeyboardInterrupt:			print('^C')			continue		except Exception as e:			print('ERROR (during command input): {}'.format(e))		if command:			if command.startswith('$'):				print(' 🐝 Executing command directly on the system:')				os.system(command[1:])				print()				continue			try:				run(command, additional_data={'inter': inter, 'arachnoid': client}, client_f=custom_send_out)				time.sleep(.1)			except Exception as e:				raise_error(lambda s: print('ERROR: ' + s), str(e), do_raise=False)				#traceback.print_exc()				exc_file = os.path.join(ENV_VARS['ROOT DIR'],'__temp.exc')				traceback.print_exc(file=open(exc_file, 'w'))				ENV_VARS['LAST EXC'] = open(exc_file, 'r').read()				os.remove(exc_file)				#print('    Task failed. For more details, type "last-exc":')	ENV_VARS['IN SHELL'] = False	client.close()def raise_error(error_type, error_message, do_raise=True):	if do_raise:		raise error_type(' 🔬 ' + error_message)	else:		print(' 🔬 ', end='')		error_type(error_message)if __name__ == '__main__':	arg = sys.argv[-1]	if arg == 'shell':		shell()	else:		if arg.startswith('verb'):			ENV_VARS['VERBOSE'] = int(arg[-1])			print('Set Verbose to : {}'.format(ENV_VARS['VERBOSE']))		interpreter()#???