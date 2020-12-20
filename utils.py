import glob
from time import ctime
from hashlib import md5
from os import listdir, chdir, getcwd
from os.path import join, isfile, isdir, getsize as filesize
from os.path import getctime, getmtime
import pickle
import subprocess

calc_file_hash = lambda file: md5(open(file, 'rb').read()).hexdigest()
get_file_info = lambda file, calc_hash: (filesize(file), ctime(getctime(file)), ctime(getmtime(file)), calc_file_hash(file) if calc_hash else 0)

def compare_file(file1, file2, check_hash=False):
	'''Return True if the two files are the same. False if they have differences.
	Comparaisons (in order):
	- size
	- created time
	- last modified time
	- md5 hash (optional)
	'''

	# compare sizes
	if filesize(file1) != filesize(file2):
		return False

	# compare created time
	if ctime(getctime(file1)) != ctime(getctime(file2)):
		return False

	# comapre last modified time
	if ctime(getmtime(file1)) != ctime(getmtime(file2)):
		return False

	if check_hash:
		# compare hashes
		hash1 = calc_file_hash(fiel1)
		hash2 = calc_file_hash(file2)
		return hash1 == hash2
	else:
		return True

def hashify_dir(dir_path, calc_hash=False):
	root = getcwd()
	chdir(dir_path)
	for obj in listdir(dir_path):
		obj = join(dir_path, obj)
		if isfile(obj):
			yield (('f', obj), get_file_info(obj, calc_hash))
		elif isdir(obj):
			yield (('d', obj.replace('\\', '/')), dict(hashify_dir(obj, calc_hash)))
		else:
			print(f'WARNING: Ignoring object {obj} which is neither a file, not a directory')
	chdir(root)

def save_obj(obj):
	filepath = join(getcwd(), '__temp.dirhash')
	fobj = open(filepath, 'wb')
	pickle.dump(obj, fobj)
	return filepath

def load_obj(filepath):
	fobj = open(filepath, 'rb')
	return pickle.load(fobj)

def serialize_data(data):
	return pickle._dumps(data)

def deserialize_data(data):
	return pickle._loads(data)

def get_object_from_dict(obj, key_list):
	for key in key_list:
		obj = obj[key]
	return obj

def compare_dir_hashes(dh1, dh2, dir1l, dir2l):
	'''Changes to apply to dir 2, so that it is synced with dir 1
	'''
	l1 = list(dh1.items())
	l2 = list(dh2.items())
	l1.sort(key=lambda arg: arg[0][1][dir1l:])
	l2.sort(key=lambda arg: arg[0][1][dir2l:])
	length1, length2 = len(l1), len(l2)
	length = min([len(l1), len(l2)])
	i1, i2 = 0, 0
	change_list = []
	while i1 < length1 and i2 < length2:
		# extract data
		key1, obj_data1 = l1[i1]
		key2, obj_data2 = l2[i2]
		(obj_type1, obj_path1) = key1
		(obj_type2, obj_path2) = key2

		# are the names similar (file is there)
		if obj_path1[dir1l:] == obj_path2[dir2l:] and obj_type1 == obj_type2: # folder-name == file-name ?
			if obj_type1 == 'f':
				if file_data1 != file_data2:
					change_list.append(('update', obj_type1, obj_path1, obj_path2))
			elif obj_type1 == 'd':
				change_list.extend(compare_dir_hashes(dh1[key1], dh2[key2], dir1l, dir2l))
			else:
				raise NotImplementedError(f'Unsupported object type {obj_type1} or {obj_type2}')
		else:
			if obj_path1[dir1l:] <= obj_path2[dir2l:]: # <= bc if fodler has exactly same name as file ?
				change_list.append(('missing', obj_type1, obj_path1))
				i1 += 1
				continue
			else:
				change_list.append('remove', obj_type2, obj_path2)
				i2 += 1
				continue

		i1 += 1
		i2 += 1

	if i2 < length2:
		change_list.extend([('remove', obj_type, obj_path) for (obj_type, obj_path),_ in l2[i2:]])

	return change_list

def sync_dir(change_list):
	for change in change_list:
		print(change)
		apply_change(change)

def apply_change(change):
	# replace dir-prefix (other) by local prefix (e.g. /home/user/folder -> C:\Users\User\folder)
	pass

class Shell:
	'''
	'''

	def __init__(self, executable):
		self.executable = executable
		self.process = None
		self.terminate_timeout=0.2

	def start(self):
		self.process = subprocess.Popen(
				self.executable,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)

	def read(self):
		return self.process.stdout.readline().decode('utf-8').strip()

	def write(self, msg):
		self.process.stdin.write(f'{msg.strip()}\n'.encode('utf-8'))
		self.process.stdin.flush()

	def terminate(self):
		self.process.stdin.close()
		self.process.terminate()
		self.process.wait(timeout=self.terminate_timeout)

	def kill(self):
		self.process.kill()

