from modules.Prototype import *
import datetime

def getColumnHeader():
    return {
        "Prefetch": ["Timeline", "File Name", "Executable Name", "Action", ""],			# 4 columns
        "EventLog": ["Logged Time", "Provider Name", "Event ID", "Level", "Data"],      # 5 columns
        "History": ["Accessed Time", "URL", "Modified Time", "", ""],					# 3 columns
        "Cache": ["Accessed Time", "URL", "File Name", "Size", "Created Time"],			# 5 columns
        "Download": ["Accessed Time", "URL", "File Name", "Size", "Download Path"],     # 5 columns
        "Report.wer": ["Modified Time", "Path", "Module", "Exception Code", "Created Time"],                # 3 columns
        "Registry": ["Modified Time", "Execution Path", "Size", "Exec Flag", "Registry Key"]       # 4 columns
    }

def getPrototype(env, timeline=None):
    from operator import itemgetter
    from threading import Thread
    prefetchList= [
        ["IEXPLORE.EXE"],   # RED
        [],
        ["WERFAULT.EXE"],   # Yellow
        ["CMD.EXE", "POWERSHELL.EXE", "RUNDLL32.EXE"]   # PURPLE
    ]
    compared = [
        {
            'channel': "Application.evtx",
            'eid': [1000, 1001],
            'providerName': {
                '1000': 'Application Error',
                '1001': 'Windows Error Reporting',
            }
        },
        {
            'channel': "Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx",
            'eid': [1001],
            'providerName': {
                '1001': 'Microsoft-Windows-Fault-Tolerant-Heap',
            }
        }
    ]
    t_list = []
    limitedTime = None
    result, prototype = getWebArtifactItems(env, CONSTANT.IE, prefetchList) # 다운로드된 것만 따로해서 레지스트리에서 검사필요?
    if not result:
        return result, prototype
    if prototype:
        prototype.sort(key=itemgetter(1))
        limitedTime = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")

    t_list.append(Thread(target=getApplicationEvtx, args=(CONSTANT.IE, compared[0], prototype, prefetchList, limitedTime,)))
    t_list.append(Thread(target=getFalutHeapEvtx, args=(CONSTANT.IE, compared[1], prototype, limitedTime,)))

    if env == CONSTANT.WIN7:
        compared.append({
            'channel': "Microsoft-Windows-WER-Diag%4Operational.evtx",
            'eid': [2],
            'providerName': {
                '2': 'Microsoft-Windows-WER-Diag'
            }
        })
        t_list.append(Thread(target=getWERDiagEvtxForWin7, args=(compared[2], prototype, limitedTime,)))
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, prefetchList[3], limitedTime,)))
    t_list.append(Thread(target=getPrefetchItems, args=(prototype, prefetchList, limitedTime,)))
    print(prefetchList[3])
    total = len(t_list)
    print("Total Thread: {}".format(total))
    for i in range(total):
        t_list[i].start()
    for i in range(total):
        t_list[i].join()

    print(len(prototype))
    prototype.sort(key=itemgetter(1))
    return True, prototype

    '''
    [빨] 웹 히스토리
    [빨] 웹 캐시: html, js 만 해당되는 경우
    [빨] IE 프리패치: 생성, 실행 (웹 히스토리 첫 기록 이전)
    [주] System.evtx EID 7036, 첫번째 로그의 시간을 저장한다.
    [주] Application.evtx EID 1000. (1번 저장 시간 이전은 제외)
    [노] WER-Diag%4Operational.evtx EID 2 (1번 저장 시간 이전은 제외) -- win7만 
    [노] WERFAULT 프리패치: 생성, 실행 모두
    [노] Report.wer: IE것만
    [초] Fault...heap.evtx EID 1001
    [파] IE 프리패치: 실행만 (웹 히스토리 첫 기록 이후)
    [남] 웹 히스토리: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    [남] 웹 캐시: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    [보] 웹 다운로드, 웹 히스토리(exe)
    [보] 13번 과정에서 EXE 모두 추출 후 프리패치 파싱
    
    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    [회] 레지스트리 - 호환성 캐시
    '''
