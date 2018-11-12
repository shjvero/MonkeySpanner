import olefile

from libs.ParsePrefetch.prefetch import *
from libs.ParseJumpList.JumpListParser import *
from libs.ParseRegistry.ShimCacheParser import get_local_data
import libs.ParseEvtx.Evtx as evtx
import libs.ParseWebArtifact.WebArtifact as WebArtifact
import modules.constant as PATH
import datetime

def getEventLogItemsForWin7(evtxList, prototype, appName=None, timeline=None):
    items = []
    headStr = "EventLog"
    orangeHead = [headStr, 2]
    yellowHead = [headStr, 3]
    greenHead = [headStr, 4]
    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        checkedEID = category['eid']
        checkedRID = category['recordID']
        # checkedProviders = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName.startswith("App"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[5].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text
                        recordID = systemTag[6].text
                        # if eventID in checkedEID and providerName in checkedProviders:
                        if int(eventID) in checkedEID and int(recordID) in checkedRID[eventID]:
                            eventDataTag = event.lxml()[1]
                            if eventDataTag[0].text != appName: continue
                            etc = eventDataTag[0].text
                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[2].text == '2' else '정보'  # 정보는 4

                            items.append([orangeHead, loggedTime, providerName, eventID, level, etc, event.xml()])
                    except Exception as e:
                        print("Error: {}".format(e))
                        continue
            elif fileName.startswith("System") or fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx") or fileName.endswith("WER-Diag%4Operational.evtx"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[7].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text
                        recordID = systemTag[8].text
                        head = []
                        # if eventID in checkedEID and providerName in checkedProviders:
                        if eventID in checkedEID and int(recordID) in checkedRID[eventID]:
                            etc = ''
                            if fileName.startswith("System"):
                                eventDataTag = event.lxml()[1]
                                etc = eventDataTag[0].text
                                if not etc.startswith("Windows Error Reporting"):
                                    continue
                                head = orangeHead
                            elif fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx"):
                                etc = '내결함성 있는 힙'
                                head = greenHead
                            elif fileName.endswith("WER-Diag%4Operational.evtx"):
                                eventDataTag = event.lxml()[1]
                                etc = eventDataTag.get("Name")
                                head = yellowHead

                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[3].text == '2' else '정보'

                            items.append([head, loggedTime, providerName, eventID, level, etc, event.xml()])
                    except Exception as e:
                        print("Error: {}".format(e))

    prototype += items

def getEventLogItemsForWin10(evtxList, prototype, appName=None, timeline=None):
    items = []
    orangeHead = ["EventLog", 2]
    greenHead = ["EventLog", 4]

    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        checkedEID = category['eid']
        checkedRID = category['recordID']
        # checkedProviders = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName.startswith("App") or fileName.startswith("System"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[5].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text
                        recordID = systemTag[6].text

                        # if eventID in checkedEID and providerName in checkedProviders:
                        if eventID in checkedEID and int(recordID) in checkedRID[eventID]:
                            etc = ''
                            if fileName.startswith("App"):
                                eventDataTag = event.lxml()[1]
                                if eventDataTag[0].text != appName: continue
                                etc = eventDataTag[0].text
                            elif timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[2].text == '2' else '정보'  # 정보는 4

                            items.append([orangeHead, loggedTime, providerName, eventID, level, etc, event.xml()])

                    except Exception as e:
                        print("Error: {}".format(e))
                        continue
            elif fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[7].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text
                        recordID = systemTag[8].text
                        # if eventID in checkedEID and providerName in checkedProviders:
                        if eventID in checkedEID and int(recordID) in checkedRID[eventID]:
                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[3].text == '2' else '정보'
                            etc = '힙 손상'
                            items.append([greenHead, loggedTime, providerName, eventID, level, etc, event.xml()])
                    except Exception as e:
                        print("Error: {}".format(e))

        prototype += items

def getReportWER(env, prototype, _dirname, timeline=None):
    import time
    items = []
    yellowHead = ["Report.wer", 3]
    for dirname in os.listdir(PATH.WER[env]):
        if dirname.startswith(_dirname):
            fullpath = PATH.WER[env] + dirname + "\\Report.wer"
            f = open(fullpath, "rb")
            content = f.read().decode('utf-16')
            createdTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(fullpath)))
            if timeline:
                if datetime.datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S") < timeline:
                    continue
            modifiedTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fullpath)))
            items.append([yellowHead, modifiedTime, fullpath, createdTime, "", "", content])
    prototype += items

