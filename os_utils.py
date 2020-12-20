# OS-related functions
import webbrowser
import platform
import os

import threading, time
import _thread

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

def get_shell_executable_name():
	if is_win:
		return 'cmd.exe'
	else:
		return '/bin/bash'

class Ticker:
	'''
	'''

	def __init__(self, interval):
		self.interval = interval
		self.timer = 0
		self.thread = threading.Thread(target=self._run)
		self.should_run = None
		self.sleep_time = min(.1, self.interval / 10)

	def start(self):
		self.should_run = True
		self.thread.start()

	def reset(self):
		self.timer = time.perf_counter()

	def stop(self):
		self.should_run = False
		self.thread.join(timeout=self.interval + .15)

	def _run(self):
		# init timer
		self.timer = time.perf_counter()
		# while the timer has been reset since a period of time < than interval
		while time.perf_counter() - self.timer < self.interval and self.should_run:
			time.sleep(self.sleep_time)

		if self.should_run:
			# raise Exception
			_thread.interrupt_main()
