import logging
import modules.constant as CONSTANT

from libs.ParsePrefetch.prefetch import *
from libs.ParseJumpList.JumpListParser import *
from libs.ParseRegistry.ShimCacheParser import get_local_data
import libs.ParseEvtx.Evtx as evtx
import libs.ParseWebArtifact.WebArtifact as WebArtifact

def getApplicationEvtx(type, compared, prototype, checkedSW, timeline=None):
    items = []
    wer_info = []
    origin = checkedSW[0]
    head1000 = head1001 = None
    if type in [CONSTANT.IE]:
        head1000 = head1001 = [CONSTANT.EVENTLOG_KEYWORD, 2]
    elif type in [CONSTANT.EDGE]:
        head1000 = [CONSTANT.EVENTLOG_KEYWORD, 2]
        head1001 = [CONSTANT.EVENTLOG_KEYWORD, 5]
    elif type in [CONSTANT.OFFICE]:
        head1000 = head1001 = [CONSTANT.EVENTLOG_KEYWORD, 3]
    elif type in [CONSTANT.HWP]:
        head1000 = head1001 = [CONSTANT.EVENTLOG_KEYWORD, 6]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    checkedProviders = compared['providerName']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[5].get("SystemTime")
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if not loggedTime: continue
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            logging.info("[Exception] EID - {}, {} was skipped, it's more older timeline".format(eventID, providerName))
                            continue

                    if systemTag[2].text == '4':
                        level = 'Information'
                    elif systemTag[2].text == '3':
                        level = 'Warning'
                    elif systemTag[2].text == '2':
                        level = 'Error'
                    elif systemTag[2].text == '1':
                        level = 'Fatal'

                    etc = ''
                    eventDataTag = event.lxml()[1]

                    if int(eventID) == 1000:
                        if eventDataTag[0].text.upper() not in origin: continue
                        etc = eventDataTag[0].text  # idx - 0 (SW), 3 (Module), 6 (Exception Code)
                        items.append([head1000, loggedTime, providerName, eventID, level, etc, event.xml()])
                    elif int(eventID) == 1001:
                        appcrashList = checkedSW[0] + checkedSW[1]
                        if eventDataTag[2].text != 'APPCRASH' or eventDataTag[5].text.upper() not in appcrashList: continue
                        etc = eventDataTag[5].text  # idx - 5 (SW), 8 (Module), 11 (Exception Code), 16 (PATH)
                        wer_info.append([eventDataTag[16].text, eventDataTag[8].text, eventDataTag[11].text])
                        items.append([head1001, loggedTime, providerName, eventID, level, etc, event.xml()])
            except Exception as e:
                if int(eventID) in checkedEID:
                    logging.info('[Error] EID - {} in "Application.evtx": {}'.format(eventID, e))
    if wer_info:
        type = CONSTANT.IE if not checkedSW[1] else CONSTANT.OFFICE
        getReportWER(wer_info, items, type)
    prototype += items


def getWERDiagEvtxForWin7(compared, prototype, timeline=None):
    items = []
    yellowHead = [CONSTANT.EVENTLOG_KEYWORD, 3]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    checkedProviders = compared['providerName']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[7].get("SystemTime")
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if not loggedTime: continue
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            logging.info("[Exception] EID - {}, {} was skipped, it's more older timeline".format(eventID, providerName))
                            continue
                    if systemTag[3].text == '1':
                        level = 'Fatal'
                    elif systemTag[3].text == '2':
                        level = 'Error'
                    elif systemTag[3].text == '3':
                        level = 'Warning'
                    elif systemTag[3].text == '4':
                        level = 'Information'
                    etc = 'Heap Corruption'
                    items.append([yellowHead, loggedTime, providerName, eventID, level, etc, event.xml()])
            except Exception as e:
                if int(eventID) in checkedEID:
                    logging.info('[Error] EID - {} in "WER-Diag/Operational.evtx": {}'.format(eventID, e))
    prototype += items


