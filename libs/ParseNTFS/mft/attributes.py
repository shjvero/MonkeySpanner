from binascii import hexlify
from collections import OrderedDict

from libs.ParseNTFS import filetime_to_datetime, FileAttributesFlag
from .common import _INDENT, _INDENTED_SMALL_BAR, AttributeTypeEnumConverter, AttributeTypeEnum

class Attribute():
    def __init__(self, header=None, data=None, enum=None):
        self.header = header
        self.data = data[:header.attribute_length]
        if self.header.is_resident:
            self.content_data = self.data[
                                self.header.content_offset:
                                self.header.content_offset + self.header.content_size]
        else:
            self.content_data = b''

    @property
    def enum(self):
        return self.header.enum

    def all_fields_described(self):
        return ()

    @property
    def content_data_hex(self):
        return hexlify(self.content_data)


class StandardInformation(Attribute):
    CREATION_TIME = ('creation time', 0, 7)
    FILE_ALTERED_TIME = ('file altered time', 8,15)
    MFT_ALTERED_TIME = ('mft altered time', 16, 23)
    FILE_ACCESSED_TIME = ('file accessed time', 24, 31)
    FLAGS = ('flags', 32, 35)
    MAXIMUM_NUMBER_OF_VERSIONS = ('maximum version of numbers', 36, 39)
    VERSION_NUMBER = ('version number', 40, 43)
    CLASS_ID = ('class id', 44, 47)
    OWNER_ID = ('owner id', 48, 51)
    SECURITY_ID = ('security id', 52, 55)
    QUOTA_CHARGED = ('quota charged', 56, 63)
    USN = ('USN', 64, 71)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_data = self.data[
                            self.header.content_offset:
                            self.header.content_offset + self.header.content_size]
        self.flags_set = FileAttributesFlag(self.flags)

    @property
    def creation_time(self):
        return "{}".format(self.creation_time_datetime)

    @property
    def file_altered_time(self):
        return "{}".format(self.file_altered_time_datetime)

    @property
    def mft_altered_time(self):
        return "{}".format(self.mft_altered_time_datetime)

    @property
    def file_accessed_time(self):
        return "{}".format(self.file_accessed_time_datetime)

    @property
    def flags(self):
        return int.from_bytes(self.content_data[32:36], byteorder='little')

    @property
    def maximum_number_of_versions(self):
        return int.from_bytes(self.content_data[36:40], byteorder='little')

    @property
    def version_number(self):
        return int.from_bytes(self.content_data[40:44], byteorder='little')

    @property
    def class_id(self):
        return int.from_bytes(self.content_data[44:48], byteorder='little')

    @property
    def owner_id(self):
        return int.from_bytes(self.content_data[48:52], byteorder='little')

    @property
    def security_id(self):
        return int.from_bytes(self.content_data[52:56], byteorder='little')

    @property
    def quota_charged(self):
        return int.from_bytes(self.content_data[56:64], byteorder='little')

    @property
    def usn(self):
        return int.from_bytes(self.content_data[64:72], byteorder='little')

    @property
    def creation_time_datetime(self):
        if not hasattr(self, '_creation_time_datetime'):
            self._creation_time_datetime = filetime_to_datetime(self.content_data[0:8])
        return self._creation_time_datetime

    @property
    def file_altered_time_datetime(self):
        if not hasattr(self, '_file_altered_time_datetime'):
            self._file_altered_time_datetime = filetime_to_datetime(self.content_data[8:16])
        return self._file_altered_time_datetime

    @property
    def mft_altered_time_datetime(self):
        if not hasattr(self, '_mft_altered_time_datetime'):
            self._mft_altered_time_datetime = filetime_to_datetime(self.content_data[16:24])
        return self._mft_altered_time_datetime

    @property
    def file_accessed_time_datetime(self):
        if not hasattr(self, '_file_accessed_time_datetime'):
            self._file_accessed_time_datetime = filetime_to_datetime(self.content_data[24:32])
        return self._file_accessed_time_datetime

    @property
    def flags_string(self):
        return '|'.join(self.flags_set.reason_list())

    def all_fields_described(self):
        base_tuple = (
            (StandardInformation.CREATION_TIME, self.creation_time),
            (StandardInformation.FILE_ALTERED_TIME, self.file_altered_time),
            (StandardInformation.MFT_ALTERED_TIME, self.mft_altered_time),
            (StandardInformation.FILE_ACCESSED_TIME,self.file_accessed_time),
            (StandardInformation.FLAGS, self.flags),
            (StandardInformation.MAXIMUM_NUMBER_OF_VERSIONS, self.maximum_number_of_versions),
            (StandardInformation.VERSION_NUMBER, self.version_number),
            (StandardInformation.CLASS_ID, self.class_id)
        )

        if len(self.content_data) == 48:
            return base_tuple
        elif len(self.content_data) == 72:
            return base_tuple + (
                (StandardInformation.OWNER_ID, self.owner_id, self.owner_id_raw),
                (StandardInformation.SECURITY_ID, self.security_id, self.security_id_raw),
                (StandardInformation.QUOTA_CHARGED, self.quota_charged, self.quota_charged_raw),
                (StandardInformation.USN, self.usn, self.usn_raw)
            )
        else:
            raise Exception('StandardInformation is of length ' + str(len(self.content_data)) + ', case unaccounted for')

    @staticmethod
    def format_csv_column_headers():
        return [
            'SI creation time',
            'SI file altered time',
            'SI mft altered time',
            'SI file accessed time',
            'SI flags',
            'SI maximum number of versions',
            'SI version number',
            'SI class id',
            'SI owner id',
            'SI security id',
            'SI quota charged',
            'SI usn'
        ]

    def format_csv(self):
        return [
            self.creation_time,
            self.file_altered_time,
            self.mft_altered_time,
            self.file_accessed_time,
            self.flags_string,
            self.maximum_number_of_versions,
            self.version_number,
            self.class_id,
            self.owner_id,
            self.security_id,
            self.quota_charged,
            self.usn
        ]


