from modules.Prototype import *


def getColumnHeader():
    return {
        "Prefetch": ["Timeline", "File Name", "Executable Name", "Action", ""],  # 4 columns
        "Report.wer": ["Modified Time", "Path", "Module", "Exception Code", "Created Time"],    # 5 columns
        "Registry": ["Modified Time", "Execution Path", "Size", "Exec Flag", "Registry Key"],   # 5 columns
        "JumpList[L]": ["Modified Time", "File Path", "Drive Type", "Size", "Created Time"],    # 5 columns
        "JumpList[D]": ["Last Recorded Time", "File Path", "File Name", "Access", "New (Timestamp)"],    # 5 columns
    }


def getPrototype(env):
    from operator import itemgetter
    from threading import Thread
    prefetchList = [
        ["HWP.EXE"],  # Red
        ["GBB.EXE", "GSWIN32C.EXE"],  # Orange
        ["WERFAULT.EXE"],  # Yellow
        # ["CMD.EXE", "POWERSHELL.EXE"],  # PURPLE
        []
    ]
    target = prefetchList[0] + prefetchList[1]
    reportArchive = ["appcrash_" + name.lower() for name in target]

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
    getPrefetchItems(prototype, prefetchList)
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
        t_list.append(Thread(target=getWERDiagEvtxForWin7, args=(compared[2], prototype, limitedTime, )))

    t_list.append(Thread(target=getApplicationEvtx, args=(CONSTANT.HWP, compared[0], prototype, prefetchList, limitedTime,)))
    t_list.append(Thread(target=getFalutHeapEvtx, args=(CONSTANT.HWP, compared[1], prototype, limitedTime,)))
    t_list.append(Thread(target=getJumplistItemsVerSummary, args=(CONSTANT.HWP, prototype, )))
    t_list.append(Thread(target=getAppCompatCache, args=(prototype, prefetchList[3], limitedTime,)))
    print(prefetchList[3])
    total = len(t_list)

    print("Total Thread: {}".format(total))
    for i in range(total):
        t_list[i].start()
    for i in range(total):
        t_list[i].join()
    print(len(prototype))
    prototype.sort(key=itemgetter(1))
    return prototype

    '''
    [ + ] 이벤트 로그 추가해서 수정 필요
    
    [빨] HWP 프리패치: HWP.EXE
    [주] 점프리스트
    [노] 연관 프로세스 프리패치: GBB.EXE, GSWIN32C.EXE
    [초] 파일 시스템 삭제 파일(.ps)
    [파] WER 프리패치: WERFAULT.EXE
    [파] Report.wer
    [남] 임시 파일 - 파일 시스템 로그 필요,,
    [보] Cmd, Powershell 프리패치 - 첫 타임라인 이후 (생성, 실행 모두)

    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    [회] 레지스트리 - 호환성 캐시

    (PASS to Dialog) 점프리스트
    (PASS to Dialog) 호환성 아티팩트: recentfilecache.bcf (win7), amache.hve (win10)
    '''