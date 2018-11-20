import sys
import uuid, struct, datetime
from bitstring import BitArray


def FromFiletime(filetime):
    if filetime < 0:
        return None
    timestamp = filetime / 10

    date_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
    # return date_time.strftime("%d %b %Y %I:%M:%S %p")
    return date_time.strftime("%Y-%m-%d %H:%M:%S.%f")

def lnk_flags(flags_to_parse):
    flags = {0: "HasLinkTargetIDList",
             1: "HasLinkInfo",
             2: "HasName",
             3: "HasRelativePath",
             4: "HasWorkingDir",
             5: "HasArguments",
             6: "HasIconLocation",
             7: "IsUnicode",
             8: "ForceNoLinkInfo",
             9: "HasExpString",
             10: "RunInSeparateProcess",
             11: "Unused1",
             12: "HasDarwinID",
             13: "RunAsUser",
             14: "HasExpIcon",
             15: "NoPidlAlias",
             16: "Unused2",
             17: "RunWithShimLayer",
             18: "ForceNoLinkTrack",
             19: "EnableTargetMetadata",
             20: "DisableLinkPathTracking",
             21: "DisableKnownFolderTracking",
             22: "DisableKnownFolderAlias",
             23: "AllowLinkToLink",
             24: "UnaliasOnSave",
             25: "PreferEnvironmentPath",
             26: "KeepLocalIDListForUNCTarget"}

    flags_to_parse = flags_to_parse[::-1]  # reverse the list
    setflags = []
    for count, items in enumerate(flags_to_parse):
        if int(items) == 1:
            setflags.append(count)
        else:
            continue
    return setflags


# This is the function to parse the attributes
# So to get this to work, you do lnk_attrib(bits_test.bin)
def lnk_attrib(attrib_to_parse):
    attrib = {0: "FILE_ATTRIBUTE_READONLY",
              1: "FILE_ATTRIBUTE_HIDDEN",
              2: "FILE_ATTRIBUTE_SYSTEM",
              3: "Reserved1",
              4: "FILE_ATTRIBUTE_DIRECTORY",
              5: "FILE_ATTRIBUTE_ARCHIVE",
              6: "Reserved2",
              7: "FILE_ATTRIBUTE_NORMAL",
              8: "FILE_ATTRIBUTE_TEMPORARY",
              9: "FILE_ATTRIBUTE_SPARSE_FILE",
              10: "FILE_ATTRIBUTE_REPARSE_POINT",
              11: "FILE_ATTRIBUTE_COMPRESSED",
              12: "FILE_ATTRIBUTE_OFFLINE",
              13: "FILE_ATTRIBUTE_NOT_CONTENT_INDEXED",
              14: "FILE_ATTRIBUTE_ENCRYPTED"}

def lnk_show_win(showwin):
    if showwin == hex(0x1):
        return "SW_SHOWNORMAL"
    elif showwin == hex(0x3):
        return "SW_SHOWMAXIMIZED"
    elif showwin == hex(0x7):
        return "SW_SHOWMINNOACTIVE"
    else:
        return "SW_SHOWNORMAL (default)"


def lnk_hot_key_high(hotkey_high):
    hotkey = {"0x0": "None",
              "0x1": "Shift",
              "0x2": "Ctrl",
              "0x3": "Shift + Ctrl",
              "0x4": "Alt",
              "0x5": "Shift + Alt",
              "0x6": "Ctrl + Alt"}
    bits_hotkey = BitArray(hex(hotkey_high))
    return hotkey[str(bits_hotkey)]


def lnk_hot_key_low(hotkey):
    return chr(hotkey)


def lnk_hot_key_parse(hotkey):
    hotkey_one = lnk_hot_key_high(hotkey[1])
    hotkey_two = lnk_hot_key_low(hotkey[0])
    return hotkey_one, hotkey_two


