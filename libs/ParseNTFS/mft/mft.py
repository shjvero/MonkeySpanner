from collections import OrderedDict
import os, sys, csv
from .factories import AttributeTypeEnum
from .mft_entry import MFTEntry
from .attribute_headers import RunList

class MFT():
    MFT = 0

    def __init__(self, image_name=None):
        self.image_name = image_name
        self.mft_file_size = os.path.getsize(self.image_name)
        self.mft_offset_bytes = 0
        self.mft_entry_size = 0
        self.offset_of_mft_entry_size = 28
        self.entries = OrderedDict()
        self.invalid_entries = OrderedDict()
        self.mft = self._parse_mft()
        self.entries[0] = self.mft

    def _parse_mft(self):
        with open(self.image_name, 'rb') as f:
            f.seek(self.offset_of_mft_entry_size)
            self.mft_entry_size = int.from_bytes(f.read(4), byteorder='little')
            f.seek(self.mft_offset_bytes)
            self.mft_offset_bytes += self.mft_entry_size
            return MFTEntry(inum=0, data=f.read(self.mft_entry_size))

    def parse_all(self, num=None):
        with open(self.image_name, 'rb') as f:
            mft = MFTEntry(inum=0, image_byte_offset=self.mft_offset_bytes, data=f.read(self.mft_entry_size))
            self.mft_offset_bytes += self.mft_entry_size

            inum = 1
            while self.mft_offset_bytes < self.mft_file_size:
                entry = MFTEntry(inum=inum,
                                image_byte_offset=self.mft_offset_bytes,
                                data=f.read(self.mft_entry_size))
                if entry.is_valid:
                    self.entries[inum] = entry
                else:
                    self.invalid_entries[inum] = entry
                inum += 1
                self.mft_offset_bytes += self.mft_entry_size


    def getFullPath(self, entry_num):
        MFT_ENTRY = self.entries[entry_num]
        if AttributeTypeEnum.FILE_NAME in MFT_ENTRY.attributes.keys():
            Attr_FileName = MFT_ENTRY.attributes[AttributeTypeEnum.FILE_NAME][0]
            parent_mft_entry_num = Attr_FileName.parent_directory_file_reference_mft_entry
            if parent_mft_entry_num == entry_num:
                return Attr_FileName.name
            return self.getFullPath(parent_mft_entry_num) + "\\" + Attr_FileName.name
        else:
            print("Not Found Attribute.FILE_NAME")
        return "Not_Found_MFT-ENTRY[{}]".format(entry_num)

    def export_parsed(self, inum_range=None, export_file=None):
        if inum_range:
            iterator = inum_range.iterate
        else:
            iterator = self.entries.keys()        # 1) Write to file. Open file and pass descriptor
        if export_file:
            with open(export_file, 'w') as f:
                for inum in iterator:
                    self.entries[inum].writeout_parsed(f)
        # 2) To stdout. Pass sys.stdout
        else:
            for inum in iterator:
                self.entries[inum].writeout_parsed(sys.stdout)

    def export_csv(self, inum_range=None, export_file=None):
        formatted_columns = []
        if inum_range:
            iterator = inum_range.iterate
        else:
            iterator = self.entries.keys()
        # Any MFTEntry object will do, we just have easy access to MFT's own entry.
        formatted_columns.extend(self.mft.format_csv_column_headers())

        # 1) Write to file. Open file and pass descriptor
        if export_file:
            with open(export_file, 'w') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(formatted_columns)
                for inum in iterator:
                    formatted = []
                    formatted.extend(self.entries[inum].format_csv())
                    csv_writer.writerow(formatted)
        # 2) To stdout. Pass sys.stdout
        else:
            csv_writer = csv.writer(sys.stdout)
            csv_writer.writerow(formatted_columns)
            for inum in iterator:
                formatted = []
                formatted.extend(self.entries[inum].format_csv())
                csv_writer.writerow(formatted)
    
    def max_inum(self):
        return max(self.entries.keys(), key=int)

    def print_statistics(self):
        print('%-20s %s' % ('Maxinum inum:', str(self.max_inum())))
        print('%-20s %s' % ('MFT entries:', str(len([entry for entry in self.entries if entry is not None]))))

    def output_name_mappings(self):
        for entry in self.entries.values():
            if AttributeTypeEnum.FILE_NAME in entry.attributes.keys():
                print('%-6d %s' % (entry.inum, entry.attributes[AttributeTypeEnum.FILE_NAME][0].name))