def getPrefetchItems(prototype, included, timeline=None):
    items = []
    headStr = "Prefetch"
    redHead = [headStr, 1]
    yellowHead = [headStr, 3]
    blueHead = [headStr, 5]
    purpleHead = [headStr, 7]
    for i in os.listdir(PATH.PREFETCH):
        if i.endswith(".pf"):
            if os.path.getsize(PATH.PREFETCH + i) == 0:
                print("[ - ] {}: Zero-byte Prefetch File".format(i))
                continue
            try:
                p = Prefetch(PATH.PREFETCH + i)
            except Exception as e:
                print("[ - ] {} could not be parsed".format(i))

            pf_name = "{}-{}.pf".format(p.executableName, p.hash)
            createdTime = p.volumesInformationArray[0]["Creation Date"]
            createdTimeObj = datetime.datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S.%f")
            if p.executableName == included[0]: # 특정 SW
                # if limitedTime:
                #     if createdTimeObj < limitedTime:
                #         head[1] = 0
                content = p.prettyPrint()
                items.append([redHead, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    if timeline:
                        head = redHead if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") <= timeline else blueHead
                    else:
                        head = blueHead
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            elif p.executableName == included[1]: #WERFAULT
                head = yellowHead
            elif not timeline and p.executableName not in included:
                continue
            elif p.executableName in included[2:]:
                content = p.prettyPrint()
                head = purpleHead
                if createdTimeObj > timeline:
                    items.append([head, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                        continue
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            else:
                continue
            content = p.prettyPrint()
            items.append([head, createdTime, pf_name, p.executableName, "Create", content])
            for timestamp in p.timestamps:
                items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
    prototype += items

def getJumplistItems(contents):
    _list = contents
    for content in contents:
        fullpath = PATH.JUMPLIST[0] + content[1] + ".automaticDestinations-ms"
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

def getWebArtifactItems(env, prefetchList, timeline=None):
    import glob
    cwd = os.getcwd()
    fileList = glob.glob(cwd + "\\WebCacheV*.dat")
    fullpath = ''
    items = {}
    if not fileList:
        dirname = PATH.IE_ARTIFACT_PATH[env]["History"]
        fullpath = glob.glob(dirname + "WebCacheV*.dat")[0]
        logPath = cwd + '\\temp.txt'
        if os.path.exists(fullpath):
            _log = ''
            command1 = 'tasklist | find /i '
            command2 = 'taskkill /f /im '
            try:
                killed_rst1 = os.system(command2 + "taskhostw.exe")
                killed_rst2 = os.system(command2 + "dllhost.exe")
            except Exception as e:
                killed_rst1 = -1
                killed_rst2 = -1
            # os.system(command1 + '"taskhost" > ' + logPath)
            # os.system(command1 + '"dllhost" >> ' + logPath)
            # with open(logPath, "r+") as f:
            #     prevTask = ''
            #     killedList = []
            #     for line in f.readlines():
            #         if line == "\n" or line.startswith("background"):
            #             continue
            #         t = line.split()[0]
            #         if prevTask == t: continue
            #         killedList.append(t)
            #         # i = 0
            #         # for i in range(3):
            #         #     if os.system(command2 + '"{}" >> {}'.format(t, logPath)) == 0:
            #         #         break
            #         #     i += 1
            #         # if i > 0:
            #         #     return False, '[Not terminated] "{}"'.format(t)
            #         prevTask = t
            # print(killedList)
            # import shutil, psutil
            # for proc in psutil.process_iter():
            #     if proc.name in killedList:
            #         proc.kill()
            import shutil
            try:
                shutil.copy(fullpath, cwd + "\\WebCacheV01.dat")
            except Exception as e:
                print(e)
                return False, "Please terminate any process using " + fullpath
            fullpath = glob.glob(cwd + "\\WebCacheV*.dat")[0]
    else:
        fullpath = fileList[0]
    # cookiesList = WebArtifact.getCookies(fullname)
    # domList = WebArtifact.getDom(fullname)
    history = WebArtifact.getHistory(fullpath, prefetchList, timeline)
    caches = WebArtifact.getContent(fullpath, timeline)
    limitedTime = None if not history else datetime.datetime.strptime(history[0][1], "%Y-%m-%d %H:%M:%S.%f")
    download = WebArtifact.getDownloads(fullpath, prefetchList, limitedTime)
    return True, history + caches + download

def getAppCompatCache(prototype, prefetchList, timeline):
    rst = get_local_data(prefetchList, timeline)
    print("rst : ")
    print(rst)
    if rst:
        prototype += rst


