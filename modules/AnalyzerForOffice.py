from modules.ArtifactAnalyzer import *

def getColumnHeader():
    return {
        CONSTANT.PREFETCH_KEYWORD: CONSTANT.TableHeader[CONSTANT.PREFETCH_KEYWORD],
        CONSTANT.WER_KEYWORD: CONSTANT.TableHeader[CONSTANT.WER_KEYWORD],
        CONSTANT.REGISTRY_KEYWORD: CONSTANT.TableHeader[CONSTANT.REGISTRY_KEYWORD],
        CONSTANT.LNKFILE_KEYWORD: CONSTANT.TableHeader[CONSTANT.LNKFILE_KEYWORD],
        CONSTANT.DESTLIST_KEYWORD: CONSTANT.TableHeader[CONSTANT.DESTLIST_KEYWORD],
        CONSTANT.EVENTLOG_KEYWORD: CONSTANT.TableHeader[CONSTANT.EVENTLOG_KEYWORD],
        CONSTANT.CACHE_KEYWORD: CONSTANT.TableHeader[CONSTANT.CACHE_KEYWORD]
    }


def getPrototype(env, office_msg=None):
    from operator import itemgetter
    from threading import Thread
    prefetchList = [
        ["WINWORD.EXE", "POWERPNT.EXE", "EXCEL.EXE"],  # Red
        ["WMIPRVSE.EXE", "EQNEDT32.EXE", "DW20.EXE", "DWWIN.EXE", "FLTLDR.EXE"],  # Orange
        ["WERFAULT.EXE"],  # Yellow
        ["CMD.EXE", "POWERSHELL.EXE"],  # PURPLE
    ]
    compared = [
        {
            'channel': "OAlerts.evtx",
            'eid': [300],
            'providerName': None
        },
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
    getPrefetchItems(CONSTANT.OFFICE, prototype, prefetchList)
    if prototype:
        prototype.sort(key=itemgetter(1))
        limitedTime = datetime.datetime.strptime(prototype[0][1], "%Y-%m-%d %H:%M:%S.%f")
    else:
        limitedTime = None

    t_list.append(Thread(target=getOAlertsEvtx, args=(compared[0], prototype, limitedTime,)))
    t_list.append(
        Thread(target=getApplicationEvtx, args=(CONSTANT.OFFICE, compared[1], prototype, prefetchList, limitedTime,)))
    t_list.append(Thread(target=getFalutHeapEvtx, args=(CONSTANT.OFFICE, compared[2], prototype, limitedTime,)))

    if env == CONSTANT.WIN7:
        compared.append({
            'channel': "Microsoft-Windows-WER-Diag%4Operational.evtx",
            'eid': [2],
            'providerName': {
                '2': 'Microsoft-Windows-WER-Diag'
            }
        })
        t_list.append(Thread(target=getWERDiagEvtxForWin7, args=(compared[3], prototype, limitedTime,)))
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, limitedTime,)))
    t_list.append(Thread(target=getJumplistItemsVerSummary, args=(CONSTANT.OFFICE, prototype,)))
    t_list.append(Thread(target=getWebArtifactItems, args=(env, CONSTANT.OFFICE, office_msg, limitedTime, prototype)))
    total = len(t_list)

    # print("Total Thread: {}".format(total))
    for i in range(total):
        t_list[i].start()
    for i in range(total):
        t_list[i].join()
    # print(len(prototype))
    prototype.sort(key=itemgetter(1))
    return True, prototype

    '''
    [빨] MS-Office 프리패치: WINWORD.EXE, POWERPNT.EXE, EXCEL.EXE
    [빨] 점프리스트
    [주] 오피스 프로세스 프리패치: WMIPRVSE.EXE, EQNEDT32.EXE, DW20.EXE, DWWIN.EXE, FLTLDR.EXE
    [노] 이벤트로그: Microsoft-Office-Alerts.evtx EID:300
    [노] 이벤트로그: Application.evtx EID 1001, Windows Error Reporting
    [노] 이벤트로그: Microsoft-Windows-WER-Diagnostics EID 2
    [노] 이벤트로그: Microsoft-Windows-Fault-Tolerant-Heap EID 1001
    [노] 타 프로세스 프리패치: WERFAULT.EXE
    [초] Report.wer
    [파] WebCache
    [남] 임시 파일 - 파일 시스템 로그 필요,,
            -- 경로: %LocalAppData%\Microsoft\Windows\Temporary Internet Files\Content.Word
    [보] Cmd, Powershell 프리패치 - 첫 타임라인 이후 (생성, 실행 모두)

    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    [회] 레지스트리 - 호환성 캐시

    (PASS to Dialog) 호환성 아티팩트: recentfilecache.bcf (win7), amache.hve (win10)
    '''