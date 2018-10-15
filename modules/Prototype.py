import os, sys
from libs.ParsePrefetch.prefetch import *
from libs.ParseJumpList.JumpListParser import *
import libs.ParseEvtx.Evtx as evtx
import libs.ParseEvtx.Views as e_views
import libs.IE.WebArtifact as WebArtifact
import modules.constant as PATH

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
def getEventLogItemsForWin7(evtxList, timeline=None):
    items = []
    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        eid = category['eid']
        providerName = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName == "Application.evtx" or fileName == "Microsoft-Windows-WER-Diag%4Operational.evtx":       # Application.evtx
                for event in log.records():
                    systemTag = event.lxml()[0]
                    if systemTag[1].text in eid and systemTag[0].get("Name") in providerName:
                        level = ''
                        if systemTag[2].text == '2':
                            level = '오류'
                        elif systemTag[2].text == '4':
                            level = '정보'
                        items.append([
                            systemTag[5].get("SystemTime"),     # Timeline
                            level,                              # Level
                            systemTag[1].text,                  # Event ID
                            systemTag[0].get("Name"),           # Provider Name
                            systemTag[3].text,                  # Task
                            systemTag[7].text,                  # Channel
                            event.xml()                         # detail
                        ])
            elif fileName == "System.evtx" or fileName == "Microsoft-Windows-Fault-Tolerant-Heap%4Operational.evtx":
                for event in log.records():
                    systemTag = event.lxml()[0]
                    if systemTag[1].text in eid and systemTag[0].get("Name") in providerName:
                        level = ''
                        if systemTag[3].text == '2':
                            level = '오류'
                        elif systemTag[3].text == '4':
                            level = '정보'
                        items.append([
                            systemTag[7].get("SystemTime"),     # Timeline
                            level,                              # Level
                            systemTag[1].text,                  # EventID
                            systemTag[0].get("Name"),           # Provider Name
                            systemTag[4].text,                  # Task
                            systemTag[11].text,                 # Channel
                            event.xml()                         # detail
                        ])
    return items

def getEventLogItemsForWin10(evtxList, timeline=None):
    items = []
    for fileName, category in evtxList.items():
        fullPath = PATH.EVENTLOG + fileName
        eid = category['eid']
        providerName = category['providerName']
        with evtx.Evtx(fullPath) as log:
            if fileName == "Application.evtx":
                for event in log.records():
                    systemTag = event.lxml()[0]
                    if systemTag[1].text in eid and systemTag[0].get("Name") in providerName:
                        level = ''
                        if systemTag[3].text == '2':
                            level = '오류'
                        elif systemTag[3].text == '4':
                            level = '정보'
                        items.append([
                            systemTag[5].get("SystemTime"),     # Timeline
                            level,                              # Level
                            systemTag[1].text,                  # EventID
                            systemTag[0].get("Name"),           # Provider Name
                            systemTag[4].text,                  # Task
                            systemTag[11].text,                 # Channel
                            event.xml()                         # detail
                        ])
            elif fileName == "System.evtx":
                for event in log.records():
                    systemTag = event.lxml()[0]
                    if systemTag[1].text in eid and systemTag[0].get("Name") in providerName:
                        level = ''
                        if systemTag[2].text == '2':
                            level = '오류'
                        elif systemTag[2].text == '4':
                            level = '정보'
                        items.append([
                            systemTag[5].get("SystemTime"),     # Timeline
                            level,                              # Level
                            systemTag[1].text,                  # Event ID
                            systemTag[0].get("Name"),           # Provider Name
                            systemTag[3].text,                  # Task
                            systemTag[7].text,                  # Channel
                            event.xml()
                        ])
    return items

def getPrefetchItems(exeNameList):
    items = []
    for i in os.listdir(PATH.PREFETCH):
        for sw in exeNameList:
            if i.startswith(sw) and i.endswith(".pf"):
                if os.path.getsize(PATH.PREFETCH + i) > 0:
                    try:
                        p = Prefetch(PATH.PREFETCH + i)
                    except Exception as e:
                        print("[ - ] {} could not be parsed".format(i))
                    content = p.prettyPrint()
                    pf_name = "{}-{}.pf".format(p.executableName, p.hash)
                    items.append([
                        p.volumesInformationArray[0]["Creation Date"],
                        pf_name,
                        p.executableName,
                        "Create",
                        content
                    ])
                    for timestamp in p.timestamps:
                        items.append([
                            timestamp,
                            pf_name,
                            p.executableName,
                            "Execute",
                            content
                        ])
                else:
                    print("[ - ] {}: Zero-byte Prefetch File".format(i))
            else:
                continue
    return items

def getJumplistItems(fileName):
    ''' 점프리스트 목록 조회
    filenames = os.listdir(PATH.JUMPLIST[0])    # AutomaticDestinations
    for fname in filenames:
        fullname = os.path.join(PATH.JUMPLIST[0], fname)
        print(fullname)
    '''
    LinkFiles = []
    DestList = []
    _path = PATH.JUMPLIST[0] + fileName
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

                LinkFiles.append({
                    'E_NO': item[0] + "(" + str(int(item[0], 16)) + ")",
                    'Modified': lnk_header[0],
                    'Accessed': lnk_header[1],
                    'Created': lnk_header[2],
                    'FileSize': lnk_header[3],
                    'DriveType': lnk_after_header[0],
                    'VolumeName': lnk_after_header[1],
                    'SerialNo': lnk_after_header[2],
                    'LocalBasePath': lnk_after_header[3],
                })

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

def getWebArtifactItems(env, type=None):
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
                        if os.system('taskkill /f /im "%s"'.format(t)) == 0:
                            print("[Kill] " + t)
                            if os.system('xcopy / s / h / i / y "{}" ".\\repo\\"'.format(fullpath)):
                                print("Failed copy..")
                            else:
                                fullpath = glob.glob(".\\repo\\WebCacheV*.dat")[0]
                        else:
                            flag += 1
                            print("[Error] Dirty Shutdown: " + t)
                if flag > 0:
                    return items
    else:
        fullpath = fileList[0]
    items["History"] = WebArtifact.getHistory(fullpath)
    items["Cache"] = WebArtifact.getContent(fullpath)
    # items = WebArtifact.getCookies(fullname)
    # items = WebArtifact.getDom(fullname)
    # items = WebArtifact.getDownloads(fullname)

    return items
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
