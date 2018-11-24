class BootSector():
    OEM_NAME = 'OEM name'
    BYTES_PER_SECTOR = 'bytes per sector'
    SECTORS_PER_CLUSTER = 'sectors per cluster'
    TOTAL_NUMBER_OF_SECTORS = 'total number of sectors'
    MFT_STARTING_CLUSTER = 'mft starting cluster'
    MFT_MIRROR_STARTING_CLUSTER = 'mft mirror starting cluster'
    MFT_ENTRY_SIZE = 'mft entry size'
    SERIAL_NUMBER = 'serial number'
    CLUSTER_SIZE = 'cluster size'
    SIGNATURE = "Signature"

    def __init__(self, image_name=None, offset_sectors=None, offset_bytes=None, sector_size=512):
        self.image_name = image_name
        if offset_sectors is not None:
            self.offset_bytes = offset_sectors * sector_size
        elif offset_bytes is not None:
            self.offset_bytes = offset_bytes
        else:
            self.offset_bytes = 0

        with open(self.image_name, 'rb') as f:
            f.seek(self.offset_bytes)
            self.data = f.read(512)

    @property
    def oem_name(self):
        return self.data[3:11].decode("unicode-escape")

    @property
    def bytes_per_sector(self):
        return int.from_bytes(self.data[11:13], byteorder='little')

    @property
    def sectors_per_cluster(self):
        return int.from_bytes(self.data[13:14], byteorder='little')

    @property
    def total_number_of_sectors(self):
        return int.from_bytes(self.data[40:48], byteorder='little')

    @property
    def mft_starting_cluster(self):
        return int.from_bytes(self.data[48:56], byteorder='little')

    @property
    def mft_mirror_starting_cluster(self):
        return int.from_bytes(self.data[56:64], byteorder='little')

    @property
    def mft_entry_size(self):
        # val is either:
        #   - positive: it shows the number of clusters that are used for each entry
        #   - negative: it represents the base-2 log of the number of bytes.
        # it's negative when the size of a cluster is larger than a signle MFT entry
        val = int.from_bytes(self.data[64:65], byteorder='little')
        if val > 0:
            return val * self.cluster_size
        else:
            return 2 ** abs(val)

    @property
    def serial_number(self):
        return int.from_bytes(self.data[72:80], byteorder='little')

    @property
    def signature(self):
        return int.from_bytes(self.data[510:512], byteorder='little')

    @property
    def cluster_size(self):
        return self.bytes_per_sector * self.sectors_per_cluster

    @property
    def byte_offset(self):
        return self.offset_bytes

    def all_fields_described(self):
        return (
            (BootSector.OEM_NAME, self.oem_name),
            (BootSector.BYTES_PER_SECTOR, self.bytes_per_sector),
            (BootSector.SECTORS_PER_CLUSTER, self.sectors_per_cluster),
            (BootSector.TOTAL_NUMBER_OF_SECTORS, self.total_number_of_sectors),
            (BootSector.MFT_STARTING_CLUSTER, self.mft_starting_cluster),
            (BootSector.MFT_MIRROR_STARTING_CLUSTER, self.mft_mirror_starting_cluster),
            (BootSector.MFT_ENTRY_SIZE, self.mft_entry_size),
            (BootSector.SERIAL_NUMBER, self.serial_number),
            (BootSector.SIGNATURE, self.signature),
        )

    def getResult(self):
        if self.signature != 43605:
            return False, "This Partition was damaged."
        contents = "Directly taken from the boot sector:\n"
        contents += "-----------------------------------------------------\n"
        for description, value in self.all_fields_described():
            contents += '%-30s%s\n' % (description + ':', value)
        contents += "Derived from the boot sector:\n"
        contents += "-----------------------------------------------------\n"
        contents += '%-30s"%s"' % (BootSector.CLUSTER_SIZE + ':', self.cluster_size)
        return True, contents
