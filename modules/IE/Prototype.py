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
        "Download": ["Accessed Time", "URL", "File Name", "Size", "Download Path"],      # 5 columns
        # └ Response Header exists.(??)
        "Report.wer": ["Modified Time", "Path", "Created Time", "", ""],                # 3 columns
        # └ Detail exists (wer)
        "Registry": ["Modified Time", "Execution Path", "Size", "Exec Flag", "Registry Key"]       # 4 columns
        # └ Detail exists (path)
    }

def getPrototype(env, timeline=None):
    from operator import itemgetter
    prefetchList= ["IEXPLORE.EXE", "WERFAULT.EXE", "CMD.EXE", "POWERSHELL.EXE", "RUNDLL32.EXE"]
    reportArchive = "AppCrash_IEXPLORE.EXE"
    evtxLogFor7 = [
        {
            "System.evtx": {
                'eid': [206, 7036],
                'providerName': {
                    # '206': 'Microsoft-Windows-Application-Experience'
                    # >> 프로그램 호환성 관리자 서비스에서 2단계 초기화를 수행했습니다. (필요?)
                    '7036': 'Service Control Manager',
                }
            },
        },
        {
            "Application.evtx": {
                'eid': [1000, 1001],
                'providerName': {
                    '1000': 'Application Error',
                    '1001': 'Windows Error Reporting',
                }
            }
        },
        {
            "Microsoft-Windows-WER-Diag%4Operational.evtx": {
                'eid': [2],
                'providerName': {
                    '2': 'Microsoft-Windows-WER-Diag'
                }
            }
        },
        {
            "Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx": {
                'eid': [1001],
                'providerName': {
                    '1001': 'Microsoft-Windows-Fault-Tolerant-Heap',
                }
            }
        }
    ]
    evtxLogFor10 = [
        {
            "Application.evtx": {
                'eid': [1000, 1001],
                'providerName': {
                    '1000': 'Application Error',
                    '1001': 'Windows Error Reporting',
                }
            }
        },
        {
            "Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx": {
                'eid': [1001],
                'providerName': {
                    '1001': 'Microsoft-Windows-Fault-Tolerant-Heap',
                }
            }
        },
    ]
    t_list = []
    from threading import Thread
    limitedTime = None
    result, prototype = getWebArtifactItems(env, prefetchList) # 다운로드된 것만 따로해서 레지스트리에서 검사필요?
    if not result:
        return result, prototype
    if prototype:
        prototype.sort(key=itemgetter(1))
        limitedTime = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
    print("Web Artifact: {}".format(len(prototype)))
    if env == "Windows7":
        t_list.append(Thread(target=getEventLogItemsForWin7, args=(evtxLogFor7[0], prototype, None, limitedTime, )))
        t_list.append(Thread(target=getEventLogItemsForWin7, args=(evtxLogFor7[1], prototype, "IEXPLORE.EXE", limitedTime, )))
        t_list.append(Thread(target=getEventLogItemsForWin7, args=(evtxLogFor7[2], prototype, None, limitedTime, )))
        t_list.append(Thread(target=getEventLogItemsForWin7, args=(evtxLogFor7[3], prototype, None, limitedTime, )))
    elif env == "Windows10":
        t_list.append(Thread(target=getEventLogItemsForWin10, args=(evtxLogFor10[0], prototype, "IEXPLORE.EXE", limitedTime,)))
        t_list.append(Thread(target=getEventLogItemsForWin10, args=(evtxLogFor10[1], prototype, None, limitedTime,)))
    t_list.append(Thread(target=getReportWER, args=(env, prototype, reportArchive, limitedTime,)))
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, prefetchList, limitedTime,)))
    t_list.append(Thread(target=getPrefetchItems, args=(prototype, list(set(prefetchList)), limitedTime,)))
    total = len(t_list)
    print("Total Thread: {}".format(total))
    for i in range(total-1):
        t_list[i].start()
    for i in range(total-1):
        t_list[i].join()

    t_list[total-1].start()
    t_list[total - 1].join()
    print(len(prototype))
    prototype.sort(key=itemgetter(1))
    return True, prototype

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
    11. [남] 웹 히스토리: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    12. [남] 웹 캐시: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    13. [보] 웹 다운로드, 웹 히스토리(exe)
    14. [보] 레지스트리 - 호환성 캐시 회색
    15. [보] 13번 과정에서 EXE 모두 추출 후 프리패치 파싱
    '''
