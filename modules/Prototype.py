import olefile
import modules.constant as CONSTANT

from libs.ParsePrefetch.prefetch import *
from libs.ParseJumpList.JumpListParser import *
from libs.ParseRegistry.ShimCacheParser import get_local_data
import libs.ParseEvtx.Evtx as evtx
import libs.ParseWebArtifact.WebArtifact as WebArtifact

def getApplicationEvtx(compared, prototype, checkedSW, timeline=None):
    items = []
    wer_info = []
    origin = checkedSW[0]
    orangeHead = [CONSTANT.EVENTLOG_KEYWORD, 2]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    checkedProviders = compared['providerName']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[5].get("SystemTime")
                if not loggedTime: continue
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                            continue
                    etc = ''
                    eventDataTag = event.lxml()[1]
                    if int(eventID) == 1000:
                        if eventDataTag[0].text not in origin: continue
                        etc = eventDataTag[0].text      # idx - 0 (SW), 3 (Module), 6 (Exception Code)
                    elif int(eventID) == 1001:
                        appcrashList = checkedSW[0] + checkedSW[1]
                        if eventDataTag[2].text != 'APPCRASH' or eventDataTag[5].text not in appcrashList: continue
                        etc = eventDataTag[5].text      # idx - 5 (SW), 8 (Module), 11 (Exception Code), 16 (PATH)
                        wer_info.append([eventDataTag[16].text, eventDataTag[8].text, eventDataTag[11].text])

                    if systemTag[2].text == '1':
                        level = 'Fatal'
                    elif systemTag[2].text == '2':
                        level = 'Error'
                    elif systemTag[2].text == '3':
                        level = 'Warning'
                    elif systemTag[2].text == '4':
                        level = 'Information'

                    items.append([orangeHead, loggedTime, providerName, eventID, level, etc, event.xml()])
            except Exception as e:
                print("Error: Application.evtx {}".format(e))
            continue
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
                if not loggedTime: continue
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
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
                print("Error: {}".format(e))
    prototype += items

def getFalutHeapEvtx(compared, prototype, type, timeline=None):
    items = []
    head = None
    if type == CONSTANT.IE:
        head = [CONSTANT.EVENTLOG_KEYWORD, 4]
    elif type == CONSTANT.OFFICE:
        head = [CONSTANT.EVENTLOG_KEYWORD, 3]

    fullPath = CONSTANT.EVENTLOG + compared['channel']
    checkedEID = compared['eid']
    checkedProviders = compared['providerName']
    with evtx.Evtx(fullPath) as log:
        for event in log.records():
            try:
                systemTag = event.lxml()[0]
                loggedTime = systemTag[7].get("SystemTime")
                if not loggedTime: continue
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
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
                print("Error: Fault.evtx {}".format(e))
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
                if not loggedTime: continue
                providerName = systemTag[0].get("Name")
                eventID = systemTag[1].text
                if int(eventID) in checkedEID:
                    if timeline:
                        if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
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
                print("Error: OAlert.evtx {}".format(e))
    prototype += items
