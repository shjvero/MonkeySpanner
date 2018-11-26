import logging
import datetime
from collections import namedtuple

from libs.ParseRegistry import Registry
from libs.ParseRegistry.RegistryParse import parse_windows_timestamp as _parse_windows_timestamp

g_logger = logging.getLogger("amcache")
Field = namedtuple("Field", ["name", "getter"])

def make_value_getter(value_name):
    """ return a function that fetches the value from the registry key """

    def _value_getter(key):
        try:
            return key.value(value_name).value()
        except Registry.RegistryValueNotFoundException:
            return None

    return _value_getter


def make_windows_timestamp_value_getter(value_name):
    """
    return a function that fetches the value from the registry key
      as a Windows timestamp.
    """
    f = make_value_getter(value_name)

    def _value_getter(key):
        try:
            return parse_windows_timestamp(f(key) or 0)
        except ValueError:
            return datetime.datetime.min

    return _value_getter


def parse_unix_timestamp(qword):
    return datetime.datetime.utcfromtimestamp(qword)


def parse_windows_timestamp(qword):
    try:
        return _parse_windows_timestamp(qword)
    except ValueError:
        return datetime.datetime.min
    except Exception as e:
        print(e)
        return datetime.datetime.min

def make_unix_timestamp_value_getter(value_name):
    """
    return a function that fetches the value from the registry key
      as a UNIX timestamp.
    """
    f = make_value_getter(value_name)

    def _value_getter(key):
        try:
            return parse_unix_timestamp(f(key) or 0)
        except ValueError:
            return datetime.datetime.min

    return _value_getter


UNIX_TIMESTAMP_ZERO = parse_unix_timestamp(0)
WINDOWS_TIMESTAMP_ZERO = parse_windows_timestamp(0)

# via: http://www.swiftforensics.com/2013/12/amcachehve-in-windows-8-goldmine-for.html
# Product Name    UNICODE string
# ==============================================================================
# 0   Product Name    UNICODE string
# 1   Company Name    UNICODE string
# 2   File version number only    UNICODE string
# 3   Language code (1033 for en-US)  DWORD
# 4   SwitchBackContext   QWORD
# 5   File Version    UNICODE string
# 6   File Size (in bytes)    DWORD
# 7   PE Header field - SizeOfImage   DWORD
# 8   Hash of PE Header (unknown algorithm)   UNICODE string
# 9   PE Header field - Checksum  DWORD
# a   Unknown QWORD
# b   Unknown QWORD
# c   File Description    UNICODE string
# d   Unknown, maybe Major & Minor OS version DWORD
# f   Linker (Compile time) Timestamp DWORD - Unix time
# 10  Unknown DWORD
# 11  Last Modified Timestamp FILETIME
# 12  Created Timestamp   FILETIME
# 15  Full path to file   UNICODE string
# 16  Unknown DWORD
# 17  Last Modified Timestamp 2   FILETIME
# 100 Program ID  UNICODE string
# 101 SHA1 hash of file


# note: order here implicitly orders CSV column ordering cause I'm lazy
FIELDS = [
    Field("Source_Key_Timestamp", lambda key: key.timestamp()),
    Field("Path", make_value_getter("15")),
    Field("SHA1", make_value_getter("101")),
    Field("Size", make_value_getter("6")),
    Field("File_Description", make_value_getter("c")),
    Field("Created_Time", make_windows_timestamp_value_getter("12")),
    Field("Modified_Time", make_windows_timestamp_value_getter("11")),
    Field("Modified_Time2", make_windows_timestamp_value_getter("17")),
    Field("Linker_Time", make_unix_timestamp_value_getter("f")),
    Field("Product", make_value_getter("0")),
    Field("Company", make_value_getter("1")),
    Field("PE_Size_of_Image", make_value_getter("7")),
    Field("Version_Number", make_value_getter("2")),
    Field("Version", make_value_getter("5")),
    Field("Language", make_value_getter("3")),
    Field("Header_Hash", make_value_getter("8")),
    Field("PE_Checksum", make_value_getter("9")),
    Field("ID", make_value_getter("100")),
    Field("SwitchBackContext", make_value_getter("4")),
]

def get(path):
    try:
        reg = Registry.Registry(path)
        volumes = reg.open("Root\\File")
    except Registry.RegistryKeyNotFoundException as e:
        return False, "{}".format(e)

    contents = []
    for volumekey in volumes.subkeys():
        for filekey in volumekey.subkeys():
            contents.append(["{}".format(e.getter(filekey)) for e in FIELDS])

    from operator import itemgetter
    return True, sorted(contents, key=itemgetter(0))