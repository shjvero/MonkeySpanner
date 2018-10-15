import pyesedb
import datetime
import os, sys

EXE_EXTENSION = [ "exe", "doc", "docx", "hta", "xls", "ppts", "pptx", "pdf", "msu", "msi" ]
#Get file time
def getFiletime(dt):
    if dt == 0:
        return "-"
    else:
        try:
            microseconds = dt / 10
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 86400)
            return "{}".format(datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds))
        except:
            return "-"

#Fix response data
def fixRespData(txtin):
    if txtin is not None:
        fixed = txtin.decode("unicode-escape").replace("\n","\\").replace("\r","\\").replace(","," ").replace('"'," ")
        return ''.join(i for i in fixed if ord(i)<128)
    else:
        return ""

#Get history
def getHistory(filepath, timeline=None):
    esedb_file = pyesedb.file()
    esedb_file.open(filepath)
    containers = esedb_file.get_table_by_name("Containers")

    #Get list of containers that contain IE history
    histContList = []
    histNameDict = dict()
    histDirDict = dict()
    for cRecords in containers.records:
        if "Hist" in cRecords.get_value_data_as_string(8):
            histContList.append("Container_%s" % cRecords.get_value_data_as_integer(0))
            histNameDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(8)
            histDirDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(10)

    items = []
    head = ["History", 3]
    #Get history from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            _url = hRecords.get_value_data_as_string(17)
            if _url.count("@") > 0:
                accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
                if datetime.datetime.strptime(accessedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                    continue
                if _url[-3] in EXE_EXTENSION:
                    head[1] = 5
                items.append([
                    head,
                    accessedTime,    # Accessed Time
                    _url.split("@")[1],  # URL
                    getFiletime(hRecords.get_value_data_as_integer(12)),    # Modified Time
                    # str(getFiletime(hRecords.get_value_data_as_integer(10))),  # Created Time
                    # str(hRecords.get_value_data_as_integer(8)),  # Access Count
                    # hRecords.get_value_data_as_string(18),  # File Name
                    # "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),   # ID
                    # histNameDict[hcl],  # Container Name,
                    # getFiletime(hRecords.get_value_data_as_integer(11)),    # Expires
                    # getFiletime(hRecords.get_value_data_as_integer(9)),     # Synced
                    # hRecords.get_value_data_as_integer(15),                 # Sync Count
                    # hRecords.get_value_data_as_integer(5),                  # File Size
                    # histDirDict[hcl]  # Directory
                ])
            '''
            print("ID: {}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)))
            print("Container Name: {}".format(histNameDict[hcl]))
            print("Created: {}".format(getFiletime(hRecords.get_value_data_as_integer(10))))
            print("Accessed: {}".format(getFiletime(hRecords.get_value_data_as_integer(13))))
            print("Modified: {}".format(getFiletime(hRecords.get_value_data_as_integer(12))))
            print("Expires: {}".format(getFiletime(hRecords.get_value_data_as_integer(11))))
            print("Synced: {}".format(getFiletime(hRecords.get_value_data_as_integer(9))))
            print("Sync Count: {}".format(hRecords.get_value_data_as_integer(15)))
            print("Access Count: {}".format(hRecords.get_value_data_as_integer(8)))
            print("URL: {}".format(hRecords.get_value_data_as_string(17)))
            print("File Name: {}".format(hRecords.get_value_data_as_string(18)))
            print("File Size: {}".format(hRecords.get_value_data_as_integer(5)))
            print("Response Headers: -".format())
            print("Directory: {}".format(histDirDict[hcl]))
            '''
    return items

#Get content
def getContent(filepath, timeline=None):
    esedb_file = pyesedb.file()
    esedb_file.open(filepath)
    containers = esedb_file.get_table_by_name("Containers")

    #Get list of containers that contain IE content
    histContList = []
    histNameDict = dict()
    histDirDict = dict()
    for cRecords in containers.records:
        if "Content" in cRecords.get_value_data_as_string(8):
            histContList.append("Container_%s" % cRecords.get_value_data_as_integer(0))
            histNameDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(8)
            histDirDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(10)

    items = []
    exeList = []
    head = ["Cache", 4]
    #Get content from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
            if datetime.datetime.strptime(accessedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                continue
            fileName = hRecords.get_value_data_as_string(18)
            if fileName.count("."):
                extension = fileName.split(".")[1]
                if extension in EXE_EXTENSION:
                    head[1] = 6
                    if extension == EXE_EXTENSION[0]:
                        exeList.append(fileName.upper())
            items.append([
                head,
                accessedTime,  # Accessed Time
                hRecords.get_value_data_as_string(17),  # URL
                fileName,  # File Name
                str(hRecords.get_value_data_as_integer(5)),  # File Size
                str(getFiletime(hRecords.get_value_data_as_integer(10))),  # Created Time
                fixRespData(hRecords.get_value_data(21)),  # Response Headers
                # hRecords.get_value_data_as_integer(8),  # Access Count
                # "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),   # ID
                # histNameDict[hcl],  # Container Name
                # getFiletime(hRecords.get_value_data_as_integer(12)),    # Modified Time
                # getFiletime(hRecords.get_value_data_as_integer(11)),    # Expires
                # getFiletime(hRecords.get_value_data_as_integer(9)),     # Synced
                # hRecords.get_value_data_as_integer(15),                 # Sync Count
                # histDirDict[hcl],                                       # Directory
            ])
            '''
            print("ID: {}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)))
            print("Container Name: {}".format(histNameDict[hcl]))
            print("Created: {}".format(getFiletime(hRecords.get_value_data_as_integer(10))))
            print("Accessed: {}".format(getFiletime(hRecords.get_value_data_as_integer(13))))
            print("Modified: {}".format(getFiletime(hRecords.get_value_data_as_integer(12))))
            print("Expires: {}".format(getFiletime(hRecords.get_value_data_as_integer(11))))
            print("Synced: {}".format(getFiletime(hRecords.get_value_data_as_integer(9))))
            print("Sync Count: {}".format(hRecords.get_value_data_as_integer(15)))
            print("Access Count: {}".format(hRecords.get_value_data_as_integer(8)))
            print("URL: {}".format(hRecords.get_value_data_as_string(17)))
            print("File Name: {}".format(hRecords.get_value_data_as_string(18)))
            print("File Size: {}".format(hRecords.get_value_data_as_integer(5)))
            print("Response Headers: {}".format(fixRespData(hRecords.get_value_data(21))))
            print("Directory: {}".format(histDirDict[hcl]))
            '''
    return {
        'caches': items,
        'exeList': exeList
    }

#Get cookies
def getCookies(filepath):
    esedb_file = pyesedb.file()
    esedb_file.open(filepath)
    containers = esedb_file.get_table_by_name("Containers")

    #Get list of containers that contain IE cookies
    histContList = []
    histNameDict = dict()
    histDirDict = dict()
    for cRecords in containers.records:
        if "Cookies" in cRecords.get_value_data_as_string(8):
            histContList.append("Container_%s" % cRecords.get_value_data_as_integer(0))
            histNameDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(8)
            histDirDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(10)

    items = []
    #Get cookies from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            items.append([
                getFiletime(hRecords.get_value_data_as_integer(13)),  # Accessed Time
                {
                    'ID': "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                    # 'ContainerName': histNameDict[hcl],
                    'Created': getFiletime(hRecords.get_value_data_as_integer(10)),
                    'Modified': getFiletime(hRecords.get_value_data_as_integer(12)),
                    'Expires': getFiletime(hRecords.get_value_data_as_integer(11)),
                    'Synced': getFiletime(hRecords.get_value_data_as_integer(9)),
                    'SyncCount': hRecords.get_value_data_as_integer(15),
                    'AccessCount': hRecords.get_value_data_as_integer(8),
                    'URL': hRecords.get_value_data_as_string(17),
                    'FileName': hRecords.get_value_data_as_string(18),
                    'FileSize': hRecords.get_value_data_as_integer(5),
                    'Directory': histDirDict[hcl],
                }
            ])

    return items

