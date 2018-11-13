import sys
import struct
import zipfile
import argparse
import binascii
import datetime
import codecs
import xml.etree.cElementTree as et
from io import StringIO as sio
from os import path
from csv import writer

# Values used by Windows 6.1 (Win7 and Server 2008 R2)
CACHE_MAGIC_NT6_1 = 0xbadc0fee
CACHE_HEADER_SIZE_NT6_1 = 0x80
NT6_1_ENTRY_SIZE32 = 0x20
NT6_1_ENTRY_SIZE64 = 0x30
CSRSS_FLAG = 0x2

# Values used by Windows 10
WIN10_STATS_SIZE = 0x30
WIN10_CREATORS_STATS_SIZE = 0x34
WIN10_MAGIC = '10ts'
CACHE_HEADER_SIZE_NT6_4 = 0x30
CACHE_MAGIC_NT6_4 = 0x30

bad_entry_data = 'N/A'
g_verbose = False
g_usebom = False
output_header  = ["Last Modified", "Last Update", "Path", "File Size", "Exec Flag"]

# Date Formats
DATE_MDY = "%m/%d/%y %H:%M:%S"
DATE_ISO = "%Y-%m-%d %H:%M:%S.%f"
g_timeformat = DATE_ISO

g_timeline = None
g_prefetchList = []
grayHead = ["Registry", 0]
purpleHead = ["Registry", 7]
# Shim Cache format used by Windows 6.1 (Win7 through Server 2008 R2)
class CacheEntryNt6(object):

	def __init__(self, is32bit, data=None):

		self.is32bit = is32bit
		if data != None:
			self.update(data)

	def update(self, data):
		if self.is32bit:
			entry = struct.unpack('<2H 7L', data)
		else:
			entry = struct.unpack('<2H 4x Q 4L 2Q', data)
		self.wLength = entry[0]
		self.wMaximumLength =  entry[1]
		self.Offset = entry[2]
		self.dwLowDateTime = entry[3]
		self.dwHighDateTime = entry[4]
		self.FileFlags = entry[5]
		self.Flags = entry[6]
		self.BlobSize = entry[7]
		self.BlobOffset = entry[8]

	def size(self):

		if self.is32bit:
			return NT6_1_ENTRY_SIZE32
		else:
			return NT6_1_ENTRY_SIZE64

# Convert FILETIME to datetime.
# Based on http://code.activestate.com/recipes/511425-filetime-to-datetime/
def convert_filetime(dwLowDateTime, dwHighDateTime):
	global g_timeline
	try:
		date = datetime.datetime(1601, 1, 1, 0, 0, 0)
		temp_time = dwHighDateTime
		temp_time <<= 32
		temp_time |= dwLowDateTime
		res = date + datetime.timedelta(microseconds=temp_time/10)
		if g_timeline:
			if res < g_timeline:
				return None
		return res
	except OverflowError as err:
		print("{} in convert_filetime at ShimCacheParse.py".format(err))
		return None

# Return a unique list while preserving ordering.
def unique_list(li):

	ret_list = []
	for entry in li:
		if entry not in ret_list:
			ret_list.append(entry)
	return ret_list

# Write the Log.
def write_it(rows, outfile=None):

	try:
		if not rows:
			print("[-] No data to write...")
			return

		f = open(outfile, 'w')
		if g_usebom:
			f.write(codecs.BOM_UTF8)
		csv_writer = writer(f, delimiter=',')
		csv_writer.writerows(rows)
		f.close()
	except (IOError, UnicodeEncodeError) as err:
		print("[-] Error writing output file: %s" % str(err))
		return

# Read the Shim Cache format, return a list of last modified dates/paths.
def read_cache(cachebin, quiet=False):

	if len(cachebin) < 16:
		# Data size less than minimum header size.
		return None

	try:
		# Get the format type
		magic = struct.unpack("<L", cachebin[:4])[0]
		# This is a Windows 7/2k8-R2 Shim Cache.
		if magic == CACHE_MAGIC_NT6_1:
			test_size = (struct.unpack("<H",
						 cachebin[CACHE_HEADER_SIZE_NT6_1:
						 CACHE_HEADER_SIZE_NT6_1 + 2])[0])
			test_max_size = (struct.unpack("<H", cachebin[CACHE_HEADER_SIZE_NT6_1+2:
							 CACHE_HEADER_SIZE_NT6_1 + 4])[0])
							 
			# Shim Cache types can come in 32-bit or 64-bit formats.
			# We can determine this because 64-bit entries are serialized with
			# u_int64 pointers. This means that in a 64-bit entry, valid
			# UNICODE_STRING sizes are followed by a NULL DWORD. Check for this here.
			if (test_max_size-test_size == 2 and
				struct.unpack("<L", cachebin[CACHE_HEADER_SIZE_NT6_1+4:
				CACHE_HEADER_SIZE_NT6_1 + 8])[0] ) == 0:
				if not quiet:
					print("[+] Found 64bit Windows 7/2k8-R2 Shim Cache data...")
				entry = CacheEntryNt6(False)
				return read_nt6_entries(cachebin, entry)
			else:
				if not quiet:
					print("[+] Found 32bit Windows 7/2k8-R2 Shim Cache data...")
				entry = CacheEntryNt6(True)
				return read_nt6_entries(cachebin, entry)

		# Windows 10 will use a different magic dword, check for it
		elif len(cachebin) > WIN10_STATS_SIZE and cachebin[WIN10_STATS_SIZE:WIN10_STATS_SIZE+4].decode() == WIN10_MAGIC:
			if not quiet:
				print("[+] Found Windows 10 Apphelp Cache data...")
			return read_win10_entries(cachebin, WIN10_MAGIC)

		# Windows 10 Creators Update will use a different STATS_SIZE, account for it
		elif len(cachebin) > WIN10_CREATORS_STATS_SIZE and cachebin[WIN10_CREATORS_STATS_SIZE:WIN10_CREATORS_STATS_SIZE+4].decode() == WIN10_MAGIC:
			if not quiet:
				print("[+] Found Windows 10 Creators Update Apphelp Cache data...")
			return read_win10_entries(cachebin, WIN10_MAGIC, creators_update=True)

		else:
			print("[-] Got an unrecognized magic value of 0x%x... bailing" % magic)
			return None

	except (RuntimeError, TypeError, NameError) as err:
		print("[-] Error reading Shim Cache data: %s" % err)
		return None