def convert_hex_to_ascii(h):
    h = h[2:16]
    machine_id = ''.join([chr(int(''.join(c), 16)) for c in zip(h[0::2], h[1::2])])
    return machine_id[::-1]


def convert_mac(mac):
    mac = mac[2:10] + mac[12:16]
    mac = [mac[i:i + 2] for i in range(0, len(mac), 2)]
    return ':'.join(str(i) for i in mac)


def change(changehex):
    changehex = changehex[:2] + changehex[10:] + changehex[6:10] + changehex[2:6]
    return changehex


def convert_hex(gethex):
    gethex = gethex[:2] + "0" + gethex[3:]
    return int(gethex, 0)


def lnk_file_header(header_data):
    header_list = []  # empty List

    lnk_header_size = struct.unpack("<L", header_data[0:4])
    header_clsid = header_data[4:20]
    lnk_header_clsid = uuid.UUID(bytes_le=header_clsid)

    # These two lines will parse out the individual bits in the Link flags section
    lnk_header_flags = struct.unpack("<I", header_data[20:24])
    lnk_header_flags_bits = BitArray(hex(lnk_header_flags[0]))

    # These two lines will parse out the individual bits for the file attributes
    lnk_header_file_attrib = struct.unpack("<I", header_data[24:28])
    lnk_header_file_attrib_bits = BitArray(hex(lnk_header_file_attrib[0]))

    # Parse the creation time stamp
    header_creation_time = struct.unpack("<Q", header_data[28:36])
    lnk_header_creation_time = FromFiletime(header_creation_time[0])

    # Parse the access time stamp
    header_access_time = struct.unpack("<Q", header_data[36:44])
    lnk_header_access_time = FromFiletime(header_access_time[0])

    # Parse the write time stamp
    header_write_time = struct.unpack("<Q", header_data[44:52])
    lnk_header_write_time = FromFiletime(header_write_time[0])

    lnk_header_file_size = struct.unpack("<L", header_data[52:56])
    lnk_header_icon_indx = struct.unpack("<L", header_data[56:60])
    lnk_header_show_window = struct.unpack("<L", header_data[60:64])
    lnk_header_hot_key = struct.unpack("<2B", header_data[64:66])
    hot_key = lnk_hot_key_parse(lnk_header_hot_key)

    lnk_flags(lnk_header_flags_bits.bin)
    lnk_attrib(lnk_header_file_attrib_bits.bin)
    header_list.append(lnk_header_write_time)
    header_list.append(lnk_header_access_time)
    header_list.append(lnk_header_creation_time)
    header_list.append(str(lnk_header_file_size[0]))

    return header_list


