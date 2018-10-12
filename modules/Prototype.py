import os, sys
from libs.ParsePrefetch.prefetch import *
import modules.constant as PATH
from libs.ParseJumpList.JumpListParser import *

def getPrefetchItems(sw):
    prototype = []
    for i in os.listdir(PATH.PREFETCH):
        if i.startswith(sw) and i.endswith(".pf"):
            if os.path.getsize(PATH.PREFETCH + i) > 0:
                try:
                    p = Prefetch(PATH.PREFETCH + i)
                except Exception as e:
                    print("[ - ] {} could not be parsed".format(i))
                content = p.prettyPrint()
                pf_name = "{}-{}.pf".format(p.executableName, p.hash)
                prototype.append([
                    p.volumesInformationArray[0]["Creation Date"],
                    {
                        "pf_name": pf_name,
                        "action": "CREATE",
                        "executableName": p.executableName,
                        "detail": content,
                    }
                ])
                for timestamp in p.timestamps:
                    prototype.append([
                        timestamp,
                        {
                            "pf_name": pf_name,
                            "action": "EXECUTE",
                            "executableName": p.executableName,
                            "detail": content
                        }
                    ])
            else:
                print("[ - ] {}: Zero-byte Prefetch File".format(i))
        else:
            continue
    return prototype

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