# Read Windows 10 Apphelp Cache entry format
def read_win10_entries(bin_data, ver_magic, creators_update=False):
	try:
		offset = 0
		entry_meta_len = 12
		entry_list = []

		# Skip past the stats in the header
		if creators_update:
			cache_data = bin_data[WIN10_CREATORS_STATS_SIZE:]
		else:
			cache_data = bin_data[WIN10_STATS_SIZE:]

		from io import BytesIO
		data = BytesIO(cache_data)
		while data.tell() < len(cache_data):
			header = data.read(entry_meta_len)
			# Read in the entry metadata
			# Note: the crc32 hash is of the cache entry data
			magic, crc32_hash, entry_len = struct.unpack('<4sLL', header)
			magic = magic.decode()

			# Check the magic tag
			if magic != ver_magic:
				raise Exception("Invalid version magic tag found: 0x%x" % struct.unpack("<L", magic)[0])

			entry_data = BytesIO(data.read(entry_len))

			# Read the path length
			head = grayHead
			path_len = struct.unpack('<H', entry_data.read(2))[0]
			if path_len == 0:
				path = 'None'
			else:
				path = entry_data.read(path_len).decode('utf-16le', 'replace')

				global g_prefetchList
				from modules.constant import SYSTEMROOT, LOCALAPPDATA
				if path[-3:].lower() == "exe":
					head = grayHead
				elif SYSTEMROOT.lower() in path.lower() or LOCALAPPDATA in path.lower():
					head = grayHead
				else:
					continue

			# Read the remaining entry data
			low_datetime, high_datetime = struct.unpack('<LL', entry_data.read(8))

			last_mod_date = convert_filetime(low_datetime, high_datetime)
			if not last_mod_date:
				continue
			try:
				last_mod_date = last_mod_date.strftime("%Y-%m-%d %H:%M:%S.%f")
			except ValueError as e:
				continue
				#last_mod_date = bad_entry_data

			row = [head, last_mod_date, path, 'N/A', 'N/A', "AppCompatCache"]

			if row not in entry_list:
				entry_list.append(row)
				if path[-3:].lower() == "exe":
					added = path.rsplit("\\", 1)[-1].upper()
					g_prefetchList.append(added)

		return entry_list
	except (RuntimeError, ValueError, NameError) as err:
		print('[-] Error reading Shim Cache data: %s...' % err)
		return None

# Read the Shim Cache Windows 7/2k8-R2 entry format,
# return a list of last modifed dates/paths.
def read_nt6_entries(bin_data, entry):

	try:
		entry_list = []
		exec_flag = ""
		entry_size = entry.size()
		num_entries = struct.unpack('<L', bin_data[4:8])[0]
		
		if num_entries == 0:
			return None
		# Walk each entry in the data structure.
		for offset in range(CACHE_HEADER_SIZE_NT6_1,
							 num_entries*entry_size + CACHE_HEADER_SIZE_NT6_1,
							 entry_size):

			entry.update(bin_data[offset:offset+entry_size])
			last_mod_date = convert_filetime(entry.dwLowDateTime,
											 entry.dwHighDateTime)
			if not last_mod_date:
				continue
			try:
				last_mod_date = last_mod_date.strftime("%Y-%m-%d %H:%M:%S.%f")
			except ValueError as e:
				print(e)
			path = (bin_data.decode("unicode-escape")[entry.Offset:entry.Offset +
							 entry.wLength])[8:].replace("\x00", "")
			global g_prefetchList
			from modules.constant import SYSTEMROOT, LOCALAPPDATA
			if path[-3:].lower() == "exe":
				head = grayHead
			elif SYSTEMROOT.lower() in path.lower() or LOCALAPPDATA in path.lower():
				head = grayHead
			else:
				continue

			# Test to see if the file may have been executed.
			if (entry.FileFlags & CSRSS_FLAG):
				exec_flag = 'True'
			else:
				exec_flag = 'False'

			row = [head, last_mod_date, path, 'N/A', exec_flag, "AppCompatCache"]

			if row not in entry_list:
				entry_list.append(row)
				if path[-3:].lower() == "exe":
					added = path.rsplit("\\", 1)[-1].upper()
					g_prefetchList.append(added)
		return entry_list

	except (RuntimeError, ValueError, NameError) as err:
		print('[-] Error reading Shim Cache data: %s...' % err)
		return None

