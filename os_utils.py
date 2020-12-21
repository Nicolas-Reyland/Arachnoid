# OS-related functions
import webbrowser
import platform
import os

'''
functions which are os-dependant
Supported oses re Windows and Linux.

Looking forward to supporting Darwin (MacOS).
'''

os_name = platform.uname()[0] # 'Windows' or 'Linux'
if os_name not in ['Windows', 'Linux']:
	raise Warning(f'UNRECOGNIZED OS "{os_}". Some functions will break. Proceeed with caution')

is_win = os_name == 'Windows'

if is_win:
	from wexpect import spawn
else:
	from pexpect import spawnu as spawn

def clear_stdout():
	if is_win:
		os.system('cls')
	else:
		os.system('clear')

def open_url(url):
	if os:
		if os.path.isfile('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'):
			webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open(url,new=2)
		elif os.path.isfile('C:/Program Files/Google/Chrome/Application/chrome.exe'):
			webbrowser.get('C:/Program Files/Google/Chrome/Application/chrome.exe %s').open(url,new=2)
		else:
			# print('chrome was not found')
			webbrowser.open_new_tab(url)
	else:
		webbrowser.open_new_tab(url)

def kill_pid(pid):
	if is_win:
		cmd = f'taskkill /f /im {pid}'
	else:
		cmd = f'kill {pid}'
	os.system(cmd)

def get_shell_executable_name():
	if is_win:
		return 'cmd.exe'
	else:
		return '/bin/bash'

def complex_path(root_dir, target_dir):
	'''For this function to be called, OS DIFF must be true
	'''
	# check if complete path was given
	if os.path.isdir(target_dir):
		return target_dir
	# assert there are no bizarre things in file/folder names
	if is_win: assert not '/' in target_dir # no forward slash in file names/folder names
	else: assert not '\\' in root_dir # no backslash in file names/folder names

	# every dir-separator is a "/"
	if is_win: root_dir = root_dir.replace('\\', '/')
	else: target_dir = target_dir.replace('\\', '/')

	# add '/' at the end of both, if absent. so we can check on equality
	if not root_dir.endswith('/'): root_dir += '/'
	if not target_dir.endswith('/'): target_dir += '/'

	# check if euqual, containing, work-with-".."
	if target_dir == root_dir:
		return target_dir
	#
	if target_dir in root_dir:
		assert root_dir.startswith(target_dir)
		return ''
	# more complex path
	# C:\Users\Manon\Documents\Arachnoid
	# /home/ilu_vatar_/python/networking/Arachnoid
	# ../../web/
	# __pycache__/
	os.path.join(root_dir, target_dir)
