from modules.ArtifactAnalyzer import *

def getColumnHeader():
    return {
        CONSTANT.PREFETCH_KEYWORD: CONSTANT.TableHeader[CONSTANT.PREFETCH_KEYWORD],
        CONSTANT.EVENTLOG_KEYWORD: CONSTANT.TableHeader[CONSTANT.EVENTLOG_KEYWORD],
        CONSTANT.WER_KEYWORD: CONSTANT.TableHeader[CONSTANT.WER_KEYWORD],
        CONSTANT.REGISTRY_KEYWORD: CONSTANT.TableHeader[CONSTANT.REGISTRY_KEYWORD],
        CONSTANT.LNKFILE_KEYWORD: CONSTANT.TableHeader[CONSTANT.LNKFILE_KEYWORD],
        CONSTANT.DESTLIST_KEYWORD: CONSTANT.TableHeader[CONSTANT.DESTLIST_KEYWORD],
    }

def getPrototype(env):
    from operator import itemgetter
    from threading import Thread
    prefetchList = [
        ["HWP.EXE"],  # Red
        ["GBB.EXE", "GSWIN32C.EXE"],  # Orange
        ["WERFAULT.EXE"],
        ["CMD.EXE", "POWERSHELL.EXE"],  # PURPLE
        []
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
    prototype = []
    getPrefetchItems(CONSTANT.HWP, prototype, prefetchList)
    if prototype:
        prototype.sort(key=itemgetter(1))
        limitedTime = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
    else:
        limitedTime = None

    if env == CONSTANT.WIN7:
        compared.append({
            'channel': "Microsoft-Windows-WER-Diag%4Operational.evtx",
            'eid': [2],
            'providerName': {
                '2': 'Microsoft-Windows-WER-Diag'
            }
        })
        t_list.append(Thread(target=getWERDiagEvtxForWin7, args=(compared[2], prototype, limitedTime,)))
    t_list.append(Thread(target=getApplicationEvtx, args=(CONSTANT.HWP, compared[0], prototype, prefetchList, limitedTime,)))
    t_list.append(Thread(target=getFalutHeapEvtx, args=(CONSTANT.HWP, compared[1], prototype, limitedTime,)))
    t_list.append(Thread(target=getJumplistItemsVerSummary, args=(CONSTANT.HWP, prototype,)))
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, limitedTime,)))
    total = len(t_list)

    for i in range(total):
        t_list[i].start()
    for i in range(total):
        t_list[i].join()
    prototype.sort(key=itemgetter(1))
    return prototype

    '''
    [빨] HWP 프리패치: 생성 -- HWP.EXE
    [주] HWP 프리패치: 실행
    [주] 점프리스트
    [노] 연관 프로세스 프리패치: GBB.EXE, GSWIN32C.EXE
    [파] WER 프리패치: WERFAULT.EXE
    [남] Report.wer
    [남] 이벤트 로그: Application.evtx EID 1000, 1001
    [보] Cmd, Powershell 프리패치 - 첫 타임라인 이후 (생성, 실행 모두)

    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    [회] 레지스트리 - 호환성 캐시
    
    (PASS to SubWindow) 파일 시스템 삭제 파일(.ps)
    (PASS to Dialog) 호환성 아티팩트: recentfilecache.bcf (win7), amache.hve (win10)
    '''