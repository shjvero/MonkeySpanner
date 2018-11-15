import pyesedb
import datetime
import modules.constant as CONSTANT

DOM_EXTENSION = ['htm', 'html', 'js', 'css', 'php', 'jsp', 'asp', 'aspx']
DOC_EXTENSION = ['doc', 'docx', 'hta', 'rtf', 'xls', 'ppts', 'pptx', 'pdf', 'woff', 'sct', 'wsc']
ETC_EXTENSION = ['dll', 'bat', 'exe']

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
        # fixed = txtin.decode("unicode-escape").replace("\n","\\").replace("\r","\\").replace(","," ").replace('"'," ")
        fixed = txtin.decode("unicode-escape").replace(","," ").replace('"'," ")
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
                if URL[-3:] in DOC_EXTENSION:
                    head = navyHead
                elif URL[-3:] == "exe":
                    try:
                        prefetchList += URL.rsplit('/', 1)[-1].upper()
                    except Exception as e:
                        print(e)
                    head = purpleHead
                else:
                    head = redHead
                content = [
                    "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                    histNameDict[hcl],
                    "{}".format(getFiletime(hRecords.get_value_data_as_integer(10))),
                    "{}".format(accessedTime),
                    "{}".format(modifiedTime),
                    "{}".format(getFiletime(hRecords.get_value_data_as_integer(11))),
                    "{}".format(getFiletime(hRecords.get_value_data_as_integer(9))),
                    str(hRecords.get_value_data_as_integer(15)),
                    str(hRecords.get_value_data_as_integer(8)),
                    _url,
                    hRecords.get_value_data_as_string(18),
                    str(hRecords.get_value_data_as_integer(5)),
                    histDirDict[hcl],
                    None
                ]
                items.append([head, accessedTime, URL, modifiedTime, content])

    return items

#Get content
def getContent(filepath, timeline=None, type=CONSTANT.IE):
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
    grayHead = [CONSTANT.CACHE_KEYWORD, 0]
    redHead = [CONSTANT.CACHE_KEYWORD, 1]
    navyHead = [CONSTANT.CACHE_KEYWORD, 6]

    #Get content from each container
    for hcl in histContList:
        histCont = esedb_file.get_table_by_name(hcl)
        for hRecords in histCont.records:
            accessedTime = getFiletime(hRecords.get_value_data_as_integer(13))
            _url = hRecords.get_value_data_as_string(17)
            fileName = hRecords.get_value_data_as_string(18)
            fileSize = str(hRecords.get_value_data_as_integer(5))
            createdTime = str(getFiletime(hRecords.get_value_data_as_integer(10)))
            head = []
            if fileName.count("."):
                extension = fileName.split(".")[1]
                if type == CONSTANT.IE:
                    if extension in DOM_EXTENSION:
                        head = redHead
                    elif extension in DOC_EXTENSION + ETC_EXTENSION:
                        head = navyHead
                    else:
                        continue
                elif type == CONSTANT.OFFICE:
                    if extension in DOC_EXTENSION:
                        head = navyHead
                    elif extension in ETC_EXTENSION:
                        head = grayHead
                    else:
                        continue
            else:
                continue
            content = [
                "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                histNameDict[hcl],
                "{}".format(createdTime),
                "{}".format(accessedTime),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(12))),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(11))),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(9))),
                str(hRecords.get_value_data_as_integer(15)),
                str(hRecords.get_value_data_as_integer(8)),
                _url,
                fileName,
                fileSize,
                histDirDict[hcl],
                fixRespData(hRecords.get_value_data(21)),
            ]
            items.append([head, accessedTime, _url, fileName, fileSize, createdTime, content])
    return items

'''
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
            _url = hRecords.get_value_data_as_string(17)
            fileName = hRecords.get_value_data_as_string(18)
            if fileName.split('.')[1] == "exe":
                prefetchList += fileName.upper()
                print(fileName)
            fileSize = str(hRecords.get_value_data_as_integer(5))
            downloadPath = fixRespData(hRecords.get_value_data(21)) # 파싱필요
            content = [
                "{}.{}".format(hRecords.get_value_data_as_integer(1), hRecords.get_value_data_as_integer(0)),
                histNameDict[hcl],
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(10))),
                "{}".format(accessedTime),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(12))),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(11))),
                "{}".format(getFiletime(hRecords.get_value_data_as_integer(9))),
                str(hRecords.get_value_data_as_integer(15)),
                str(hRecords.get_value_data_as_integer(8)),
                _url,
                fileName,
                fileSize,
                histDirDict[hcl],
                downloadPath,
            ]
            items.append([purpleHead, accessedTime, _url, fileName, fileSize, "", content])
    return items
'''