import sys
from modules.Prototype import *

def getColumnHeader():
	return {
		"Prefetch": ["Timeline", "File Name", "Executable Name", "Action", ""],					# 4 columns
		# └ Detail exists
		"EventLog": ["Logged Time", "Provider Name", "Event ID", "Level", "Task", "Channel"],	# 5 columns
		# └ Detail exists (XML)
		"History": ["Accessed Time", "URL", "Modified Time", "", ""],							# 3 columns
		# └ Detail exists (not response header)
		"Cache": ["Accessed Time", "URL", "File Name", "Size", "Created Time"],			# 5 columns
		# └ Response Header exists.
	}

def getPrototype(env, timeline=None):
	prefetchList= ["IEXPLORER.EXE", "WERFAULT.EXE", "CMD.EXE", "POWERSHELL.EXE"]
	evtxLogFor7 = {
		"Application.evtx": {
			'eid': ['1000'],
			'providerName': ['Appllication Error']
		},
		"System.evtx": {
			'eid': ['7036'],
			'providerName': ['Service Control Manager']
		},
		"Microsoft-Windows-WER-Diag%4Operational.evtx": {
			'eid': ['2'],
			'providerName': ['Microsoft-Windows-WER-Diag']
		},
		"Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx": {
			'eid': ['1001'],
			'providerName': ['Microsoft-Windows-Fault-Tolerant-Heap']
		}
	}
	evtxLogFor10 = {
		"Application.evtx": {

		},
		"System.evtx": {

		}
	}
	prototype = {}
	prototype["Prefetch"] = getPrefetchItems(prefetchList)
	# if env == "Windows7":
	# 	prototype["EventLog"] = getEventLogItemsForWin7(evtxLogFor7)
	# elif env == "Windows10":
	# 	prototype["EventLog"] = getEventLogItemsForWin10(evtxLogFor10)
	prototype.update(getWebArtifactItems(env))
	# 그 외 Report.wer or JumpList등등
	total = len(prototype["Prefetch"]) + len(prototype["History"]) + len(prototype["Cache"])
	return prototype, total