#Get DOM
def getDom(filepath):
    esedb_file = pyesedb.file()
    esedb_file.open(filepath)
    containers = esedb_file.get_table_by_name("Containers")

    #Get list of containers that contain IE DOM info
    histContList = []
    histNameDict = dict()
    histDirDict = dict()
    for cRecords in containers.records:
        if "DOMStore" in cRecords.get_value_data_as_string(8):
            histContList.append("Container_%s" % cRecords.get_value_data_as_integer(0))
            histNameDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(8)
            histDirDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(10)

    items = []
    #Get DOM info from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            items.append([
                getFiletime(hRecords.get_value_data_as_integer(13)),  # Accessed Time
                {
                    'ID': "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                    'ContainerName': histNameDict[hcl],
                    'Created': getFiletime(hRecords.get_value_data_as_integer(10)),
                    'Modified': getFiletime(hRecords.get_value_data_as_integer(12)),
                    'Expires': getFiletime(hRecords.get_value_data_as_integer(11)),
                    'Synced': getFiletime(hRecords.get_value_data_as_integer(9)),
                    'SyncCount': hRecords.get_value_data_as_integer(15),
                    'AccessCount': hRecords.get_value_data_as_integer(8),
                    'URL': hRecords.get_value_data_as_string(17),
                    'FileName': hRecords.get_value_data_as_string(18),
                    'FileSize': hRecords.get_value_data_as_integer(5),
                    'Directory': histDirDict[hcl],
                }
            ])
    return items

#Get downloads
def getDownloads(filepath):
    esedb_file = pyesedb.file()
    esedb_file.open(filepath)
    containers = esedb_file.get_table_by_name("Containers")

    #Get list of containers that contain IE downloads
    histContList = []
    histNameDict = dict()
    histDirDict = dict()
    for cRecords in containers.records:
        if "download" in cRecords.get_value_data_as_string(8):
            histContList.append("Container_%s" % cRecords.get_value_data_as_integer(0))
            histNameDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(8)
            histDirDict["Container_%s" % cRecords.get_value_data_as_integer(0)] = cRecords.get_value_data_as_string(10)

    items = []
    #Get downloads from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            items.append([
                getFiletime(hRecords.get_value_data_as_integer(13)),  # Accessed Time
                {
                    'ID': "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                    'ContainerName': histNameDict[hcl],
                    'Created': getFiletime(hRecords.get_value_data_as_integer(10)),
                    'Modified': getFiletime(hRecords.get_value_data_as_integer(12)),
                    'Expires': getFiletime(hRecords.get_value_data_as_integer(11)),
                    'Synced': getFiletime(hRecords.get_value_data_as_integer(9)),
                    'SyncCount': hRecords.get_value_data_as_integer(15),
                    'AccessCount': hRecords.get_value_data_as_integer(8),
                    'URL': hRecords.get_value_data_as_string(17),
                    'FileName': hRecords.get_value_data_as_string(18),
                    'FileSize': hRecords.get_value_data_as_integer(5),
                    'Directory': histDirDict[hcl],
                }
            ])

    return items