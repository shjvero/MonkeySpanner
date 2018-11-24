from collections import OrderedDict
import os, sys, csv
from .factories import AttributeTypeEnum
from .mft_entry import MFTEntry
from .attribute_headers import RunList


class MFT():
    MFT = 0

    def __init__(self, image_name=None, boot_sector=None):
        self.image_name = image_name
        self.isSingleFile = False if boot_sector else True
        self.mft_offset_bytes = boot_sector.byte_offset + boot_sector.mft_starting_cluster * boot_sector.cluster_size if boot_sector else 0
        self.partition_offset_bytes = boot_sector.byte_offset if boot_sector else 0
        self.sector_size = boot_sector.bytes_per_sector if boot_sector else 512
        self.cluster_size = boot_sector.cluster_size if boot_sector else 4096
        self.mft_entry_size = 1024  # boot_sector.mft_entry_size
        self.entries = OrderedDict()
        self.invalid_entries = OrderedDict()
        self.parse_all()

    def parse_all(self, num=None):
        if self.isSingleFile:
            self.mft_file_size = os.path.getsize(self.image_name)
            with open(self.image_name, 'rb') as f:
                inum = 0
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
            return

        with open(self.image_name, 'rb') as f:
            f.seek(self.mft_offset_bytes)

            mft = MFTEntry(inum=0, image_byte_offset=self.mft_offset_bytes, data=f.read(self.mft_entry_size))
            mft_runs = mft.attributes[AttributeTypeEnum.DATA][0].header.runlist_extended.cleaned_runs

            inum = 0

            run = mft_runs[0]
            offset = run[RunList.RUN_OFFSET] * self.cluster_size
            length = run[RunList.RUN_LENGTH]

            for run_index in range(len(mft_runs)):
                if run_index:
                    run = mft_runs[run_index]
                    offset = offset + run[RunList.RUN_OFFSET] * self.cluster_size
                    length = run[RunList.RUN_LENGTH]

                f.seek(self.partition_offset_bytes + offset)

                n_entries = int(length * self.cluster_size / self.mft_entry_size)

                for i in range(n_entries):
                    entry = MFTEntry(inum=inum,
                                     image_byte_offset=self.partition_offset_bytes + offset + i * self.cluster_size,
                                     data=f.read(self.mft_entry_size))
                    if entry.is_valid:
                        self.entries[inum] = entry
                    else:
                        self.invalid_entries[inum] = entry
                    inum += 1
                    if inum == num:
                        break

    def max_inum(self):
        return max(self.entries.keys(), key=int)

    # Added
    def parse_inum(self, inum):
        runlist = self.entries[0].attributes[AttributeTypeEnum.DATA][0].header.runlist_extended
        with open(self.image_name, 'rb') as f:
            image_byte_offset = self.partition_offset_bytes + runlist.to_real_offset(inum * self.mft_entry_size,
                                                                                     cluster_size=self.cluster_size)
            f.seek(image_byte_offset)
            entry = MFTEntry(inum=inum, image_byte_offset=image_byte_offset, data=f.read(self.mft_entry_size))
            self.entries[inum] = entry

    def parse_inums(self, inum_range=None):
        runlist = self.entries[0].attributes[AttributeTypeEnum.DATA][0].header.runlist_extended
        with open(self.image_name, 'rb') as f:
            for first, last in inum_range.ranges:
                for inum in range(first, last + 1):
                    image_byte_offset = self.partition_offset_bytes + runlist.to_real_offset(inum * self.mft_entry_size,
                                                                                             cluster_size=self.cluster_size)
                    f.seek(image_byte_offset)
                    entry = MFTEntry(inum=inum, image_byte_offset=image_byte_offset, data=f.read(self.mft_entry_size))
                    self.entries[inum] = entry
                    image_byte_offset += self.mft_entry_size

    def extract_data(self, inum=None, output_file=None, stream=None, isCarving=False):
        if not self.entries[inum].is_valid:
            return False, "{}st MFT Entry is not valid.".format(inum)

        if AttributeTypeEnum.DATA not in self.entries[inum].attributes.keys():
            return False, "{}st MFT Entry hasn't $DATA Attribute.".format(inum)

        data_stream = self.entries[inum].attributes[AttributeTypeEnum.DATA][stream]
        if not isCarving:
            if AttributeTypeEnum.FILE_NAME not in self.entries[inum].attributes.keys():
                output_file += "MFT_Entry_#{}".format(inum)
            else:
                output_file += self.entries[inum].attributes[AttributeTypeEnum.FILE_NAME][0].name

        with open(self.image_name, 'rb') as in_file, open(output_file, 'wb') as out_file:
            if data_stream.header.is_resident:
                self.extract_resident_data(attr=data_stream, out=out_file)
            else:
                rst, msg = self.extract_non_resident_data(attr=data_stream, in_file=in_file, out_file=out_file)
                if not rst:
                    return rst, msg
        return True, output_file

    def extract_resident_data(self, attr=None, out=None):
        out.write(attr.content_data)

    def extract_non_resident_data(self, attr=None, in_file=None, out_file=None):
        runs = attr.header.runlist_extended.cleaned_runs
        if not runs:
            return False, '"{}" is non_resident, but has not Cluster Run List.'.format(out_file)
        prev_offset = self.partition_offset_bytes
        for offset, length in runs:
            in_file.seek(prev_offset + offset * self.cluster_size, os.SEEK_SET)
            prev_offset = in_file.tell()
            out_file.write(in_file.read(length * self.cluster_size))
        return True, None

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