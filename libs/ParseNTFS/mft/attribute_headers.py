import math

from binascii import hexlify
from .common import AttributeTypeEnumConverter

class AttributeHeader():
    TYPE_RAW = ('type', 0, 3)
    ATTRIBUTE_LENGTH = ('attribute length', 4, 7)
    NON_RESIDENT_FLAG = ('non-resident flag', 8, 8)
    NAME_LENGTH = ('name length', 9, 9)
    NAME_OFFSET = ('name offset length', 10, 11)
    FLAGS = ('flags', 12, 13)
    ATTRIBUTE_IDENTIFIER = ('attribute identifier', 14, 15)

    def __init__(self, data):
        attribute_length = int.from_bytes(data[4:8], byteorder='little')
        self.data = data[:attribute_length]

    @property
    def type(self):
        return int.from_bytes(self.data[0:4], byteorder='little')

    @property
    def attribute_length(self):
        return int.from_bytes(self.data[4:8], byteorder='little')

    @property
    def non_resident_flag(self):
        return int.from_bytes(self.data[8:9], byteorder='little')

    @property
    def name_length(self):
        return int.from_bytes(self.data[9:10], byteorder='little')

    @property
    def name_offset(self):
        return int.from_bytes(self.data[10:12], byteorder='little')

    @property
    def flags(self):
        return int.from_bytes(self.data[12:14], byteorder='little')

    @property
    def attribute_identifier(self):
        return int.from_bytes(self.data[14:16], byteorder='little')

    @property
    def enum(self):
        return self._enum

    @property
    def is_resident(self):
        return not bool(self.non_resident_flag)

    @property
    def is_non_resident(self):
        return bool(self.non_resident_flag)

    @property
    def name(self):
        return self.data[self.name_offset: self.name_offset + 2 * self.name_length].decode('utf-16')

    ####################################################################################################################
    # Printing

    def all_fields_described(self):
        return (
            (AttributeHeader.TYPE_RAW, self.type),
            (AttributeHeader.ATTRIBUTE_LENGTH, self.attribute_length),
            (AttributeHeader.NON_RESIDENT_FLAG, self.non_resident_flag),
            (AttributeHeader.NAME_LENGTH, self.name_length),
            (AttributeHeader.NAME_OFFSET, self.name_offset),
            (AttributeHeader.FLAGS, self.flags),
            (AttributeHeader.ATTRIBUTE_IDENTIFIER, self.attribute_identifier)
        )


class AttributeHeaderResident(AttributeHeader):
    CONTENT_SIZE = ('content size', 16, 19)
    CONTENT_OFFSET = ('content offset', 20, 21)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum = AttributeTypeEnumConverter.from_identifier(self.type)

    @property
    def content_size(self):
        return int.from_bytes(self.data[16:20], byteorder='little')

    @property
    def content_offset(self):
        return int.from_bytes(self.data[20:22], byteorder='little')

    def all_fields_described(self):
        return super().all_fields_described() + (
            (AttributeHeaderResident.CONTENT_SIZE, self.content_size),
            (AttributeHeaderResident.CONTENT_OFFSET, self.content_offset)
        )


