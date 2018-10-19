import os, sys

from libs.ParsePrefetch.prefetch import *
from libs.ParseJumpList.JumpListParser import *
import libs.ParseEvtx.Evtx as evtx
import libs.ParseEvtx.Views as e_views
import libs.IE.WebArtifact as WebArtifact
import modules.constant as PATH
import datetime

'''
sw = {
    Win7 : {
        Application.evtx: {
            eid: [ ... ],
            providerName: [ ... ],
        },
        System.evtx: {
            eid: [ ... ],
            providerName: [ ... ],
        },
        Microsoft-Windows-WER-Diag%4Operational.evtx: 이하 동일
    },
    Win10 : {
        ...
    }
}
'''
def getEventLogItemsForWin7(evtxList, appName=None, timeline=None):
    items = []
    headStr = "EventLog"
    orangeHead = [headStr, 2]
    yellowHead = [headStr, 3]
    greenHead = [headStr, 4]
    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        checkedEID = category['eid']
        checkedProviders = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName.startswith("App"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[5].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text

                        if eventID in checkedEID and providerName in checkedProviders:
                            eventDataTag = event.lxml()[1]
                            if eventDataTag[0].text != appName: continue
                            etc = eventDataTag[0].text
                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[2].text == '2' else '정보'  # 정보는 4
                            # channel = systemTag[7].text

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
                        if eventID in checkedEID and providerName in checkedProviders:
                            etc = ''
                            if fileName.startswith("System"):
                                eventDataTag = event.lxml()[1]
                                etc = eventDataTag[0].text
                            elif fileName.endswith("Fault-Tolerant-Heap%4Operational.evtx"):
                                etc = '내결함성 있는 힙'
                            elif fileName.endswith("WER-Diag%4Operational.evtx"):
                                eventDataTag = event.lxml()[1]
                                etc = eventDataTag.get("Name")

                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[3].text == '2' else '정보'
                            # channel = systemTag[11].text

                            items.append([greenHead, loggedTime, providerName, eventID, level, etc, event.xml()])
                    except Exception as e:
                        print("Error: {}".format(e))

    return items

def getEventLogItemsForWin10(evtxList, appName=None, timeline=None):
    items = []
    orangeHead = ["EventLog", 2]
    greenHead = ["EventLog", 4]

    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        checkedEID = category['eid']
        checkedProviders = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName.startswith("App") or fileName.startswith("System"):
                for event in log.records():
                    try:
                        systemTag = event.lxml()[0]
                        loggedTime = systemTag[5].get("SystemTime")
                        if not loggedTime: continue
                        providerName = systemTag[0].get("Name")
                        eventID = systemTag[1].text

                        if eventID in checkedEID and providerName in checkedProviders:
                            etc = ''
                            if fileName.startswith("App"):
                                eventDataTag = event.lxml()[1]
                                if eventDataTag[0].text != appName: continue
                                etc = eventDataTag[0].text
                            elif timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[2].text == '2' else '정보'  # 정보는 4
                            # channel = systemTag[7].text

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
                        if eventID in checkedEID and providerName in checkedProviders:
                            if timeline:
                                if datetime.datetime.strptime(loggedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                                    continue
                            level = '오류' if systemTag[3].text == '2' else '정보'
                            # channel = systemTag[11].text
                            etc = '내결함성 있는 힙'
                            items.append([greenHead, loggedTime, providerName, eventID, level, etc, event.xml()])
                    except Exception as e:
                        print("Error: {}".format(e))

    return items

def getReportWER(_dirname, timeline=None):
    import time
    items = []
    yellowHead = ["Report.wer", 3]
    for dirname in os.listdir(PATH.WER):
        if dirname.startswith(_dirname):
            fullpath = PATH.WER + _dirname
            filename = [f for f in os.listdir(fullpath)]
            fullpath = fullpath + filename
            content = open(fullpath, "r").read()
            createdTime = time.ctime(os.path.getctime(fullpath))
            modifiedTime = time.ctime(os.path.getmtime(fullpath))
            items.append([yellowHead, modifiedTime, fullpath, createdTime, content])
    return items


def getPrefetchItems(included, timeline=None):
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
            # limitedTime = timeline[0] if timeline[0] else timeline[1]
            limitedTime = timeline[0] if timeline[0] else None
            if p.executableName == included[0]: # 특정 SW
                # if limitedTime:
                #     if createdTimeObj < limitedTime:
                #         head[1] = 0
                content = p.prettyPrint()
                items.append([redHead, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    if timeline[0]:
                        head = redHead if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") <= timeline[0] else blueHead
                    else:
                        head = blueHead
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            elif p.executableName == included[1]: #WERFAULT
                head = yellowHead
            elif not limitedTime and p.executableName not in included:
                continue
            elif p.executableName in included[2:]:
                content = p.prettyPrint()
                head = purpleHead
                if createdTimeObj > limitedTime:
                    items.append([head, createdTime, pf_name, p.executableName, "Create", content])
                for timestamp in p.timestamps:
                    if datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") < limitedTime:
                        continue
                    items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
                continue
            else:
                continue
            content = p.prettyPrint()
            items.append([head, createdTime, pf_name, p.executableName, "Create", content])
            for timestamp in p.timestamps:
                items.append([head, timestamp, pf_name, p.executableName, "Execute", content])
    return items

def getJumplistItems(fnameHash):
    ''' 점프리스트 목록 조회
    filenames = os.listdir(PATH.JUMPLIST[0])    # AutomaticDestinations
    for fname in filenames:
        fullname = os.path.join(PATH.JUMPLIST[0], fname)
        print(fullname)
    '''
    LinkFiles = []
    DestList = []
    _path = PATH.JUMPLIST[0] + fnameHash + ".automaticDestinations-ms"
    if not os.path.exists(_path):
        return
    assert olefile.isOleFile(_path)
    base = os.path.basename(_path)  # Get the JumpList file name
    # print(os.path.splitext(base)[0]) # split file name from extension
    ole = olefile.OleFileIO(_path)
    '''
    dirname = os.path.splitext(base)[0]
    try:
        os.makedirs(dirname)
    except OSError:
        if os.path.exists(dirname):
            pass
    newpath = os.path.join(os.getcwd(), dirname)
    
    newdirectory = os.chdir(newpath)
    csvfilename = open('LinkFiles.csv', 'w')
    field_names = ['E.No.', 'Modified', 'Accessed',
                   'Created', 'Drive Type', 'Volume Name', 'Serial No.', 'File Size', 'LocalBasePath']
    lnk_writer = csv.DictWriter(csvfilename, delimiter=',', lineterminator='\n', fieldnames=field_names)
    lnk_writer.writeheader()
    '''

    # print("E.No. | Modified | Accessed | Created | Drive Type | Volume Name | Serial No. | File Size | LocalBasePath")
    for item in ole.listdir():
        file = ole.openstream(item)
        file_data = file.read()
        header_value = file_data[:4]  # first four bytes value should be 76 bytes
        try:
            if header_value[0] == 76:  # first four bytes value should be 76 bytes
                lnk_header = lnk_file_header(file_data[:76])
                lnk_after_header = lnk_file_after_header(file_data)  # after 76 bytes to last 100 bytes

                '''
                newdirectory = os.chdir(newpath)
                csvfile = open('LinkFiles.csv', 'ab')
                lnk_writer.writerow({'E.No.': item[0] + "(" + str(int(item[0], 16)) + ")",
                                     'Modified': lnk_header[0], 'Accessed': lnk_header[1],
                                     'Created': lnk_header[2], 'Drive Type': lnk_after_header[0],
                                     'Volume Name': lnk_after_header[1], 'Serial No.': lnk_after_header[2],
                                     'File Size': lnk_header[3], 'LocalBasePath': lnk_after_header[3]})
                '''

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
    return {
        "LinkFiles": LinkFiles,
        "DestList": DestList
    }

def getWebArtifactItems(env, timeline=None):
    import glob
    fileList = glob.glob(".\\repo\\WebCacheV*.dat")
    fullpath = ''
    items = {}
    if not fileList:
        dirname = PATH.IE_ARTIFACT_PATH[env]["History"]
        fullpath = glob.glob(dirname + "WebCacheV*.dat")[0]
        if os.path.exists(fullpath):
            if os.system('tasklist | find /i "taskhost" > .\\repo\\target.txt') == 0:
                flag = 0
                with open(".\\repo\\target.txt", "r") as f:
                    for line in f.readlines():
                        if line == "\n":
                            continue
                        t = line.split()[0]
                        if os.system('taskkill /f /im "{}"'.format(t)) == 0:
                            print("[Kill] " + t)
                            # if os.system('xcopy / s / h / i / y "{}" ".\\repo\\"'.format(fullpath)):
                            #     print("Failed copy..")
                            # else:
                            #     fullpath = glob.glob(".\\repo\\WebCacheV*.dat")[0]
                        else:
                            flag += 1
                            print("[Error] Dirty Shutdown: '{}'".format(t))
                if flag > 0:
                    return items
    else:
        fullpath = fileList[0]

    # cookiesList = WebArtifact.getCookies(fullname)
    # domList = WebArtifact.getDom(fullname)
    # downloadList = WebArtifact.getDownloads(fullname)
    print("path: " + fullpath)
    history = WebArtifact.getHistory(fullpath, timeline)
    caches = WebArtifact.getContent(fullpath, timeline)
    return history + caches
'''
    items = {
        "history": [ 
                    [ Accesed Time, { ... } ],
                    [ Accesed Time, { ... } ],
                    [ Accesed Time, { ... } ],
                ]
        "content": [ 
                    [ Accesed Time, { ... } ],
                    [ Accesed Time, { ... } ],
                    [ Accesed Time, { ... } ],
                ]
    } 
'''

def getNTFSItems(type):
    items = []
    if type == 0:
        print("ALL NTFS Log")
    elif type == 1:
        print("Usnjrnl")
    elif type == 2:
        print("MFT")
    elif type == 3:
        print("LogFile")

    return items

def getSessionRestoreItems():
    print("세션저장")

def getbcf():
    print()
    # RecentFileCache.bcf ( only Windows 7 )