def getFalutHeapEvtx(type, compared, prototype, timeline=None):
    items = []
    head = None
    if type in [CONSTANT.IE, CONSTANT.HWP]:
        head = [CONSTANT.EVENTLOG_KEYWORD, 4]
    elif type in [CONSTANT.OFFICE]:
        head = [CONSTANT.EVENTLOG_KEYWORD, 3]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    checkedProviders = compared['providerName']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[7].get("SystemTime")
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if not loggedTime: continue
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            logging.info("[Exception] EID - {}, {} was skipped, it's more older timeline".format(eventID, providerName))
                            continue
                    if systemTag[3].text == '1':
                        level = 'Fatal'
                    elif systemTag[3].text == '2':
                        level = 'Error'
                    elif systemTag[3].text == '3':
                        level = 'Warning'
                    elif systemTag[3].text == '4':
                        level = 'Information'
                    eventDataTag = event.lxml()[1]
                    etc = eventDataTag.get("Name")
                    items.append([head, loggedTime, providerName, eventID, level, etc, event.xml()])
            except Exception as e:
                if int(eventID) in checkedEID:
                    logging.info('[Error] EID - {} in "Fault-Tolerant-Heap/Operational.evtx": {}'.format(eventID, e))
    prototype += items


def getOAlertsEvtx(compared, prototype, timeline=None):
    items = []
    yellowHead = [CONSTANT.EVENTLOG_KEYWORD, 3]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[5].get("SystemTime")
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if not loggedTime: continue
                if int(eventID) in checkedEID:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            logging.info("[Exception] EID - {}, {} was skipped, it's more older timeline".format(eventID, providerName))
                            continue
                    if systemTag[2].text == '1':
                        level = 'Fatal'
                    elif systemTag[2].text == '2':
                        level = 'Error'
                    elif systemTag[2].text == '3':
                        level = 'Warning'
                    elif systemTag[2].text == '4':
                        level = 'Information'
                    eventDataTag = event.lxml()[1]
                    etc = eventDataTag[0].text
                    items.append([yellowHead, loggedTime, providerName, eventID, level, etc, event.xml()])
            except Exception as e:
                if int(eventID) in checkedEID:
                    logging.info('[Error] EID - {} in "OAlerts.evtx": {}'.format(eventID, e))
    prototype += items


def getReportWER(wer_info, prototype, type):
    import os
    head = None
    if type == CONSTANT.IE:
        head = [CONSTANT.WER_KEYWORD, 3]
    elif type == CONSTANT.OFFICE:
        head = [CONSTANT.WER_KEYWORD, 4]
    elif type == [CONSTANT.HWP, CONSTANT.EDGE]:
        head = [CONSTANT.WER_KEYWORD, 6]

    for data in wer_info:
        if os.path.exists(data[0]):
            fullpath = data[0] + "\\Report.wer"
            f = open(fullpath, "rb")
            content = f.read().decode('utf-16')
            createdTime = datetime.datetime.fromtimestamp(os.path.getctime(fullpath))
            modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
            prototype.append(
                [head, "{}".format(modifiedTime), fullpath, data[1], data[2], "{}".format(createdTime), content])