class RunList():
    RUN_OFFSET = 0
    RUN_LENGTH = 1

    def __init__(self, runlist_bytes):
        self.runlist_bytes = runlist_bytes
        self.runs = []
        self._parse()

    def _parse(self):
        current_runlist = self.runlist_bytes
        while len(current_runlist) > 2 and current_runlist[0] >= 0b00000001:
            run_offset_length = (current_runlist[0] & 0b11110000) >> 4
            run_length_length = current_runlist[0] & 0b00001111

            if run_offset_length > 0:
                run_offset_bytes = current_runlist[1 + run_length_length: 1 + run_length_length + run_offset_length]
                run_offset = int.from_bytes(run_offset_bytes, byteorder='little')
                # Check whether the MSB is set, which means that it is signed and therefore negative
                if run_offset_bytes[-1] >= 128:
                    run_offset -= 256 ** len(run_offset_bytes)
            else:
                run_offset = 0
            run_length_bytes = current_runlist[1: 1 + run_length_length]
            run_length = int.from_bytes(run_length_bytes, byteorder='little')
            self.runs.append((run_offset, run_length))
            current_runlist = current_runlist[1 + run_length_length + run_offset_length:]

    @property
    def cleaned_runs(self):
        # In case of a sparse run, skip this one. We don't want to write useless zeros.
        # In some circumstances people choose to include them, because it makes it easier for indexing.
        return [tup for tup in self.runs if tup[self.RUN_OFFSET] != 0]

    def to_real_offset(self, virt_offset, cluster_size=4096):
        """Converts a virtual offset to an actual offset based on the start of the cluster run."""

        offset = 0
        # see in what run the virtual offset resides
        virt_cluster = math.floor(virt_offset / cluster_size)
        virt_cluster_remainder = virt_offset % cluster_size

        # Go through all runs, each time either returning the right location or progressing further looking for it.
        for run_offset, run_length in self.cleaned_runs:
            if virt_cluster >= run_length:
                # the offset we're looking for is beyond this run.
                offset += run_offset
                virt_cluster -= run_length
            else:
                # The virtual byte offset is in this run. Determine the exact offset.
                offset += run_offset + virt_cluster
                return offset * cluster_size + virt_cluster_remainder


class AttributeHeaderNonResident(AttributeHeader):
    RUNLIST_STARTING_VCN = ('runlist starting VCN', 16, 23)
    RUNLIST_ENDING_VCN = ('runlist ending VCN', 24, 31)
    RUNLIST_OFFSET = ('runlist offset', 32, 33)
    COMPRESSION_UNIT_SIZE = ('compression unit size', 34, 35)
    ATTRIBUTE_CONTENT_ALLOCATED_SIZE = ('attribute content allocated size', 40, 47)
    ATTRIBUTE_CONTENT_ACTUAL_SIZE = ('attribute content actual size', 48, 55)
    ATTRIBUTE_CONTENT_INITIALIZED_SIZE = ('attribute content initialized size', 56, 63)
    RUNLIST = ('runlist', '?', '+')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum = AttributeTypeEnumConverter.from_identifier(self.type)
        self.runlist_raw = self.data[self.runlist_offset: self.runlist_offset + self.attribute_length]
        self.runlist_extended = RunList(self.runlist_raw)

    @property
    def runlist_starting_vcn(self):
        return int.from_bytes(self.data[16:24], byteorder='little')

    @property
    def runlist_ending_vcn(self):
        return int.from_bytes(self.data[24:32], byteorder='little')  # self.data[16:24]

    @property
    def runlist_offset(self):
        return int.from_bytes(self.data[32:34], byteorder='little')

    @property
    def compression_unit_size(self):
        # not checked yet if this is correct. see blz 257
        return int.from_bytes(self.data[34:36], byteorder='little')

    @property
    def attribute_content_allocated_size(self):
        return int.from_bytes(self.data[40:48], byteorder='little')

    @property
    def attribute_content_actual_size(self):
        return int.from_bytes(self.data[48:56], byteorder='little')

    @property
    def attribute_content_initialized_size(self):
        return int.from_bytes(self.data[56:64], byteorder='little')

    @property
    def runlist(self):
        return hexlify(self.runlist_raw).decode()

    def all_fields_described(self):
        return super().all_fields_described() + (
            (AttributeHeaderNonResident.RUNLIST_STARTING_VCN, self.runlist_starting_vcn),
            (AttributeHeaderNonResident.RUNLIST_ENDING_VCN, self.runlist_ending_vcn),
            (AttributeHeaderNonResident.RUNLIST_OFFSET, self.runlist_offset),
            (AttributeHeaderNonResident.COMPRESSION_UNIT_SIZE, self.compression_unit_size),
            (AttributeHeaderNonResident.ATTRIBUTE_CONTENT_ALLOCATED_SIZE, self.attribute_content_allocated_size),
            (AttributeHeaderNonResident.ATTRIBUTE_CONTENT_ACTUAL_SIZE, self.attribute_content_actual_size),
            (AttributeHeaderNonResident.ATTRIBUTE_CONTENT_INITIALIZED_SIZE, self.attribute_content_initialized_size),
            (AttributeHeaderNonResident.RUNLIST, self.runlist)
        )