#
# def getEventLogItemsForWin7(compared, prototype, origin=None, timeline=None):
#     items = []
#     headStr = "EventLog"
#     orangeHead = [headStr, 2]
#     yellowHead = [headStr, 3]
#     greenHead = [headStr, 4]
#     for fileName, category in compared.items():
#         fullPath = CONSTANT.EVENTLOG + fileName
#         checkedEID = category['eid']
#         checkedProviders = category['providerName']
#         with evtx.Evtx(fullPath) as log:
#             if fileName.startswith("App"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[5].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
#                             eventDataTag = event.lxml()[1]
#                             if int(eventID) == 1000 and eventDataTag[0].text not in origin: continue
#                             etc = eventDataTag[0].text
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[2].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[2].text == '2':
#                                 level = 'Error'
#                             elif systemTag[2].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[2].text == '4':
#                                 level = 'Information'
#
#                             items.append([orangeHead, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#                         continue
#             elif fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx") or fileName.endswith("WER-Diag%4Operational.evtx"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[7].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         head = []
#                         if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
#                             etc = ''
#                             if fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx"):
#                                 etc = 'Heap Corruption'
#                                 head = greenHead
#                             elif fileName.endswith("WER-Diag%4Operational.evtx"):
#                                 eventDataTag = event.lxml()[1]
#                                 etc = eventDataTag.get("Name")
#                                 head = yellowHead
#
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[3].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[3].text == '2':
#                                 level = 'Error'
#                             elif systemTag[3].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[3].text == '4':
#                                 level = 'Information'
#
#                             items.append([head, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#             elif fileName.startswith("OAlerts"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[5].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         if int(eventID) in checkedEID:
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[2].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[2].text == '2':
#                                 level = 'Error'
#                             elif systemTag[2].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[2].text == '4':
#                                 level = 'Information'
#                             eventDataTag = event.lxml()[1]
#                             etc = eventDataTag[0].text
#                             items.append([yellowHead, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#     prototype += items
#
# def getEventLogItemsForWin10(compared, prototype, checkedSW=None, timeline=None):
#     items = []
#     headStr = "EventLog"
#     orangeHead = [headStr, 2]
#     yellowHead = [headStr, 3]
#     greenHead = [headStr, 4]
#     origin = checkedSW[0]
#     reportArchive = []
#     for fileName, category in compared.items():
#         fullPath = CONSTANT.EVENTLOG + fileName
#         checkedEID = category['eid']
#         checkedProviders = category['providerName']
#         with evtx.Evtx(fullPath) as log:
#             if fileName.startswith("App"): # or fileName.startswith("System"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[5].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
#                             etc = ''
#                             # if fileName.startswith("App"):
#                             eventDataTag = event.lxml()[1]
#                             if int(eventID) == 1000:
#                                 if eventDataTag[0].text not in origin: continue
#                                 etc = eventDataTag[0].text
#                             elif int(eventID) == 1001:
#                                 appcrashList = checkedSW[0] + checkedSW[1]
#                                 if eventDataTag[2].text != 'APPCRASH' or eventDataTag[5].text not in appcrashList: continue
#                                 etc = eventDataTag[5].text
#                                 reportArchive.append(eventDataTag[16].text)
#                             # elif timeline:
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[2].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[2].text == '2':
#                                 level = 'Error'
#                             elif systemTag[2].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[2].text == '4':
#                                 level = 'Information'
#
#                             items.append([orangeHead, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#                         continue
#             elif fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[7].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         if int(eventID) in checkedEID and providerName == checkedProviders[eventID]:
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[3].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[3].text == '2':
#                                 level = 'Error'
#                             elif systemTag[3].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[3].text == '4':
#                                 level = 'Information'
#                             etc = 'Heap Corruption'
#                             items.append([greenHead, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#             elif fileName.startswith("OAlerts"):
#                 for event in log.records():
#                     try:
#                         systemTag = event.lxml()[0]
#                         loggedTime = systemTag[5].get("SystemTime")
#                         if not loggedTime: continue
#                         providerName = systemTag[0].get("Name")
#                         eventID = systemTag[1].text
#                         if int(eventID) in checkedEID:
#                             if timeline:
#                                 if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
#                                     continue
#                             if systemTag[2].text == '1':
#                                 level = 'Fatal'
#                             elif systemTag[2].text == '2':
#                                 level = 'Error'
#                             elif systemTag[2].text == '3':
#                                 level = 'Warning'
#                             elif systemTag[2].text == '4':
#                                 level = 'Information'
#                             eventDataTag = event.lxml()[1]
#                             etc = eventDataTag[0].text
#                             items.append([yellowHead, loggedTime, providerName, eventID, level, etc, event.xml()])
#                     except Exception as e:
#                         print("Error: {}".format(e))
#
#         prototype += items

def getReportWER(wer_info, prototype, type):
    import os
    import time
    head = None
    if type == CONSTANT.IE:
        head = [CONSTANT.WER_KEYWORD, 3]
    elif type == CONSTANT.OFFICE:
        head = [CONSTANT.WER_KEYWORD, 4]

    for data in wer_info:
        if os.path.exists(data[0]):
            fullpath = data[0] + "\\Report.wer"
            f = open(fullpath, "rb")
            content = f.read().decode('utf-16')
            createdTime = datetime.datetime.fromtimestamp(os.path.getctime(fullpath))
            modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
            prototype.append([head, "{}".format(modifiedTime), fullpath, data[1], data[2], "{}".format(createdTime), content])