def lnk_file_after_header(lnk_file_data):
    after_header_list = []  # Empty List
    has_lnk_id_list_size = struct.unpack("<H", lnk_file_data[76:78])  # has link target id list size
    lnk_info_size = struct.unpack("<H", lnk_file_data[76 + has_lnk_id_list_size[0]:76 + has_lnk_id_list_size[0] + 2])  # 2 bytes  termination string
    lnk_info_size = struct.unpack("<L", lnk_file_data[78 + has_lnk_id_list_size[0]:82 + has_lnk_id_list_size[0]])  # 4 bytes Link ifomation size
    lnk_info_header_size = struct.unpack("<L", lnk_file_data[82 + has_lnk_id_list_size[0]:82 + has_lnk_id_list_size[0] + 4])  # 4 bytes header size
    lnk_info_flags = struct.unpack("<L", lnk_file_data[86 + has_lnk_id_list_size[0]:86 + has_lnk_id_list_size[0] + 4])  # 4 bytes link information flags

    '''
    if lnk_info_flags[0] == 1:
        print("Flags: VolomeIDAndLocalBasePath")
    if lnk_info_flags[0] == 3:
        print("Flags: VolomeIDAndLocalBasePath,CommonNetworkRelativeLinkAndPathSuffix")
    '''

    # 4 bytes volume id offset
    lnk_volumeidoffset = struct.unpack("<L", lnk_file_data[90 + has_lnk_id_list_size[0]:90 + has_lnk_id_list_size[0] + 4])
    # 4 bytes volume id offset
    lnk_localbasepathoffset = struct.unpack("<L", lnk_file_data[94 + has_lnk_id_list_size[0]:94 + has_lnk_id_list_size[0] + 4])
    # 4 bytes volume id offset
    lnk_commonnetworkrelativelinkoffset = struct.unpack("<L", lnk_file_data[98 + has_lnk_id_list_size[0]:102 + has_lnk_id_list_size[0]])
    # 4 bytes volume id offset
    lnk_commonpathsuffixoffset = struct.unpack("<L", lnk_file_data[102 + has_lnk_id_list_size[0]:106 + has_lnk_id_list_size[0]])
    # 4 bytes volume id offset
    lnk_volumeid_size = struct.unpack("<L",
                                      lnk_file_data[78 + has_lnk_id_list_size[0] + lnk_volumeidoffset[0]:lnk_volumeidoffset[0] + 82 + has_lnk_id_list_size[0]])
    # 4 bytes volume id offset
    lnk_drivetype = struct.unpack("<L", lnk_file_data[
                                        82 + has_lnk_id_list_size[0] + lnk_volumeidoffset[0]:lnk_volumeidoffset[0] + 86 + has_lnk_id_list_size[0]])

    if lnk_drivetype[0] == 0:
        after_header_list.append("The drive can not be determined")
    elif lnk_drivetype[0] == 1:
        after_header_list.append("No volume mounted")
    elif lnk_drivetype[0] == 2:
        after_header_list.append("Removable")
    elif lnk_drivetype[0] == 3:
        after_header_list.append("Fixed")
    elif lnk_drivetype[0] == 4:
        after_header_list.append("Network")
    elif lnk_drivetype[0] == 5:
        after_header_list.append("CD-ROM")
    else:
        after_header_list.append("RAM Disk")

    # 4 bytes volume id offset
    lnk_driveserialnumber = struct.unpack("<L",
                                          lnk_file_data[86 + has_lnk_id_list_size[0] + lnk_volumeidoffset[0]:lnk_volumeidoffset[0] + 90 + has_lnk_id_list_size[0]])
    # 4 bytes volume id offset
    lnk_volumelabeloffset = struct.unpack("<L",
                                          lnk_file_data[90 + has_lnk_id_list_size[0] + lnk_volumeidoffset[0]:lnk_volumeidoffset[0] + 94 + has_lnk_id_list_size[0]])

    if lnk_volumelabeloffset[0] == 14:
        offset1 = lnk_volumeid_size[0] - (4 + 4 + 4 + 4 + 4)
    else:
        offset1 = lnk_volumeid_size[0] - (4 + 4 + 4 + 4)

    # volume id size - 20
    # 4 bytes volume id offset
    lnk_volumelabel = lnk_file_data[lnk_volumeidoffset[0] + 94 + has_lnk_id_list_size[0]:lnk_volumeidoffset[0] + 94 + has_lnk_id_list_size[0] + offset1]
    Volume_Label = lnk_volumelabel.decode('ascii')
    after_header_list.append(Volume_Label)
    after_header_list.append(str(lnk_driveserialnumber[0]))

    if lnk_info_flags[0] == 1:
        size_of_localbasepath = lnk_info_size[0] - lnk_localbasepathoffset[0]

        lnk_localbasepath = lnk_file_data[
                            78 + has_lnk_id_list_size[0] + lnk_localbasepathoffset[0]:78 + has_lnk_id_list_size[0] + lnk_localbasepathoffset[0] + size_of_localbasepath
                            ]
        LocalBasePath = lnk_localbasepath.decode('ascii')
        after_header_list.append(LocalBasePath)

    if lnk_info_flags[0] == 3:
        size_of_localbasepath = lnk_commonnetworkrelativelinkoffset[0] - lnk_localbasepathoffset[0]
        lnk_localbasepath = lnk_file_data[
                            78 + has_lnk_id_list_size[0] + lnk_localbasepathoffset[0]:78 + has_lnk_id_list_size[0] + lnk_localbasepathoffset[0] + size_of_localbasepath
                            ]
        tempoffset = 78 + has_lnk_id_list_size[0] + lnk_commonnetworkrelativelinkoffset[0]

        # 4 bytes CommonNetworkRelativeLink Size
        lnk_commonnetworkrelativelink_size = struct.unpack("<L", lnk_file_data[tempoffset:tempoffset + 4])
        lnk_commonnetworkrelativelink_flags = struct.unpack("<L", lnk_file_data[tempoffset + 4:tempoffset + 8])
        lnk_commonnetworkrelativelink_netnameoffset = struct.unpack("<L", lnk_file_data[tempoffset + 8:tempoffset + 12])
        lnk_commonnetworkrelativelink_devicenameoffset = struct.unpack("<L", lnk_file_data[tempoffset + 12:tempoffset + 16])
        lnk_commonnetworkrelativelink_networkprovidertype = struct.unpack("<L", lnk_file_data[tempoffset + 16:tempoffset + 20])

        if lnk_commonnetworkrelativelink_netnameoffset[0] > 14:
            netname_size = lnk_commonnetworkrelativelink_size[0] - (20)
            lnk_commonnetworkrelativelink_netname = lnk_file_data[tempoffset + lnk_commonnetworkrelativelink_netnameoffset[0]:]

    commonpathsuffix_size = lnk_info_size[0] - lnk_commonpathsuffixoffset[0]
    # 4 bytes volume id offset
    lnk_commonpathsuffix = lnk_file_data[78
                                         + lnk_commonpathsuffixoffset[0]
                                         + has_lnk_id_list_size[0]:78
                                                                   + lnk_commonpathsuffixoffset[0]
                                                                   + has_lnk_id_list_size[0]
                                                                   + commonpathsuffix_size
                           ]

    return after_header_list


