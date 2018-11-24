from collections import OrderedDict

from .common import AttributeTypeEnum
from .factories import AttributeFactory
from .attributes import StandardInformation, FileName

class MFTEntry():
    SIGNATURE = ('signature', 0, 3)
    OFFSET_TO_FIXUP_ARRAY = ('offset to fixup array', 4, 5)
    NUMBER_OF_ENTRIES_IN_FIXUP_ARRAY = ('number of entries in fixup array', 6, 7)
    LOGFILE_SEQUENCE_NUMBER = ('logfile sequence number', 8, 15)
    SEQUENCE_VALUE = ('sequence value', 16, 17)
    LINK_COUNT = ('link count', 18, 19)
    OFFSET_TO_FIRST_ATTRIBUTE = ('offset to first attribute', 20, 21)
    FLAGS = ('flags', 22, 23)
    USED_SIZE_OF_MFT_ENTRY = ('used size of MFT entry', 24, 27)
    ALLOCATED_SIZE_OF_MFT_ENTRY = ('allocated size of MFT entry', 28, 31)
    FILE_REFERENCE_TO_BASE_RECORD = ('file reference to base record', 32, 39)
    NEXT_ATTRIBUTE_ID = ('next attribute id', 40, 41)

    def __init__(self, inum=None, image_byte_offset=None, data=None, logfile_parse=False):
        self.inum = inum
        self.image_byte_offset = image_byte_offset
        self.data = bytearray(data)
        self._is_valid = self._check_validity()
        self.attributes = OrderedDict()
        self.logfile_parse = logfile_parse
        if not self.is_valid:
            return
        if not self.logfile_parse:
            self._replace_fixup_values()

        attribute_offset = self.first_attribute_offset

        while True:
            if self.data[attribute_offset:attribute_offset + 4] == b'\xff\xff\xff\xff':
                break
            attribute = AttributeFactory.create_attribute(self.data[attribute_offset:])
            type_enum = attribute.header.enum
            if type_enum not in self.attributes.keys():
                self.attributes[type_enum] = []
            self.attributes[type_enum].append(attribute)
            attribute_offset += attribute.header.attribute_length

    def _replace_fixup_values(self):
        fixup_part = self.data[self.fixup_array_offset : self.fixup_array_offset + 2 * self.fixup_array_n_entries]
        for e in range(1, self.fixup_array_n_entries):
            mem_view = memoryview(self.data)
            mem_view[e * 512 - 2 : e * 512] = fixup_part[2 * e : 2 * e + 2]

    def _check_validity(self):
        return True if self.signature == 'FILE' else False

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def signature(self):
        return self.data[0:4].decode()

    @property
    def fixup_array_offset(self):
        return int.from_bytes(self.data[4:6], byteorder='little')

    @property
    def fixup_array_n_entries(self):
        return int.from_bytes(self.data[6:8], byteorder='little')

    @property
    def lsn(self):
        return int.from_bytes(self.data[8:16], byteorder='little')

    @property
    def sequence_value(self):
        return int.from_bytes(self.data[16:18], byteorder='little')

    @property
    def link_count(self):
        return int.from_bytes(self.data[18:20], byteorder='little')

    @property
    def first_attribute_offset(self):
        return int.from_bytes(self.data[20:22], byteorder='little')

    @property
    def flags(self):
        return int.from_bytes(self.data[22:24], byteorder='little')

    @property
    def mft_entry_used_size(self):
        return int.from_bytes(self.data[24:28], byteorder='little')

    @property
    def mft_entry_allocated_size(self):
        return int.from_bytes(self.data[28:32], byteorder='little')

    @property
    def file_reference_to_base_record(self):
        return int.from_bytes(self.data[32:40], byteorder='little')

    @property
    def next_attribute_id(self):
        return int.from_bytes(self.data[40:42], byteorder='little')

    @property
    def is_base_entry(self):
        """Boolean. Is True when it doesn't point to another MFT entry."""
        return not self.file_reference_to_base_record

    @property
    def is_in_use(self):
        """Boolean. Is True when the entry is in use (the 0x01 flag is set)."""
        return bool(self.flags & 1)

    @property
    def is_directory(self):
        """Boolean. Is True when the entry denotes a directory (the 0x02 flag is set)."""
        return bool(self.flags & 2)

    def all_fields_described(self):
        return (
            (MFTEntry.SIGNATURE, self.signature),
            (MFTEntry.OFFSET_TO_FIXUP_ARRAY, self.fixup_array_offset),
            (MFTEntry.NUMBER_OF_ENTRIES_IN_FIXUP_ARRAY, self.fixup_array_n_entries),
            (MFTEntry.LOGFILE_SEQUENCE_NUMBER, self.lsn),
            (MFTEntry.SEQUENCE_VALUE, self.sequence_value),
            (MFTEntry.LINK_COUNT, self.link_count),
            (MFTEntry.OFFSET_TO_FIRST_ATTRIBUTE, self.first_attribute_offset),
            (MFTEntry.FLAGS, self.flags),
            (MFTEntry.USED_SIZE_OF_MFT_ENTRY, self.mft_entry_used_size),
            (MFTEntry.ALLOCATED_SIZE_OF_MFT_ENTRY, self.mft_entry_allocated_size),
            (MFTEntry.FILE_REFERENCE_TO_BASE_RECORD, self.file_reference_to_base_record),
            (MFTEntry.NEXT_ATTRIBUTE_ID, self.next_attribute_id)
        )

    def format_csv(self):
        formatted = [
            self.inum,
            self.file_reference_to_base_record,
            self.signature,
            self.lsn,
            self.sequence_value,
            self.link_count,
            self.is_base_entry,
            self.is_in_use,
            self.is_directory,
            self.mft_entry_used_size,
            self.mft_entry_allocated_size,
            self.file_reference_to_base_record,
            self.next_attribute_id
        ]

        if AttributeTypeEnum.STANDARD_INFORMATION in self.attributes.keys():
            formatted.extend(self.attributes[AttributeTypeEnum.STANDARD_INFORMATION][0].format_csv())
        else:
            formatted.extend(len(StandardInformation.format_csv_column_headers()) * [None])

        if AttributeTypeEnum.FILE_NAME in self.attributes.keys():
            formatted.extend(self.attributes[AttributeTypeEnum.FILE_NAME][0].format_csv())
        else:
            formatted.extend(len(FileName.format_csv_column_headers()) * [None])

        return formatted

    def format_csv_column_headers(self):
        formatted = [
            'inum',
            'base entry',
            MFTEntry.SIGNATURE[0],
            MFTEntry.LOGFILE_SEQUENCE_NUMBER[0],
            MFTEntry.SEQUENCE_VALUE[0],
            MFTEntry.LINK_COUNT[0],
            'is base entry',
            'in use',
            'directory',
            MFTEntry.USED_SIZE_OF_MFT_ENTRY[0],
            MFTEntry.ALLOCATED_SIZE_OF_MFT_ENTRY[0],
            MFTEntry.FILE_REFERENCE_TO_BASE_RECORD[0],
            MFTEntry.NEXT_ATTRIBUTE_ID[0]
        ]

        formatted.extend(StandardInformation.format_csv_column_headers())
        formatted.extend(FileName.format_csv_column_headers())
        return formatted

    def detail(self):
        fileNameAttrList = []
        if AttributeTypeEnum.FILE_NAME in self.attributes.keys():
            FileNameAttrs = self.attributes[AttributeTypeEnum.FILE_NAME]
            for attr in FileNameAttrs:
                fileNameAttrList.append([
                    attr.name,
                    attr.file_creation_time,
                    attr.file_modification_time,
                    attr.mft_modification_time,
                    attr.file_access_time,
                ])
        usnList = None
        if AttributeTypeEnum.STANDARD_INFORMATION in self.attributes.keys():
            usnList = [str(si.usn) for si in self.attributes[AttributeTypeEnum.STANDARD_INFORMATION]]
        return [
            str(self.inum),
            str(self.sequence_value),
            str(self.is_base_entry),
            str(self.is_in_use),
            ', '.join(usnList) if usnList else [],
            str(self.lsn),
            fileNameAttrList,
        ]