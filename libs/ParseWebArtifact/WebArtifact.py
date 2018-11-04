import pyesedb
import datetime

EXE_EXTENSION = ["dll", "rtf", "doc", "docx", "hta", "xls", "ppts", "pptx", "pdf", "woff", "hwp", "bat"]
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
def getHistory(filepath, prefetchList, timeline=None):
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
    headStr = "History"
    redHead = [headStr, 1]
    navyHead = [headStr, 6]
    purpleHead = [headStr, 7]
    #Get history from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            _url = hRecords.get_value_data_as_string(17)
            if _url.count("@") > 0:
                URL = _url.split("@")[1]
                if not URL.startswith("http"):
                    continue
                accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
                modifiedTime = getFiletime(hRecords.get_value_data_as_integer(12))
                if URL[-3:] in EXE_EXTENSION:
                    head = navyHead
                elif URL[-3:] == "exe":
                    try:
                        prefetchList += URL.rsplit('/', 1)[-1].upper()
                    except Exception as e:
                        print(e)
                    head = purpleHead
                else:
                    head = redHead
                content = "ID: {}.{}\n".format(hRecords.get_value_data_as_integer(1),
                                               hRecords.get_value_data_as_integer(0))
                content += "Container Name: {}\n".format(histNameDict[hcl])
                content += "Created Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(10)))
                content += "Accessed Time: {}\n".format(accessedTime)
                content += "Modified Time: {}\n".format(modifiedTime)
                content += "Expires Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(11)))
                content += "Synced Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(9)))
                content += "Sync Count: {}\n".format(hRecords.get_value_data_as_integer(15))
                content += "Access Count: {}\n".format(hRecords.get_value_data_as_integer(8))
                content += "URL: {}\n".format(_url)
                content += "File Name: {}\n".format(hRecords.get_value_data_as_string(18))
                content += "File Size: {}\n".format(hRecords.get_value_data_as_integer(5))
                content += "Directory: {}\n".format(histDirDict[hcl])
                items.append([head, accessedTime, URL, modifiedTime, content])

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
    redHead = ["Cache", 1]
    navyHead = ["Cache", 6]
    #Get content from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
            url = hRecords.get_value_data_as_string(17)
            fileName = hRecords.get_value_data_as_string(18)
            fileSize = str(hRecords.get_value_data_as_integer(5))
            createdTime = str(getFiletime(hRecords.get_value_data_as_integer(10)))
            head = []
            if fileName.count("."):
                extension = fileName.split(".")[1]
                if extension in ["htm", "html", "js", "php", "jsp", "asp", "aspx"]:
                    head = redHead
                elif extension in EXE_EXTENSION:
                    head = navyHead
                else:
                    continue
            else:
                continue
            content = "ID: {}.{}\n".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0))
            content += "Container Name: {}\n".format(histNameDict[hcl])
            content += "Created Time: {}\n".format(createdTime)
            content += "Accessed Time: {}\n".format(accessedTime)
            content += "Modified Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(12)))
            content += "Expires Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(11)))
            content += "Synced Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(9)))
            content += "Sync Count: {}\n".format(hRecords.get_value_data_as_integer(15))
            content += "Access Count: {}\n".format(hRecords.get_value_data_as_integer(8))
            content += "URL: {}\n".format(url)
            content += "File Name: {}\n".format(fileName)
            content += "File Size: {}\n".format(fileSize)
            content += "Response Headers: {}\n".format(fixRespData(hRecords.get_value_data(21)))
            content += "Directory: {}\n".format(histDirDict[hcl])
            items.append([head, accessedTime, url, fileName, fileSize, createdTime, content])
    return items

#Get downloads
def getDownloads(filepath, prefetchList, timeline=None):
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
    purpleHead = ["Download", 7]
    #Get downloads from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
            if timeline:
                if datetime.datetime.strptime(accessedTime, "%Y-%m-%d %H:%M:%S.%f") < timeline:
                    continue
            url = hRecords.get_value_data_as_string(17)
            fileName = hRecords.get_value_data_as_string(18)
            if fileName.split('.')[1] == "exe":
                prefetchList += fileName.upper()
                print(fileName)
            fileSize = hRecords.get_value_data_as_integer(5)
            downloadPath = fixRespData(hRecords.get_value_data(21)) # 파싱필요
            content = "ID: {}.{}\n".format(hRecords.get_value_data_as_integer(1),
                                           hRecords.get_value_data_as_integer(0))
            content += "Container Name: {}\n".format(histNameDict[hcl])
            content += "Created Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(10)))
            content += "Accessed Time: {}\n".format(accessedTime)
            content += "Modified Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(12)))
            content += "Expires Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(11)))
            content += "Synced Time: {}\n".format(getFiletime(hRecords.get_value_data_as_integer(9)))
            content += "Sync Count: {}\n".format(hRecords.get_value_data_as_integer(15))
            content += "Access Count: {}\n".format(hRecords.get_value_data_as_integer(8))
            content += "URL: {}\n".format(url)
            content += "File Name: {}\n".format(fileName)
            content += "File Size: {}\n".format(fileSize)
            content += "Response Headers: {}\n".format(downloadPath)
            content += "Directory: {}\n".format(histDirDict[hcl])
            items.append([purpleHead, accessedTime, url, fileName, fileSize, "", content])

    return items

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