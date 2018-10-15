import sys
from datetime import datetime

from modules.Prototype import *

def getColumnHeader():
	return {
		"Prefetch": ["Timeline", "File Name", "Executable Name", "Action", ""],					# 4 columns
		# └ Detail exists
		"EventLog": ["Logged Time", "Provider Name", "Event ID", "Level", "Channel"],	# 5 columns
		# └ Detail exists (XML)
		"History": ["Accessed Time", "URL", "Modified Time", "", ""],							# 3 columns
		# └ Detail exists (not response header)
		"Cache": ["Accessed Time", "URL", "File Name", "Size", "Created Time"],			# 5 columns
		# └ Response Header exists.
	}

def getPrototype(env, timeline=None):
	prefetchList= ["IEXPLORE.EXE", "WERFAULT.EXE"]
	evtxLogFor7 = [
		{
			"System.evtx": {
				'eid': ['7036'],
				'providerName': ['Service Control Manager']
			},
		},
		{
			"Application.evtx": {
				'eid': ['1000'],
				'providerName': ['Appllication Error']
			}
		},
		{
			"Microsoft-Windows-WER-Diag%4Operational.evtx": {
				'eid': ['2'],
				'providerName': ['Microsoft-Windows-WER-Diag']
			}
		},
		{
			"Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx": {
				'eid': ['1001'],
				'providerName': ['Microsoft-Windows-Fault-Tolerant-Heap']
			}
		}
	]
	evtxLogFor10 = [
		{
			"Application.evtx": {

			}
		},
		{
			"System.evtx": {

			}
		}
	]

	prototype = []
	''' (Windows 7)
	각 이벤트 로그 중 없는 경우, 3번 이전이 없다라고 한다면 1번 이전
	1. [빨] System.evtx 이벤트 로그를 보고, 첫번째 로그의 시간을 저장한다.
	2. [빨] Application.evtx 이벤트 로그를 본다. (1번 이전은 제외)
	3. [빨] WERFAULT.evtx 이벤트 로그를 보고, 첫번째 로그의 시간을 저장한다. (1번 이전은 제외)
	4. [빨, 주] 프리패치를 본다.
		ㄴ IE 프리패치 `생성`은 무조건 빨간색 (3번 이전은 제외)
		ㄴ IE 프리패치 `실행` 중 3번 이전은 빨간색, 이후는 주황색
		ㄴ WERFAULT 프리패치는 `생성`, `실행` 모두 주황색
	5. [주] Report.wer를 찾는다. 없으면 패스
	6. [주] Fault...heap.evtx 이벤트 로그를 보고, 첫번째 로그의 시간을 저장한다.
	7. 웹 히스토리(Win10 공통) : 단, 6번 이전은 제외
		ㄴ [노] exe, doc, docx, hta, xls, ppts, pptx, ppsx, pdf 가 끝에 없다면, 단순 접근 (http로 시작)
		ㄴ [파] exe, doc, docx, hta, xls, ppts, pptx, ppsx, pdf 및 download 문자열 포함(?)
			ㄴ exe 확장자를 포함하는 경우 모두 저장
	8. 웹 캐시(Win10 공통) : 단, 6번 이전은 제외
		ㄴ [초] exe, doc, docx, hta, xls, ppts, pptx, ppsx, pdf 확장자를 갖지 않는 파일명
		ㄴ [남] exe, doc, docx, hta, xls, ppts, pptx, ppsx, pdf 확장자를 갖는 파일명 
			ㄴ exe 확장자를 포함하는 경우 모두 저장
	9. [보] 프리패치를 본다. : 단, 6번 이전은 제외
		ㄴ 7, 8에서 저장한 exe를 갖는 파일명 모두 조회
	'''
	limitedTime = [0, 0, 0]
	if env == "Windows7":
		# 1 - 3
		prototype = getEventLogItemsForWin7(evtxLogFor7[0])
		others = getEventLogItemsForWin7(evtxLogFor7[1], limitedTime[0])
		if prototype:
			limitedTime[0] = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
		elif others:
			limitedTime[0] = datetime.datetime.strptime(others[0][1], "%Y-%m-%d %H:%M:%S.%f")
		prototype = prototype + others
		# 근데 아직도 없으면,,? limitedTime
		others = getEventLogItemsForWin7(evtxLogFor7[2], limitedTime[0])
		prototype = prototype + others
		limitedTime[1] = datetime.datetime.strptime(others[0][1], "%Y-%m-%d %H:%M:%S.%f")
		# Report.wer 찾기
		others = getEventLogItemsForWin7(evtxLogFor7[3], limitedTime[0])
		limitedTime[2] = datetime.datetime.strptime(others[0][1], "%Y-%m-%d %H:%M:%S.%f")
		prototype = prototype + others
		others = getWebArtifactItems(env, limitedTime[2])
		prototype = prototype + others[0]
		prefetchList = prefetchList + others[1] # include more behavior
		others = getPrefetchItems(prefetchList, limitedTime)
		prototype = prototype + others
	elif env == "Windows10":
		prefetchList = prefetchList + ["CMD.EXE", "POWERSHELL.EXE"]
		prototype = getPrefetchItems(prefetchList, limitedTime)
		limitedTime[2] = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
		others = getWebArtifactItems(env, limitedTime[2])
		prototype = prototype + others[0]

	from operator import itemgetter
	prototype.sort(key=itemgetter(1))
	return prototype
