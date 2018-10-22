from modules.Prototype import *
import datetime

def getColumnHeader():
    return {
        "Prefetch": ["Timeline", "File Name", "Executable Name", "Action", ""],			# 4 columns
        # └ Detail exists
        "EventLog": ["Logged Time", "Provider Name", "Event ID", "Level", "Data"],	# 5 columns
        # └ Detail exists (XML)
        "History": ["Accessed Time", "URL", "Modified Time", "", ""],					# 3 columns
        # └ Detail exists (not response header)
        "Cache": ["Accessed Time", "URL", "File Name", "Size", "Created Time"],			# 5 columns
        # └ Response Header exists.
        "Report.wer": ["Modified Time", "Path", "Created Time", "", ""],                # 3 columns
    }

def getPrototype(env, timeline=None):
    prefetchList= ["IEXPLORE.EXE", "WERFAULT.EXE"]
    reportArchive = "AppCrash_IEXPLORE.EXE"
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
            "System.evtx": {
                'eid': ['7036'],
                'providerName': ['Service Control Manager']
            },
        },
        {
            "Application.evtx": {
                'eid': ['1000'],
                'providerName': ['Application Error']
            }
        },
        {
            "Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx": {
                'eid': ['1001'],
                'providerName': ['Microsoft-Windows-Fault-Tolerant-Heap']
            }
        },
    ]
    limitedTime = [0, 0, 0]
    prototype = []
    if env == "Windows7":
        prototype = getWebArtifactItems(env)
        print("Web Artifact: {}".format(len(prototype)))
        others = getEventLogItemsForWin7(evtxLogFor7[0])
        prototype = prototype + others if others else prototype
        if prototype:
            limitedTime[0] = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
        elif others:
            limitedTime[0] = datetime.datetime.strptime(others[0][1], "%Y-%m-%d %H:%M:%S.%f")
        others = getEventLogItemsForWin7(evtxLogFor7[1], "IEXPLORE.EXE", limitedTime[0])
        prototype = prototype + others if others else prototype
        others = getEventLogItemsForWin7(evtxLogFor7[2], limitedTime[0])
        prototype = prototype + others if others else prototype
        others = getEventLogItemsForWin7(evtxLogFor7[3], limitedTime[0])
        prototype = prototype + others if others else prototype
    elif env == "Windows10":
        prototype = getWebArtifactItems(env)
        print("Web Artifact: {}".format(len(prototype)))
        others = getEventLogItemsForWin10(evtxLogFor10[0])
        prototype = prototype + others if others else prototype
        if prototype:
            limitedTime[0] = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
        elif others:
            limitedTime[0] = datetime.datetime.strptime(others[0][1], "%Y-%m-%d %H:%M:%S.%f")
        others = getEventLogItemsForWin10(evtxLogFor10[1], "IEXPLORE.EXE", limitedTime[0])
        prototype = prototype + others if others else prototype
        others = getEventLogItemsForWin10(evtxLogFor10[2], limitedTime[0])
        prototype = prototype + others if others else prototype
    others = getReportWER(env, "AppCrash_IEXPLORE.EXE")
    prototype = prototype + others if others else prototype
    prefetchList = prefetchList + ["CMD.EXE", "POWERSHELL.EXE", "RUNDLL32.EXE"]
    others = getPrefetchItems(prefetchList, limitedTime)
    prototype = prototype + others
    print("총 개수: {}".format(len(prototype)))

    from operator import itemgetter
    prototype.sort(key=itemgetter(1))
    return prototype

    '''
    1. [빨] 웹 히스토리: 끝에 문서형 확장자가 없을 경우 단순 접근 (시작점)
    2. [빨] 웹 캐시: html, js 만 해당되는 경우
    3. [빨] IE 프리패치: 생성만 (단, dll 검사해서 vbscript / jscript 로드 한 것만)
    4. [주] System.evtx EID 7036, 첫번째 로그의 시간을 저장한다.
    5. [주] Application.evtx EID 1000. (1번 저장 시간 이전은 제외)
    6. [노] WER-Diag%4Operational.evtx EID 2 (1번 저장 시간 이전은 제외) -- win7만 
    7. [노] WERFAULT 프리패치: 생성, 실행 모두
    8. [노] Report.wer: IE것만
    9. [초] Fault...heap.evtx EID 1001
    10. [파] IE 프리패치: 실행만
    11. [남] 웹 캐시/히스토리: 확장자 검사 (dll, doc, docx, hta, xls, woff, pdf)
    12. [보] 레지스트리 검사 필요
    13. [보] 이전과정에서 EXE 모두 추출 후 프리패치 파싱
    '''
