from modules.ArtifactAnalyzer import *

def getColumnHeader():
    return {
        CONSTANT.PREFETCH_KEYWORD: CONSTANT.TableHeader[CONSTANT.PREFETCH_KEYWORD],
        CONSTANT.WER_KEYWORD: CONSTANT.TableHeader[CONSTANT.WER_KEYWORD],
        CONSTANT.REGISTRY_KEYWORD: CONSTANT.TableHeader[CONSTANT.REGISTRY_KEYWORD],
        CONSTANT.EVENTLOG_KEYWORD: CONSTANT.TableHeader[CONSTANT.EVENTLOG_KEYWORD],
        CONSTANT.CACHE_KEYWORD: CONSTANT.TableHeader[CONSTANT.CACHE_KEYWORD],
        CONSTANT.HISTORY_KEYWORD: CONSTANT.TableHeader[CONSTANT.HISTORY_KEYWORD],
    }


def getPrototype(env, timeline=None):
    from operator import itemgetter
    from threading import Thread

    prefetchList = [
        ["IEXPLORE.EXE"],  # RED
        [],
        ["WERFAULT.EXE"],  # Yellow
        ["CMD.EXE", "POWERSHELL.EXE", "RUNDLL32.EXE"]  # PURPLE
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
    result, prototype = getWebArtifactItems(env, CONSTANT.IE, prefetchList)  # 다운로드된 것만 따로해서 레지스트리에서 검사필요?
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
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, limitedTime,)))
    t_list.append(Thread(target=getPrefetchItems, args=(CONSTANT.IE, prototype, prefetchList, limitedTime,)))
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
    [빨] 웹 캐시: html, js, css 등 웹 문서 파일만
    [빨] IE 프리패치: 생성, 실행 (웹 히스토리 첫 기록 이전)
    [주] Application.evtx EID 1000, 1001
    [노] WER-Diag%4Operational.evtx EID 2 -- win7만 
    [노] WERFAULT 프리패치: 생성, 실행 모두
    [노] Report.wer: IE것만
    [초] Fault...heap.evtx EID 1001
    [파] IE 프리패치: 실행만 (웹 히스토리 첫 기록 이후)
    [남] 웹 히스토리: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    [남] 웹 캐시: dll, doc, docx, hta, xls, woff, pdf (확장자 검사)
    [보] 웹 다운로드, 웹 히스토리(exe)
    [보] CMD, POWERSHELL 프리패치

    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    [회] 레지스트리 - 호환성 캐시
    '''
