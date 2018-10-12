import sys
import libs.ParseEvtx.Evtx as evtx
import libs.ParseEvtx.Views as e_views

def evtx_dump(_path, eid):
	with evtx.Evtx(_path) as log:
		print(e_views.XML_HEADER)
		print("<Events>")
		for record in log.records():
			eventLog = record.xml()
			if "{}</EventID>".format(eid) in eventLog:
				print(eventLog)
		print("</Events>")

def evtx_extract_record(_path, recordID):
	# recordID : The record number of the record to extract
	with evtx.Evtx(_path) as log:
		record = log.get_record(recordID)
		if record is None:
			raise RuntimeError("Cannot find the record specified.")
		print(record.xml())

if __name__ == '__main__':
	__path = "C:\Windows\System32\winevt\Logs\System.evtx"
	eid = 7001
	recordID = 20844
	evtx_dump(__path, eid)
	#evtx_extract_record(__path, recordID)