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