def lnk_file_tracker_data(tracker_data):
    # This prints distributed link tracker properties data block is 96 bytes of size.
    # print("Distributed Link Tracker Properties:\n")

    lnk_tracker_size = struct.unpack("<L", tracker_data[0:4])
    # print("Tracker size: {} (integer: {})".format(hex(lnk_tracker_size[0]), lnk_tracker_size[0]))

    # This prints Machine identifier string ASCII string terminated by an end-of-string character Unused bytes are set to 0
    lnk_tracker_machine_identifier = struct.unpack("<2Q", tracker_data[16:32])
    # print("Machine ID: {}".format(convert_hex_to_ascii(hex(lnk_tracker_machine_identifier[0]))))

    # This prints  new volume identifier
    volume_identifier = tracker_data[32:48]
    lnk_volume_identifier = uuid.UUID(bytes_le=volume_identifier)
    # print("New Volume ID: {}".format(lnk_volume_identifier))

    # This prints GUID containing an NTFS new object identifier
    object_identifier = tracker_data[48:64]
    lnk_object_identifier = uuid.UUID(bytes_le=object_identifier)
    # print("New Object ID: {}".format(lnk_object_identifier))

    # This prints the Object ID (Timestamp)
    # reads in little endian form first 2 byte(higher order time) next 2 bytes (middle order time)
    # and next 4 bytes (lower order time). First bit of higher order time is 0. (version number)
    object_timestamp = struct.unpack("<Q", tracker_data[48:56])
    object_timestamp_value = convert_hex(hex(object_timestamp[0]))
    lnk_object_timestamp = FromFiletime(object_timestamp_value - 5748192000000000)
    # print("New Object ID (Timestamp): {}".format(lnk_object_timestamp))

    # This prints the Object ID (Sequence number )
    object_sequence = struct.unpack(">H", tracker_data[56:58])
    # print("New ObjectID (Seq. No): {}".format(object_sequence[0]))

    # This prints the MAC address of the primary newtork card in the computer system
    object_mac1 = struct.unpack(">L", tracker_data[58:62])
    object_mac2 = struct.unpack(">H", tracker_data[62:64])
    # print("New ObjectID (MAC): {}".format(convert_mac(hex(object_mac1[0]) + hex(object_mac2[0]))))

    # This prints Birth volume identifier
    birth_volume_identifier = tracker_data[64:80]
    lnk_birth_volume_identifier = uuid.UUID(bytes_le=birth_volume_identifier)
    # print("Birth Volume ID: {}".format(lnk_birth_volume_identifier))

    # This prints Birth volume identifier
    birth_object_identifier = tracker_data[80:96]
    lnk_birth_object_identifier = uuid.UUID(bytes_le=birth_object_identifier)
    # print("Birth Object ID: {}".format(lnk_birth_object_identifier))

    # This prints the Birth Object ID (Timestamp)
    birth_object_timestamp = struct.unpack("<Q", tracker_data[80:88])
    # print(hex(object_timestamp[0]))
    birth_object_timestamp_value = convert_hex(hex(birth_object_timestamp[0]))
    birth_lnk_object_timestamp = FromFiletime(birth_object_timestamp_value - 5748192000000000)
    # print("Birth Object ID (Timestamp): {}".format(birth_lnk_object_timestamp))

    # This prints the Birth Object ID (Sequence number )
    birth_object_sequence = struct.unpack(">H", tracker_data[88:90])
    # print("Birth Object ID (Seq. No): {}".format(birth_object_sequence[0]))

    # This prints the Birth MAC address of the primary newtork card in the computer system
    birth_object_mac1 = struct.unpack(">L", tracker_data[90:94])
    birth_object_mac2 = struct.unpack(">H", tracker_data[94:96])
    # print("Birth Object ID (MAC): {}".format(convert_mac(hex(birth_object_mac1[0]) + hex(birth_object_mac2[0]))))