def getPrefetchItems(type, prototype, included, timeline=None):
    items = []
    headStr = "Prefetch"
    grayHead = [headStr, 0]             # [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    shellHead = [headStr, 7]            # [보] Cmd, Powershell 프리패치
    if type == CONSTANT.IE:
        originHead = [headStr, 1]       # [빨] IEXPLORER.EXE: 본 프리패치 생성, 실행 (웹 히스토리 첫 기록 이전)
        werHead = [headStr, 3]          # [노] WERFAULT 프리패치: 생성, 실행 모두
        reExecutionHead = [headStr, 5]  # [파] IEXPLORER.EXE: 본 프리패치 실행만 (웹 히스토리 첫 기록 이후)
        shellHead = [headStr, 7]        # [보] Cmd, Powershell 프리패치
    elif type == CONSTANT.OFFICE:
        originHead = [headStr, 1]       # [빨] WINWORD.EXE, POWERPNT.EXE, EXCEL.EXE: 생성
        reExecutionHead = [headStr, 2]  # [주] WINWORD.EXE, POWERPNT.EXE, EXCEL.EXE: 생성
        relatedHead = [headStr, 2]      # [주] WMIPRVSE.EXE, EQNEDT32.EXE, DW20.EXE, DWWIN.EXE: 관련 프로세스 프리패치
        werHead = [headStr, 3]          # [노] WERFAULT 프리패치: 생성, 실행 모두
    elif type == CONSTANT.HWP:
        originHead = [headStr, 1]       # [빨] HWP.EXE: 생성
        reExecutionHead = [headStr, 2]  # [주] HWP.EXE: 실행
        relatedHead = [headStr, 3]      # [노] GBB.EXE, GSWIN32C.EXE: 관련 프로세스 프리패치
        werHead = [headStr, 5]          # [파] WER 프리패치: WERFAULT.EXE
    elif type == CONSTANT.EDGE:
        originHead = [headStr, 1]       # [빨] MICROSOFTEDGE.EXE: 생성
        reExecutionHead = [headStr, 1]  # [빨] MICROSOFTEDGE.EXE: 실행
        werHead = [headStr, 4]          # [초] WERFAULT 프리패치: 생성, 실행 모두(첫 기록 이전)
        relatedHead = [headStr, 6]      # [남] MICROSOFTEDGECP.EXE, MICROSOFTEDGEBCHOST.EXE: 관련 프로세스 프리패치
        # [노] SVCHOST 프리패치: 생성, 실행 모두(첫 기록 이전) -- 보류

    limitedTime = None
    if not timeline:
        import glob
        fileList = []
        for target in included[0]:
            fileList += glob.glob(CONSTANT.PREFETCH + "\\" + target + "*.pf")
        if not fileList:
            limitedTime = datetime.datetime.utcfromtimestamp(0)
        min_ctime = os.path.getctime(fileList[0])
        try:
            for file in fileList[1:]:
                file_ctime = os.path.getctime(file)
                if file_ctime < min_ctime:
                    min_ctime = file_ctime
            limitedTime = datetime.datetime.fromtimestamp(min_ctime)
        except:
            limitedTime = datetime.datetime.fromtimestamp(os.path.getctime(fileList[0]))

    for fname in os.listdir(CONSTANT.PREFETCH):
        if fname.endswith(".pf"):
            if os.path.getsize(CONSTANT.PREFETCH + fname) == 0:
                continue
            try:
                p = Prefetch(CONSTANT.PREFETCH + fname)
            except Exception as e:
                logging.info("[Error] {} could not be parsed. {}".format(fname, e))
            pf_name = "{}-{}.pf".format(p.executableName, p.hash)
            createdTime = p.volumesInformationArray[0]["Creation Date"]
            try:
                createdTimeObj = datetime.datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S.%f")
            except Exception as e:
                logging.info("{} in Parser Prefetch.".format(e))
                continue
            if p.executableName in included[0]:  # 특정 SW
                content = p.getContents()
                items.append([originHead, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    head = originHead
                    if timeline:
                        if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") > timeline:
                            head = reExecutionHead
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            elif p.executableName in included[1]:
                head = relatedHead
            elif p.executableName in included[2]:
                head = werHead
            elif p.executableName in included[3]:
                head = shellHead
            else:
                head = grayHead
            _limited = limitedTime if not timeline else timeline
            content = p.getContents()
            if createdTimeObj > _limited:
                items.append([head, createdTime, pf_name, p.executableName, "Create", content])
            for timestamp in p.timestamps:
                if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") > _limited:
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
    prototype += items


def getJumplistItemsVerSummary(type, prototype, timeline=None):
    import olefile
    contents = []
    if type == CONSTANT.HWP:
        contents.append(CONSTANT.JUMPLIST_HASH[15])
        contents.append(CONSTANT.JUMPLIST_HASH[16])
        contents.append(CONSTANT.JUMPLIST_HASH[17])
    elif type == CONSTANT.OFFICE:
        for i in range(12):
            contents.append(CONSTANT.JUMPLIST_HASH[i])
    _list = contents.copy()
    items = []
    LNKhead = [CONSTANT.LNKFILE_KEYWORD, 2]
    DESThead = [CONSTANT.DESTLIST_KEYWORD, 2]
    for content in contents:
        fullpath = CONSTANT.JUMPLIST[0] + content[1] + ".automaticDestinations-ms"
        if not os.path.exists(fullpath):
            _list.remove(content)
            logging.info("[Exception] {} JumpList doesn't exists".format(contents[0]))
            continue
        ole = olefile.OleFileIO(fullpath)

        idx = _list.index(content)
        for item in ole.listdir():
            file = ole.openstream(item)
            file_data = file.read()
            header_value = file_data[:4]
            try:
                if header_value[0] == 76:
                    lnk_header = lnk_file_header(file_data[:76])
                    lnk_after_header = lnk_file_after_header(file_data)
                    if timeline:
                        if datetime.datetime.strptime(lnk_header, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            logging.info("[Exception] A log in {} JumpList is skipped, it's more older timeline".format(contents[0]))
                            continue
                    items.append([
                        LNKhead,
                        lnk_header[0],  # Modified Time
                        lnk_after_header[3],  # LocalBasePath
                        "[LNK]" + lnk_after_header[0],  # Drive Type
                        lnk_header[3],  # File Size
                        lnk_header[2],  # Created Time
                        [fullpath.rsplit("\\", 1)[-1], _list[idx][0], "LNK", lnk_header + lnk_after_header]
                    ])
                else:
                    DestLists = destlist_data(file_data[:ole.get_size(item)])
                    for destList in DestLists:
                        items.append([
                            DESThead,
                            destList[0],  # destlist_object_timestamp
                            destList[1],  # Data = FullPath
                            destList[1].rsplit("\\", 1)[-1],  # FileName
                            destList[3],  # destlist_entry_access_count
                            destList[5],  # destlist_access_time
                            [fullpath.rsplit("\\", 1)[-1], _list[idx][0], "DestList", destList]
                        ])
            except:
                pass
    prototype += items


def getJumplistItems(contents):
    import olefile
    _list = contents.copy()
    for content in contents:
        fullpath = CONSTANT.JUMPLIST[0] + content[1] + ".automaticDestinations-ms"
        if not os.path.exists(fullpath):
            _list.remove(content)
            continue
        LinkFiles = []
        DestList = []
        ole = olefile.OleFileIO(fullpath)
        for item in ole.listdir():
            file = ole.openstream(item)
            file_data = file.read()
            header_value = file_data[:4]  # first four bytes value should be 76 bytes
            try:
                if header_value[0] == 76:  # first four bytes value should be 76 bytes
                    lnk_header = lnk_file_header(file_data[:76])
                    lnk_after_header = lnk_file_after_header(file_data)  # after 76 bytes to last 100 bytes
                    if not int(lnk_header[3]): continue
                    LinkFiles.append([
                        lnk_header[0],
                        lnk_header[1],
                        lnk_header[2],
                        lnk_after_header[3],
                        lnk_header[3],
                        item[0] + "(" + str(int(item[0], 16)) + ")",
                        lnk_after_header[0],
                        lnk_after_header[1],
                        lnk_after_header[2],
                    ])
                else:
                    DestList = destlist_data(file_data[:ole.get_size(item)])
            except:
                pass
        idx = _list.index(content)
        from operator import itemgetter
        _list[idx].append({
            "LinkFiles": sorted(LinkFiles, key=itemgetter(0)) if LinkFiles else [],
            "DestList": sorted(DestList, key=itemgetter(0)) if DestList else [],
        })
    return _list


def getWebArtifactItems(env, type, prefetchList=None, timeline=None, prototype=None):
    import glob
    import subprocess
    cwd = os.getcwd()
    fileList = glob.glob(cwd + "\\WebCacheV*.dat")
    fullpath = ''
    if not fileList:
        dirname = CONSTANT.IE_ARTIFACT_PATH[env]["History"]
        fullpath = glob.glob(dirname + "WebCacheV*.dat")[0]
        if os.path.exists(fullpath):
            _log = ''
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.call('taskkill /f /im "taskhostw.exe"', startupinfo=si)
            subprocess.call('taskkill /f /im "dllhost.exe"', startupinfo=si)

            import shutil
            try:
                shutil.copy(fullpath, cwd + "\\WebCacheV01.dat")
            except Exception:
                if type == CONSTANT.OFFICE:
                    prefetchList = "Please terminate any process using " + fullpath
                return False, "Please terminate any process using " + fullpath
            fullpath = glob.glob(cwd + "\\WebCacheV*.dat")[0]
    else:
        fullpath = fileList[0]

    if type == CONSTANT.IE:
        history = WebArtifact.getHistory(fullpath, prefetchList, timeline)
        caches = WebArtifact.getContent(fullpath, timeline, type)
        return True, history + caches
    elif type == CONSTANT.OFFICE:
        prototype += WebArtifact.getContent(fullpath, timeline, type)


def getAppCompatCache(prototype, timeline):
    rst = get_local_data(timeline)
    if rst:
        prototype += rst


def getRecentFileCache(filepath):
    contents = []
    with open(filepath, "rb") as f:
        offset = 0x14
        file_size = os.stat(filepath)[6]
        f.seek(0)
        f.seek(offset)
        while (offset < file_size):
            try:
                strLen = int.from_bytes(f.read(4), byteorder='little')
                if not strLen:
                    break
                fnlen = (strLen + 1) * 2
                contents.append(f.read(fnlen).decode('unicode-escape').replace('\x00', ''))
                file_size = offset + fnlen
            except Exception as e:
                return False, "{}".format(e)
    return True, contents