# Get Shim Cache data from a registry hive.
def read_from_hive(hive):
	out_list = []
	tmp_list = []

	# Check for dependencies.
	try:
		import Registry
	except ImportError as e:
		print(e)
		print("[-] Hive parsing requires Registry.py... Didn\'t find it, bailing...")
		sys.exit(2)
	
	try:
		reg = Registry.Registry(hive)
	except Registry.RegistryParse.ParseException as err:
		print("[-] Error parsing %s: %s" % (hive, err))
		sys.exit(1)

	# Partial hive
	partial_hive_path = ('Session Manager', 'AppCompatCache', 'AppCompatibility')
	if reg.root().path() in partial_hive_path:
		if reg.root().path() == 'Session Manager':
			# Only Session Manager
			# For example extracted with: reg save "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" "c:\temp\SessionManager.hve" /y
			print("[+] Partial hive -- 'Session Manager'")
			if reg.root().find_key('AppCompatCache').values():
				print("[+] Partial hive -- 'AppCompatCache' or 'AppCompatibility'")
				keys = reg.root().find_key('AppCompatCache').values()
		else:
			# Partial hive AppCompatCache or AppCompatibility
			# reg save "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache" "c:\temp\appCompatCache.hve" /y
			# reg save "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility" "c:\temp\AppCompatibility.hve" /y
			keys = reg.root().values()
		for k in keys:
			bin_data = str(k.value())
			tmp_list = read_cache(bin_data)

			if tmp_list:
				for row in tmp_list:
					if g_verbose:
						row.append(k.name())
					if row not in out_list:
						out_list.append(row)
	else:
		# Complete hive
		root = reg.root().subkeys()
		for key in root:
			# Check each ControlSet.
			try:
				if 'controlset' in key.name().lower():
					session_man_key = reg.open('%s\Control\Session Manager' % key.name())
					for subkey in session_man_key.subkeys():
						# Read the Shim Cache structure.
						if ('appcompatibility' in subkey.name().lower() or
							'appcompatcache' in subkey.name().lower()):
							bin_data = subkey['AppCompatCache'].value()
							tmp_list = read_cache(bin_data)
							if tmp_list:
								for row in tmp_list:
									if g_verbose:
										row.append(subkey.path())
									if row not in out_list:
										out_list.append(row)

			except Registry.RegistryKeyNotFoundException as e:
				print(e)
				continue

	if len(out_list) == 0:
		return None
	else:
		# Add the header and return the list including duplicates.
		if g_verbose:
			out_list.insert(0, output_header + ['Key Path'])
			return out_list
		else:
		# Only return unique entries.
			out_list = unique_list(out_list)
			out_list.insert(0, output_header)
			return out_list

# Acquire the current system's Shim Cache data.
def get_local_data(prefetchList, timeline=None):
	tmp_list = []
	out_list = []
	global g_verbose
	global g_timeline
	global g_prefetchList
	try:
		import winreg as reg
	except ImportError as e:
		print(e)
		sys.exit(1)
	g_timeline = timeline
	g_prefetchList = prefetchList
	hReg = reg.ConnectRegistry(None, reg.HKEY_LOCAL_MACHINE)
	hSystem = reg.OpenKey(hReg, r'SYSTEM')
	for i in range(1024):
		try:
			control_name = reg.EnumKey(hSystem, i)
			if 'controlset' in control_name.lower():
				hSessionMan = reg.OpenKey(hReg, 'SYSTEM\\%s\\Control\\Session Manager' % control_name)
				for i in range(1024):
					try:
						subkey_name = reg.EnumKey(hSessionMan, i)
						if ('appcompatibility' in subkey_name.lower()
							or 'appcompatcache' in subkey_name.lower()):
							appcompat_key = reg.OpenKey(hSessionMan, subkey_name)
							bin_data = reg.QueryValueEx(appcompat_key, 'AppCompatCache')[0]
							tmp_list = read_cache(bin_data)
							if tmp_list:
								path_name = "Registry Path:\n"
								path_name += 'SYSTEM\\%s\\Control\\Session Manager\\%s' % (control_name, subkey_name)
								for row in tmp_list:
									row.append(path_name)
									if row not in out_list:
										out_list.append(row)
					except EnvironmentError as e:
						print(e)
						break
		except EnvironmentError as e:
			print(e)
			break
	g_timeline = None
	if len(out_list) == 0:
		return None
	else:
		if g_verbose:
			#out_list.insert(0, output_header + ['Key Path'])
			return out_list
		else:
			out_list = unique_list(out_list)
			#out_list.insert(0, output_header)
			return out_list