def destlist_data(destlist_file_data):
    destlist_header_value = destlist_file_data[:4]  # Version Number

    destlist_totalentries = destlist_file_data[4:8]  # Total number of current entries in jump list
    destlist_pinned_entries = destlist_file_data[8:12]  # Total number of pinned entries
    destlist_header_value = destlist_file_data[12:16]  # Some type of counter
    destlist_lastissue_entry = destlist_file_data[16:24]  # Last issued Entry ID number
    destlist_add_delete = destlist_file_data[
                          24:32]  # Number of add/delete actions – Increments as entries are added.  Also increments as individual entries are deleted.

    destlist_entry_volumeid = destlist_file_data[40:56]  # New volume ID
    destlist_volume_identifier = uuid.UUID(bytes_le=destlist_entry_volumeid)

    destlist_entry_objectid = destlist_file_data[56:72]  # New Object ID
    destlist_object_identifier = uuid.UUID(bytes_le=destlist_entry_objectid)

    destlist_object_timestamp = struct.unpack("<Q", destlist_file_data[56:64])
    destlist_object_timestamp_value = convert_hex(hex(destlist_object_timestamp[0]))
    destlist_object_timestamp = FromFiletime(destlist_object_timestamp_value - 5748192000000000)

    destlist_object_sequence = struct.unpack(">H", destlist_file_data[64:66])

    # This prints the MAC address of the primary newtork card in the computer system
    destlist_object_mac1 = struct.unpack(">L", destlist_file_data[66:70])
    destlist_object_mac2 = struct.unpack(">H", destlist_file_data[70:72])
    new_mac = convert_mac(hex(destlist_object_mac1[0]) + hex(destlist_object_mac2[0]))

    destlist_entry_volumeid = destlist_file_data[72:88]  # Birth volume ID
    destlist_volume_identifier = uuid.UUID(bytes_le=destlist_entry_volumeid)

    destlist_entry_objectid = destlist_file_data[88:104]  # Birth Object ID
    destlist_object_identifier = uuid.UUID(bytes_le=destlist_entry_objectid)

    birth_destlist_object_timestamp = struct.unpack("<Q", destlist_file_data[88:96])
    birth_destlist_object_timestamp_value = convert_hex(hex(birth_destlist_object_timestamp[0]))
    birth_destlist_object_timestamp = FromFiletime(birth_destlist_object_timestamp_value - 5748192000000000)

    birth_object_sequence = struct.unpack(">H", destlist_file_data[96:98])

    birth_object_mac1 = struct.unpack(">L", destlist_file_data[98:102])
    birth_object_mac2 = struct.unpack(">H", destlist_file_data[102:104])
    birth_mac = convert_mac(hex(birth_object_mac1[0]) + hex(birth_object_mac2[0]))

    # This prints NetBIOS Name ASCII string terminated by an end-of-string character Unused bytes are set to 0
    destlist_netbiosname = destlist_file_data[104:120]
    destlist_netbiosname = destlist_netbiosname.decode('ascii')

    destlist_entryidnumber = struct.unpack("<L", destlist_file_data[120:124])  # Entry ID number

    destlist_some_test1 = struct.unpack("<Q", destlist_file_data[124:132])  # some test

    # Parse the last recorded access time stamp
    destlist_entry_last_access_time = struct.unpack("<Q", destlist_file_data[132:140])
    destlist_access_time = FromFiletime(destlist_entry_last_access_time[0])

    destlist_entrypin_status = struct.unpack("<L", destlist_file_data[140:144])  # Entry Pin status

    destlist_some_test2 = struct.unpack("<L", destlist_file_data[144:148])  # Entry Pin status

    destlist_entry_access_count = struct.unpack("<L", destlist_file_data[148:152])  # Access Count

    destlist_some_test4 = struct.unpack("<Q", destlist_file_data[152:160])  # Entry Pin status

    destlist_lengthstringdata = struct.unpack("<H", destlist_file_data[160:162])  # Length of Unicode string data
    # print(destlist_lengthstringdata[0])

    destlist_stringdata = destlist_file_data[162:162 + 2 * destlist_lengthstringdata[0]]  # Unocode string data
    Data = destlist_stringdata.decode('utf-16')

    offset = 166 + 2 * destlist_lengthstringdata[0]

    destlist = []
    if destlist_object_timestamp:
        destlist.append([
            destlist_object_timestamp,
            Data,
            str(destlist_entryidnumber[0]),
            str(destlist_entry_access_count[0]),
            destlist_netbiosname,
            destlist_access_time,
            new_mac,
            str(destlist_object_sequence[0]),
            birth_destlist_object_timestamp,
            birth_mac,
        ])

    for entry in range(destlist_totalentries[0] - 1):

        if destlist_entryidnumber[0] > 1:
            destlist_entry_volumeid = destlist_file_data[offset + 8:offset + 24]  # New volume ID
            destlist_volume_identifier = uuid.UUID(bytes_le=destlist_entry_volumeid)

            destlist_entry_objectid = destlist_file_data[offset + 24:offset + 40]  # New Object ID
            destlist_object_identifier = uuid.UUID(bytes_le=destlist_entry_objectid)

            destlist_entry_object_timestamp = struct.unpack("<Q", destlist_file_data[offset + 24:offset + 32])
            destlist_entry_object_timestamp_value = convert_hex(hex(destlist_entry_object_timestamp[0]))
            destlist_entry_object_timestamp = FromFiletime(destlist_entry_object_timestamp_value - 5748192000000000)
            destlist_entry_object_sequence = struct.unpack(">H", destlist_file_data[offset + 32:offset + 34])
            destlist_entry_object_mac1 = struct.unpack(">L", destlist_file_data[offset + 34:offset + 38])
            destlist_entry_object_mac2 = struct.unpack(">H", destlist_file_data[offset + 38:offset + 40])
            destlist_entry_object_mac = convert_mac(hex(destlist_entry_object_mac1[0]) + hex(destlist_entry_object_mac2[0]))

            destlist_entry_volumeid = destlist_file_data[offset + 40:offset + 56]  # Birth volume ID
            destlist_volume_identifier = uuid.UUID(bytes_le=destlist_entry_volumeid)

            destlist_entry_objectid = destlist_file_data[offset + 56:offset + 72]  # Birth Object ID
            destlist_object_identifier = uuid.UUID(bytes_le=destlist_entry_objectid)

            birth_destlist_entry_object_timestamp = struct.unpack("<Q", destlist_file_data[offset + 56:offset + 64])
            birth_destlist_entry_object_timestamp_value = convert_hex(hex(birth_destlist_entry_object_timestamp[0]))
            birth_destlist_entry_object_timestamp = FromFiletime(birth_destlist_entry_object_timestamp_value - 5748192000000000)
            birth_destlist_entry_object_sequence = struct.unpack(">H", destlist_file_data[offset + 64:offset + 66])
            birth_destlist_entry_object_mac1 = struct.unpack(">L", destlist_file_data[offset + 66:offset + 70])
            birth_destlist_entry_object_mac2 = struct.unpack(">H", destlist_file_data[offset + 70:offset + 72])
            birth_destlist_entry_object_mac = convert_mac(hex(birth_destlist_entry_object_mac1[0]) + hex(birth_destlist_entry_object_mac2[0]))

            destlist_netbiosname = destlist_file_data[offset + 72:offset + 88]
            destlist_entry_netbiosname = destlist_netbiosname.decode('ascii')
            destlist_entryidnumber = struct.unpack("<L", destlist_file_data[offset + 88:offset + 92])  # Entry ID number
            destlist_some_test1 = struct.unpack("<Q", destlist_file_data[offset + 92:offset + 100])  # some test
            destlist_entry_last_access_time = struct.unpack("<Q", destlist_file_data[offset + 100:offset + 108])
            lnk_header_access_time = FromFiletime(destlist_entry_last_access_time[0])

            destlist_entrypin_status = struct.unpack("<L", destlist_file_data[offset + 108:offset + 112])  # Entry Pin status
            # print(destlist_entrypin_status[0])

            destlist_some_test2 = struct.unpack("<L", destlist_file_data[offset + 112:offset + 116])
            # print(destlist_some_test2[0])
            destlist_entry_access_count = struct.unpack("<L", destlist_file_data[offset + 116:offset + 120])  # Access Count
            # print("Access Count:",destlist_entry_access_count[0])
            destlist_some_test4 = struct.unpack("<Q", destlist_file_data[offset + 120:offset + 128])
            # print(destlist_some_test4[0])

            destlist_lengthstringdata_new = struct.unpack("<H", destlist_file_data[offset + 128:offset + 130])  # Length of Unicode string data
            # print(destlist_lengthstringdata_new[0])

            offset1 = offset + 130 + 2 * destlist_lengthstringdata_new[0]
            destlist_stringdata = destlist_file_data[offset + 130:offset1]  # Unocode string data
            # print(destlist_stringdata)
            Data = destlist_stringdata.decode('utf-16')
            if destlist_entry_object_timestamp:
                destlist.append([
                    destlist_entry_object_timestamp,
                    Data,
                    str(destlist_entryidnumber[0]),
                    str(destlist_entry_access_count[0]),
                    destlist_netbiosname.decode(),
                    destlist_access_time,
                    destlist_entry_object_mac,
                    str(destlist_entry_object_sequence[0]),
                    birth_destlist_entry_object_timestamp,
                    birth_destlist_entry_object_mac
                ])
            offset = offset1 + 4

    return destlist