class AttributeList(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FileName(Attribute):
    PARENT_DIRECTORY_FILE  = ('parent directory file', 0, 7)
    FILE_CREATION_TIME = ('file creation time', 8, 15)
    FILE_MODIFICATION_TIME = ('file modification time', 16, 23)
    MFT_MODIFICATION_TIME = ('mft modification time', 24, 31)
    FILE_ACCESS_TIME = ('file access time', 32, 39)
    FILE_ALLOCATED_SIZE = ('file allocated size', 40, 47)
    FILE_REAL_SIZE = ('file real size', 48, 55)
    FLAGS = ('flags', 56, 59)
    REPARSE_VALUE = ('reparse value', 60, 63)
    NAME_LENGTH = ('name length', 64, 64)
    NAMESPACE = ('namespace', 65, 65)
    NAME = ('name', 66, '+')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_data = self.data[
                            self.header.content_offset:
                            self.header.content_offset + self.header.content_size]
        self.flags_set = FileAttributesFlag(self.flags)

    @property
    def parent_directory_file_reference(self):
        return hexlify(self.content_data[0:8]).decode()

    @property
    def file_creation_time(self):
        return "{}".format(self.file_creation_time_datetime)

    @property
    def file_modification_time(self):
        return "{}".format(self.file_modification_time_datetime)

    @property
    def mft_modification_time(self):
        return "{}".format(self.mft_modification_time_datetime)

    @property
    def file_access_time(self):
        return "{}".format(self.file_access_time_datetime)

    @property
    def file_allocated_size(self):
        return int.from_bytes(self.content_data[40:48], byteorder='little')

    @property
    def file_real_size(self):
        return int.from_bytes(self.content_data[48:56], byteorder='little')

    @property
    def flags(self):
        return int.from_bytes(self.content_data[56:60], byteorder='little')

    @property
    def reparse_value(self):
        return int.from_bytes(self.content_data[60:64], byteorder='little')

    @property
    def name_length(self):
        return int.from_bytes(self.content_data[64:65], byteorder='little')

    @property
    def namespace(self):
        return int.from_bytes(self.content_data[65:66], byteorder='little')

    @property
    def name(self):
        return self.content_data[66:66+self.name_length*2].decode('utf-16')

    @property
    def parent_directory_file_reference_sequence_number(self):
        return int.from_bytes(self.content_data[6:8], byteorder='little')

    @property
    def parent_directory_file_reference_mft_entry(self):
        return int.from_bytes(self.content_data[0:6], byteorder='little')

    @property
    def file_creation_time_datetime(self):
        try:
            if not hasattr(self, '_file_creation_time_datetime'):
                self._file_creation_time_datetime = filetime_to_datetime(self.content_data[8:16])
            return self._file_creation_time_datetime
        except ValueError:
            return None

    @property
    def file_modification_time_datetime(self):
        try:
            if not hasattr(self, '_file_modification_time_datetime'):
                self._file_modification_time_datetime = filetime_to_datetime(self.content_data[16:24])
            return self._file_modification_time_datetime
        except ValueError:
            return None
    @property
    def mft_modification_time_datetime(self):
        try:
            if not hasattr(self, '_mft_modification_time_datetime'):
                self._mft_modification_time_datetime = filetime_to_datetime(self.content_data[24:32])
            return self._mft_modification_time_datetime
        except ValueError:
            return None
    @property
    def file_access_time_datetime(self):
        try:
            if not hasattr(self, '_file_access_time_datetime'):
                self._file_access_time_datetime = filetime_to_datetime(self.content_data[32:40])
            return self._file_access_time_datetime
        except ValueError:
            return None

    @property
    def flags_string(self):
        return '|'.join(self.flags_set.reason_list())

    def all_fields_described(self):
        return (
            (FileName.PARENT_DIRECTORY_FILE, self.parent_directory_file_reference),
            (FileName.FILE_CREATION_TIME, self.file_creation_time),
            (FileName.FILE_MODIFICATION_TIME, self.file_modification_time),
            (FileName.MFT_MODIFICATION_TIME, self.mft_modification_time),
            (FileName.FILE_ACCESS_TIME, self.file_access_time),
            (FileName.FILE_ALLOCATED_SIZE, self.file_allocated_size),
            (FileName.FILE_REAL_SIZE, self.file_real_size),
            (FileName.FLAGS, self.flags),
            (FileName.REPARSE_VALUE, self.reparse_value),
            (FileName.NAME_LENGTH, self.name_length),
            (FileName.NAMESPACE, self.namespace),
            (FileName.NAME, self.name)
        )

    @staticmethod
    def format_csv_column_headers():
        return [
            'FN file creation time',
            'FN file modification time',
            'FN mft modification time',
            'FN file access time',
            'FN file allocated size',
            'FN file real size',
            'FN flags',
            'FN reparse value',
            'FN name length',
            'FN namespace',
            'FN name',
            'FN pdfme',
            'FN pdfsn'
        ]

    def format_csv(self):
        return [
            self.file_creation_time,
            self.file_modification_time,
            self.mft_modification_time,
            self.file_access_time,
            self.file_allocated_size,
            self.file_real_size,
            self.flags_string,
            self.reparse_value,
            self.name_length,
            self.namespace,
            self.name,
            self.parent_directory_file_reference_mft_entry,
            self.parent_directory_file_reference_sequence_number
        ]


class ObjectID(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VolumeName(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VolumeInformation(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Data(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NodeHeader():
    OFFSET_START_INDEX_ENTRY_LIST   = ('offset start index entry list', 0, 3)
    OFFSET_TO_END_USED_PORTION      = ('offset to end used portion', 4, 7)
    OFFSET_TO_END_ALLOCATION        = ('offset to end allocation', 8,  11)
    FLAGS                           = ('flags', 12, 15)

    def __init__(self, data):
        self.data = data

    @property
    def offset_start_index_entry_list(self):
        return int.from_bytes(self.data[0:4], byteorder='little')

    @property
    def offset_to_end_used_portion(self):
        return int.from_bytes(self.data[4:8], byteorder='little')

    @property
    def offset_to_end_allocation(self):
        return int.from_bytes(self.data[8:12], byteorder='little')

    @property
    def flags(self):
        return int.from_bytes(self.data[12:16], byteorder='little')

    @property
    def has_children(self):
        return bool(self.flags)

    def all_fields_described(self):
        return (
            (NodeHeader.OFFSET_START_INDEX_ENTRY_LIST, self.offset_start_index_entry_list),
            (NodeHeader.OFFSET_TO_END_USED_PORTION, self.offset_to_end_used_portion),
            (NodeHeader.OFFSET_TO_END_ALLOCATION, self.offset_to_end_allocation),
            (NodeHeader.FLAGS, self.flags)
        )


class IndexEntry():
    FIRST_EIGHT             = ('undefined', 0, 7)
    LENGTH_OF_THIS_ENTRY    = ('length of this entry', 8, 9)
    LENGTH_OF_CONTENT       = ('length of content', 10, 11)
    FLAGS                   = ('flags', 12, 15)

    def __init__(self, data):
        # data is possiby larger than this entry + content actually is. We don't know until we parse this entry.
        entry_length = int.from_bytes(data[0:8], byteorder='little')
        self.data = data[0 : entry_length]
        self.content_data = self.data[16 : 16 + self.length_of_content]

    @property
    def first_eight(self):
        return int.from_bytes(self.data[0:8], byteorder='little')

    @property
    def length_of_this_entry(self):
        return int.from_bytes(self.data[8:10], byteorder='little')

    @property
    def length_of_content(self):
        return int.from_bytes(self.data[10:12], byteorder='little')
    @property
    def flags(self):
        return int.from_bytes(self.data[12:16], byteorder='little')

    @property
    def child_node_exists(self):
        return bool(self.flags & 1)

    @property
    def last_entry_in_list(self):
        return bool(self.flags & 2)

    def all_fields_described(self):
        return (
            (self.FIRST_EIGHT, self.first_eight),
            (self.LENGTH_OF_THIS_ENTRY, self.length_of_this_entry),
            (self.LENGTH_OF_CONTENT, self.length_of_content),
            (self.FLAGS, self.flags)
        )


class HeaderStub():
    def __init__(self, attribute_length=None, enum=None):
        self.attribute_length = attribute_length
        self.is_resident = True
        self.content_offset = 0
        self.content_size = attribute_length
        self.attribute_identifier = enum.name
        self.enum = enum

class DirectoryIndexEntry(IndexEntry):
    FIRST_EIGHT = ('mft file reference', 0, 7)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = FileName(header=HeaderStub(attribute_length=self.length_of_content, enum=AttributeTypeEnum.FILE_NAME), data=self.content_data)

    @property
    def file_reference_mft_entry(self):
        return int.from_bytes(self.data[0:6], byteorder='little')

    @property
    def file_reference_sequence_number(self):
        return int.from_bytes(self.data[6:8], byteorder='little')


class IndexRoot(Attribute):
    TYPE_OF_ATTRIBUTE_IN_INDEX      = ('type of attribute in index', 0, 3)
    COLLATION_SORTING_RULE          = ('collation sorting rule', 4, 7)
    SIZE_OF_EACH_RECORD_BYTES       = ('size of each record bytes', 8, 11)
    SIZE_OF_EACH_RECORD_CLUSTERS    = ('size of each record clusters', 12, 12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # content_data is all bytes for this attribute excluding the header.
        self.content_data = self.data[
                    self.header.content_offset:
                    self.header.content_offset + self.header.content_size]
        self.node_header = NodeHeader(self.content_data[16:32])
        self.entries = OrderedDict()

        # More work is needed in case the IndexRoot has children. Skip for now.
        if self.node_header.has_children:
            return

        # The node header starts at offset 16 and calculates from that offset
        offset = 16 + self.node_header.offset_start_index_entry_list

        if self.type_of_attribute_in_index_enum == AttributeTypeEnum.FILE_NAME:
            self.entries[AttributeTypeEnum.FILE_NAME] = OrderedDict()
            more_entries = True
            while offset < self.node_header.offset_to_end_used_portion and more_entries:
                entry = DirectoryIndexEntry(self.content_data[offset :])
                self.entries[AttributeTypeEnum.FILE_NAME][entry.content.name] = entry
                offset += entry.length_of_this_entry
                more_entries = not entry.last_entry_in_list

    @property
    def type_of_attribute_in_index(self):
        return int.from_bytes(self.content_data[0:4], byteorder='little')

    @property
    def collation_sorting_rule(self):
        return int.from_bytes(self.content_data[4:8], byteorder='little')

    @property
    def size_of_each_record_bytes(self):
        return int.from_bytes(self.content_data[8:12], byteorder='little')

    @property
    def size_of_each_record_clusters(self):
        return int.from_bytes(self.content_data[12:13], byteorder='little')

    @property
    def type_of_attribute_in_index_enum(self):
        return AttributeTypeEnumConverter.from_identifier(self.type_of_attribute_in_index)


    def all_fields_described(self):
        return (
            (IndexRoot.TYPE_OF_ATTRIBUTE_IN_INDEX, self.type_of_attribute_in_index),
            (IndexRoot.COLLATION_SORTING_RULE, self.collation_sorting_rule),
            (IndexRoot.SIZE_OF_EACH_RECORD_BYTES, self.size_of_each_record_bytes),
            (IndexRoot.SIZE_OF_EACH_RECORD_CLUSTERS, self.size_of_each_record_clusters)
        ) + (
            (('-- Node header:', '', ''), '', b''),
        ) +self.node_header.all_fields_described()

    def writeout_additional(self, out):
        for vals1 in self.entries.values():
            for vals2 in vals1.values():
                out.write('\n%sEntry\n%s\n' % (_INDENT, _INDENTED_SMALL_BAR))
                for (description, low, high), value, value_raw in vals2.all_fields_described():
                    out.write('%s%-30s | %-5s | %-18s | %s\n' % (
                        _INDENT,
                        description,
                        str(low) + '-' + str(high),
                        value,
                        hexlify(value_raw)))
                out.write('\n')

                for key, value in vals2.extra_pairs():
                    out.write('%s%-50s %s\n' % (
                        _INDENT,
                        key + ':',
                        value))
                out.write('\n')
                vals2.content.writeout_content_parsed(out)


class IndexAllocation(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Bitmap(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReparsePoint(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EAInformation(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EA(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PropertySet(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoggedUtilityStream(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UnknownAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