'''
def getReportWER(env, prototype, reportArchive, type, timeline=None,):
    import time
    items = []
    headStr = "Report.wer"
    head = None
    if type == CONSTANT.IE:
        head = [headStr, 3]
    elif type == CONSTANT.OFFICE:
        head = [headStr, 4]

    for dirname in os.listdir(CONSTANT.WER[env]):
        if dirname.rsplit('_', 2)[0] in reportArchive:
            fullpath = CONSTANT.WER[env] + dirname + "\\Report.wer"
            f = open(fullpath, "rb")
            content = f.read().decode('utf-16')
            createdTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(fullpath)))
            if timeline:
                if datetime.datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S") < timeline:
                    continue
            modifiedTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fullpath)))
            items.append([head, modifiedTime, fullpath, createdTime, "", "", content])
    prototype += items
'''
def getPrefetchItems(prototype, included, timeline=None):
    items = []
    headStr = "Prefetch"
    grayHead = [headStr, 0]
    redHead = [headStr, 1]
    orangeHead = [headStr, 2]
    yellowHead = [headStr, 3]
    blueHead = [headStr, 5]
    purpleHead = [headStr, 7]

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
                print("[ - ] {}: Zero-byte Prefetch File".format(fname))
                continue
            try:
                p = Prefetch(CONSTANT.PREFETCH + fname)
            except Exception as e:
                print("[ - ] {} could not be parsed. {}".format(fname, e))

            pf_name = "{}-{}.pf".format(p.executableName, p.hash)
            createdTime = p.volumesInformationArray[0]["Creation Date"]
            createdTimeObj = datetime.datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S.%f")
            if p.executableName in included[0]: # 특정 SW
                content = p.getContents()
                items.append([redHead, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    head = redHead
                    if timeline:
                        if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") > timeline:
                            head = blueHead
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            elif p.executableName in included[1]:
                head = orangeHead
            elif p.executableName in included[2]:
                head = yellowHead    # WERFAULT
            elif p.executableName in included[3]:
                head = purpleHead
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
    '''
    MS-Office
    [빨] WINWORD.EXE, POWERPNT.EXE, EXCEL.EXE
    [주] WMIPRVSE.EXE, EQNEDT32.EXE, DW20.EXE, DWWIN.EXE
    [노] 타 프로세스 프리패치: WERFAULT.EXE
    [보] Cmd, Powershell 프리패치
    
    IE
    [빨] IE 프리패치: 생성, 실행 (웹 히스토리 첫 기록 이전)
    [파] IE 프리패치: 실행만 (웹 히스토리 첫 기록 이후)
    
    공통
    [회] 프리패치 - 첫 타임라인 이후 생성된 것만
    '''

def getJumplistItems(contents):
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
                    LinkFiles.append([
                        lnk_header[0],
                        lnk_header[1],
                        lnk_header[2],
                        lnk_after_header[3],
                        str(lnk_header[3]),
                        item[0] + "(" + str(int(item[0], 16)) + ")",
                        lnk_after_header[0],
                        lnk_after_header[1],
                        str(lnk_after_header[2]),
                    ])
                    lnk_tracker_value = file_data[ole.get_size(item) - 100:ole.get_size(item) - 96]
                    # print(lnk_tracker_value[0])
                    if lnk_tracker_value[0] == 96:  # link tracker information 4 byte value = 96
                        try:
                            lnk_tracker = lnk_file_tracker_data(file_data[ole.get_size(item) - 100:])  # last 100 bytes
                        except:
                            pass
                else:  # if first four byte value is not 76 then it is DestList stream
                    DestList = destlist_data(file_data[:ole.get_size(item)])
            except:
                pass
        idx = _list.index(content)
        _list[idx].append({
            "LinkFiles": LinkFiles,
            "DestList": DestList
        })
    return _list

def getWebArtifactItems(env, type, prefetchList=None, timeline=None, prototype=None):
    import glob
    cwd = os.getcwd()
    fileList = glob.glob(cwd + "\\WebCacheV*.dat")
    fullpath = ''
    items = {}
    if not fileList:
        dirname = CONSTANT.IE_ARTIFACT_PATH[env]["History"]
        fullpath = glob.glob(dirname + "WebCacheV*.dat")[0]
        logPath = cwd + '\\temp.txt'
        if os.path.exists(fullpath):
            _log = ''
            command2 = 'taskkill /f /im '
            try:
                killed_rst1 = os.system(command2 + "taskhostw.exe")
                killed_rst2 = os.system(command2 + "dllhost.exe")
            except Exception as e:
                print(killed_rst1)
                print(killed_rst2)
                killed_rst1 = -1
                killed_rst2 = -1
            import shutil
            try:
                shutil.copy(fullpath, cwd + "\\WebCacheV01.dat")
            except Exception as e:
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


def getAppCompatCache(prototype, prefetchList, timeline):
    rst = get_local_data(prefetchList, timeline)
    if rst:
        prototype += rst

def getRecentFileCache(filepath):
    contents = []
    with open(filepath, "rb") as f:
        # Offset
        offset = 0x14
        # File Size
        file_size = os.stat(filepath)[6]
        # Go to beginning of file.
        f.seek(0)
        # Read forward 0x14 (20).
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