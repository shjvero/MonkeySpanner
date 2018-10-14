import sys
from modules.Prototype import *

def getColumnHeader():
	return {
		"Prefetch": ["Timeline", "File Name", "Action", "File Size", "Executable Name"],		# 5 columns
		"EventLog": ["Logged Time", "Level", "Event ID", "Provider Name", "Task", "Channel"],	# 5 columns
		"History": ["Accessed Time", "URL", "Access Count", "File Name", "Created Time"],		# 5 columns
		"Cache": ["Accessed Time", "File Name", "File Size", "URL", "Access Count", "Created Time"],	# 6 columns
		# └ Response Header exists.
	}

def getPrototype(env, timeline=None):
	# 추가적인 프리패치 (시스템 프로세스 등)
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
	if env == "Windows7":
		prototype["EventLog"] = getEventLogItemsForWin7(evtxLogFor7)
	elif env == "Windows10":
		prototype["EventLog"] = getEventLogItemsForWin10(evtxLogFor10)
	prototype.update(getWebArtifactItems(env))
	# 그 외 Report.wer or JumpList등등

	return prototype
