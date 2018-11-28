from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from libs.ParseNTFS import MFT, LogFile, UsnJrnl, AttributeTypeEnum, BootSector
import datetime
from threading import Thread

class NTFSViewer(QWidget):
    USNJRNL = 1
    LOGFILE = 2
    ONLY_SHOW = 1
    ONLY_HIDE = 2
    SIMPLE_SHOW = 3
    CREATE_KEYWORD = "FILE_CREATE"
    DELETE_KEYWORD = "FILE_DELETE"
    EXTEND_KEYWORD = "DATA_EXTEND"
    OVERWRITE_KEYWORD = "DATA_OVERWRITE"

    def __init__(self):
        QWidget.__init__(self)
        from modules.UI.NTFSLogFileDialog import NTFSLogFileDialog
        self.ntfsDialog = NTFSLogFileDialog(self)
        self.ntfsDialog.submitBtn.clicked.connect(self.ready)
        self.selectedBtnNum = 0
        self.isCarvingAllowed = False
        self.usnjrnlTableHeaderItems = ['Timestamp',
                                        'USN',
                                        'File Name',
                                        'Full Path',
                                        'Reason',
                                        'File Attributes',
                                        'Source']
        self.logfileTableHeaderItems = ['LSN',
                                        'Transaction #',
                                        'MFT Modified Time',
                                        'File Name',
                                        'Full Path',
                                        'File Accessed Time',
                                        'Redo Operation',
                                        'Undo Operation',
                                        'Cluster Index',
                                        'Target VCN']
        self.filteringText = {
            "File Create": self.CREATE_KEYWORD,
            "File Delete": self.DELETE_KEYWORD,
            "Data Extend": self.EXTEND_KEYWORD,
            "Data Overwrite": self.OVERWRITE_KEYWORD,
        }

    def ready(self):
        if not self.ntfsDialog.ntfsLogFileChkBox.isChecked() and not self.ntfsDialog.diskRawChkBox.isChecked():
            QMessageBox.information(self, "Help", "Please Select analyzed file type.", QMessageBox.Ok)
            return
        if self.ntfsDialog.diskRawChkBox.isChecked():
            _path = self.ntfsDialog.diskRawTextBox.text()
            if self.ntfsDialog.selectedPartition == -1:
                import os
                disk_size = os.path.getsize(_path)
                if disk_size < 500:
                    QMessageBox.critical(self, "Error", "This is not a disk image file.", QMessageBox.Ok)
                    return

                disk_info = [[_path, str(disk_size)]]
                with open(_path, 'rb') as f:
                    checked = f.read(512)
                    if checked[510:512] != b"\x55\xaa":
                        QMessageBox.critical(self, "Error", "This is not a disk image file.", QMessageBox.Ok)
                        return

                    self.ntfsDialog.diskRawGroupBox.setDisabled(True)
                    f.seek(0x1BE)
                    for i in range(4):
                        partition_info = []
                        partition_table = f.read(16)
                        if partition_table[4:5] == b"\x07":
                            file_system = "NTFS"
                        elif partition_table[4:5] in [b"\x05", b"\x0F"]:
                            file_system = "Extended Partition"
                        else:
                            disk_info.append(None)
                            continue
                        partition_info.append(file_system)

                        active = None
                        if partition_table[0] == "\x80":
                            active = "True"
                        elif partition_table[0] == "\x00":
                            active = "False"
                        else:
                            active = "Unknown"
                        partition_info.append(active)

                        partition_starting_sector = int.from_bytes(partition_table[8:12], byteorder='little')
                        partition_info.append(str(hex(partition_starting_sector * 512)))

                        partition_sector_number = int.from_bytes(partition_table[12:], byteorder='little')
                        partition_info.append(str(partition_sector_number))
                        partition_info.append(str(partition_sector_number * 512))

                        disk_info.append(partition_info)

                self.ntfsDialog.changeInterface(disk_info)
                return
            else:
                partition_starting_offset = self.ntfsDialog.partitionItems[self.ntfsDialog.selectedPartition - 1].text(3)
                self.sector = BootSector(image_name=_path,
                                    offset_sectors=None,
                                    offset_bytes=int(partition_starting_offset, 16),
                                    sector_size=512)
                rst, msg = self.sector.getResult()
                if not rst:
                    QMessageBox.critical(self, "Error", msg, QMessageBox.Ok)
                    return
                else:
                    QMessageBox.information(self, "Help", msg, QMessageBox.Ok)
                self.isCarvingAllowed = True
        elif self.ntfsDialog.ntfsLogFileChkBox.isChecked():
            _path = [
                self.ntfsDialog.mftPathTextBox.text(),
                self.ntfsDialog.usnjrnlPathTextBox.text(),
                self.ntfsDialog.logfilePathTextBox.text()
            ]
            self.ntfsDialog.ntfsLogGroupBox.setDisabled(True)
            self.ntfsDialog.diskRawChkBox.setDisabled(True)
        rst, msg = self.check(_path)
        if rst:
            self.initUI()
            self.ntfsDialog.ready()
            try:
                t = Thread(target=self.load, args=())
                t.start()
            except Exception as e:
                QMessageBox.critical(self, "Error", "{}".format(e), QMessageBox.Ok)
                self.ntfsDialog.accept()
                return
            self.ntfsDialog.barThread.complete.connect(self.showViewer)
        else:
            QMessageBox.critical(self, "Error", msg, QMessageBox.Ok)
            self.ntfsDialog.accept()

    def showViewer(self):
        alertStr = "MFT total entry: {0}\nUsnJrnl total record: {1}\nLogFile total record: {2}\nTransaction total: {3}" \
            .format(len(self.mft.entries), self.usnjrnl_len, self.logfile_len, len(self.logfile.transactions))
        QMessageBox.information(self, "Help", alertStr, QMessageBox.Ok)
        self.ntfsDialog.accept()

        self.exportBar1.setMaximum(self.usnjrnl_len)
        self.exportBar2.setMaximum(self.logfile_len)
        self.exportThread1 = ExportThread(self.usnjrnl.records, self.USNJRNL)
        self.exportThread1.change_value.connect(self.exportBar1.setValue)
        self.exportThread1.exported.connect(self.threadFinished)
        self.exportThread2 = ExportThread(self.logfile.rcrd_records, self.LOGFILE)
        self.exportThread2.change_value.connect(self.exportBar2.setValue)
        self.exportThread2.exported.connect(self.threadFinished)

        if self.isCarvingAllowed:
            self.carvingThread = CarvingThread(self.mft)

        self.showMaximized()

    def check(self, path):
        if self.isCarvingAllowed:
            import os
            dirName = os.getcwd() + "\\NTFS_" + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f") + "\\"
            if not os.path.exists(dirName):
                os.mkdir(dirName)
            self.mft = MFT(image_name=path, boot_sector=self.sector)
            rst, output = self.mft.extract_data(inum=2, output_file=dirName, stream=0, isCarving=False)
            logfile_path = output

            usn_jrnl_inum = self.mft.entries[11]. \
                attributes[AttributeTypeEnum.INDEX_ROOT][0]. \
                entries[AttributeTypeEnum.FILE_NAME]['$UsnJrnl']. \
                file_reference_mft_entry
            rst, output = self.mft.extract_data(inum=usn_jrnl_inum, output_file=dirName, stream=0, isCarving=False)
            usnjrnl_path = output
        else:
            for p in path:
                if not p:
                    return False, "Please import log file."
            self.mft = MFT(image_name=path[0])
            usnjrnl_path = path[1]
            logfile_path = path[2]
        if not self.mft.entries[0].is_valid:
            return False, "Not $MFT file"
        self.usnjrnl = UsnJrnl(usnjrnl_path)
        self.logfile = LogFile(dump_dir="errorpages", file_name=logfile_path)
        return True, None

    def initUI(self):
        self.setWindowTitle("File System Log")

        # Layout
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.optionsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.windowLayout.addLayout(self.optionsLayout)

        # Set up Filtering
        self.groupBox = QGroupBox(self)
        chkLayout = QHBoxLayout()
        self.groupBox.setLayout(chkLayout)
        self.groupBox.setMaximumWidth(860)
        self.createChkBox = QCheckBox('File Create', self)
        self.deleteChkBox = QCheckBox('File Delete', self)
        self.extendChkBox = QCheckBox('Data Extend', self)
        self.overwriteChkBox = QCheckBox("Data Overwrite", self)
        self.createChkBox.stateChanged.connect(lambda: self.filter(self.createChkBox))
        self.deleteChkBox.stateChanged.connect(lambda: self.filter(self.deleteChkBox))
        self.extendChkBox.stateChanged.connect(lambda: self.filter(self.extendChkBox))
        self.overwriteChkBox.stateChanged.connect(lambda: self.filter(self.overwriteChkBox))
        chkLayout.addWidget(self.createChkBox)
        chkLayout.addWidget(self.deleteChkBox)
        chkLayout.addWidget(self.extendChkBox)
        chkLayout.addWidget(self.overwriteChkBox)

        # Set up Button
        self.exportUSNBtn = QPushButton("Export $UsnJrnl as CSV", self)
        self.exportUSNBtn.setFixedSize(200, 40)
        self.exportUSNBtn.setStyleSheet("background-color: darkslategray;")
        self.exportUSNBtn.clicked.connect(self.exportUSN)
        self.exportUSNBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.exportLSNBtn = QPushButton("Export $LogFile as CSV", self)
        self.exportLSNBtn.setFixedSize(200, 40)
        self.exportLSNBtn.setStyleSheet("background-color: darkslategray;")
        self.exportLSNBtn.clicked.connect(self.exportLSN)
        self.exportLSNBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # Set up Text Box for Search
        self.search = QLineEdit(self)
        self.search.setFixedHeight(30)
        self.search.showMaximized()
        self.search.setPlaceholderText("Search...")
        self.search.returnPressed.connect(self.enterPressed)

        # Set up UsnJrnl Table
        self.usnjrnlTable = QTableWidget()
        usnjrnlTableHeader = self.usnjrnlTable.verticalHeader()
        usnjrnlTableHeader.setDefaultSectionSize(28)
        usnjrnlTableHeader.setMaximumSectionSize(28)
        self.usnjrnlTable.setColumnCount(7)
        self.usnjrnlTable.setHorizontalHeaderLabels(self.usnjrnlTableHeaderItems)
        self.usnjrnlTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.usnjrnlTable.verticalHeader().setVisible(False)
        self.usnjrnlTable.cellDoubleClicked.connect(self.showDetail)

        # Set up LogFile Table
        self.logfileTable = QTableWidget()
        logfileTableHeader = self.logfileTable.verticalHeader()
        logfileTableHeader.setDefaultSectionSize(28)
        logfileTableHeader.setMaximumSectionSize(28)
        self.logfileTable.setColumnCount(10)
        self.logfileTable.setHorizontalHeaderLabels(self.logfileTableHeaderItems)
        self.logfileTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.logfileTable.verticalHeader().setVisible(False)

        # Set up Tab Widget
        self.ntfsTabs = QTabWidget()
        self.ntfsTabs.addTab(self.usnjrnlTable, "$UsnJrnl")
        self.ntfsTabs.addTab(self.logfileTable, "$LogFile")
        self.ntfsTabs.currentChanged.connect(self.tabChanged)

        self.optionsLayout.addWidget(self.groupBox)
        self.optionsLayout.addWidget(self.exportUSNBtn, alignment=Qt.AlignBottom)
        self.optionsLayout.addWidget(self.exportLSNBtn, alignment=Qt.AlignBottom)
        self.windowLayout.addWidget(self.search)
        self.windowLayout.addWidget(self.ntfsTabs)
        self.setLayout(self.windowLayout)

        # Export Progress Bar
        self.exportBar1 = QProgressBar(self)
        self.exportBar1.setFixedSize(200, 40)
        self.exportBar1.setAlignment(Qt.AlignCenter)
        self.exportBar1.hide()
        self.exportBar2 = QProgressBar(self)
        self.exportBar2.setFixedSize(200, 40)
        self.exportBar2.setAlignment(Qt.AlignCenter)
        self.exportBar2.hide()

    def tabChanged(self, idx):
        if idx:
            self.groupBox.setDisabled(True)
        else:
            self.groupBox.setDisabled(False)

    def load(self):
        tArr = []
        try:
            tArr.append(Thread(target=self.usnjrnl.parse, args=()))
            tArr.append(Thread(target=self.logfile.parse_all, args=()))

            for t in tArr:
                t.start()
            for t in tArr:
                t.join()

            self.logfile.connect_transactions()

            self.usnjrnl_len = len(self.usnjrnl.records)
            self.logfile_len = len(self.logfile.rcrd_records)

            tArr.clear()
            tArr.append(Thread(target=self.load_usnjrnlTable, args=()))
            tArr.append(Thread(target=self.load_logfileTable, args=()))
            for t in tArr:
                t.start()
            for t in tArr:
                t.join()
            self.exportThread1 = ExportThread(self.usnjrnl.records, NTFSViewer.USNJRNL)
            self.exportThread1.exported.connect(self.threadFinished)
            self.exportThread2 = ExportThread(self.logfile.rcrd_records, NTFSViewer.LOGFILE)
            self.exportThread2.exported.connect(self.threadFinished)
            if self.isCarvingAllowed:
                self.carvingThread = CarvingThread(self.mft)
                self.carvingThread.carved.connect(self.threadFinished)
        except Exception as e:
            raise Exception(e)

        self.ntfsDialog.resume()


    def load_usnjrnlTable(self):
        usn_row = 0
        self.details = []
        for record in self.usnjrnl.records:
            self.usnjrnlTable.insertRow(usn_row)
            detail = []  # [ mft, usn record, logfile transaction ]
            self_entry = self.mft.entries[record.file_reference_mft_entry]
            detail.append(self_entry.detail())

            parent_ref_entry_num = record.parent_file_reference_mft_entry
            if parent_ref_entry_num != record.file_reference_mft_entry:
                full_path = (self.mft.getFullPath(parent_ref_entry_num) + "\\" + record.file_name).replace(".\\","C:\\")
            else:
                if self_entry.is_base_entry:
                    full_path = record.file_name
                else:
                    full_path = "~unknown-ENTRY[{}]\\{}".format(self_entry.inum, record.file_name)
            self.usnjrnlTable.setItem(usn_row, 0, QTableWidgetItem("{}".format(record.timestamp_datetime)))
            self.usnjrnlTable.setItem(usn_row, 1, QTableWidgetItem(str(record.usn)))
            self.usnjrnlTable.setItem(usn_row, 2, QTableWidgetItem(record.file_name))
            self.usnjrnlTable.setItem(usn_row, 3, QTableWidgetItem(full_path))
            self.usnjrnlTable.setItem(usn_row, 4, QTableWidgetItem(record.reason_string))
            self.usnjrnlTable.setItem(usn_row, 5, QTableWidgetItem(record.file_attributes_string))
            self.usnjrnlTable.setItem(usn_row, 6, QTableWidgetItem("OS" if record.source_info else "User"))

            self.usnjrnlTable.item(usn_row, 0).setTextAlignment(Qt.AlignCenter)
            self.usnjrnlTable.item(usn_row, 1).setTextAlignment(Qt.AlignCenter)
            self.usnjrnlTable.item(usn_row, 5).setTextAlignment(Qt.AlignCenter)
            self.usnjrnlTable.item(usn_row, 6).setTextAlignment(Qt.AlignCenter)

            detail.append([
                str(record.usn),
                record.file_name,
                "{}".format(record.timestamp),
                record.reason_string,
                record.file_attributes_string,
            ])

            if self_entry.lsn in self.logfile.transactions.keys():
                transaction = self.logfile.transactions[self_entry.lsn]
                if transaction.contains_usn:
                    for usn in transaction.usns:
                        if usn[1] == record.usn:
                            detail.append([
                                transaction.transaction_num,
                                transaction.all_opcodes,
                            ])
                            for c in range(self.usnjrnlTable.columnCount()):  # Adjust COLOR of Row
                                self.usnjrnlTable.item(usn_row, c).setBackground(QColor(125, 125, 125, 30))

            if self.DELETE_KEYWORD in record.reason_string:
               if record.file_name.endswith(".ps"):
                   self.usnjrnlTable.item(usn_row, c).setBackground(QColor(0, 255, 0, 30))
               elif record.file_name[0] == '~' and record.file_name.endswith(".tmp"):
                   self.usnjrnlTable.item(usn_row, c).setBackground(QColor(0, 125, 255, 30))

            self.details.append(detail)
            usn_row += 1

        self.usnjrnlTable.setColumnWidth(0, 180)
        self.usnjrnlTable.setColumnWidth(1, 90)
        self.usnjrnlTable.setColumnWidth(2, 200)
        self.usnjrnlTable.setColumnWidth(3, 400)
        self.usnjrnlTable.setColumnWidth(4, 180)
        self.usnjrnlTable.setColumnWidth(5, 100)
        self.usnjrnlTable.horizontalHeader().setStretchLastSection(True)


    def load_logfileTable(self):
        log_row = 0
        for rcrd in self.logfile.rcrd_records:
            prev_redo = 0
            prev_undo = 0
            for (lsn_hdr, lsn_data) in rcrd.lsn_entries:
                self.logfileTable.insertRow(log_row)
                self.logfileTable.setItem(log_row, 0, QTableWidgetItem(str(lsn_hdr.this_lsn)))
                self.logfileTable.setItem(log_row, 1, QTableWidgetItem(str(lsn_hdr.transaction_num)))
                try:
                    self_entry = self.mft.entries[lsn_data.deriv_inum]
                    attr = self_entry.attributes[AttributeTypeEnum.FILE_NAME][0]
                    # File Name
                    self.logfileTable.setItem(log_row, 3, QTableWidgetItem(attr.name))
                    # Full Path
                    self.logfileTable.setItem(log_row, 4, QTableWidgetItem(self.mft.getFullPath(self_entry.inum)))
                    # File Accessed Time
                    self.logfileTable.setItem(log_row, 5, QTableWidgetItem(datetime.datetime.strftime(attr.file_access_time_datetime, "%Y-%m-%d %H:%M:%S.%f")))
                    self.logfileTable.item(log_row, 5).setTextAlignment(Qt.AlignCenter)
                except Exception as e:
                    self.logfileTable.setItem(log_row, 3, QTableWidgetItem(""))
                    self.logfileTable.setItem(log_row, 4, QTableWidgetItem(""))
                    self.logfileTable.setItem(log_row, 5, QTableWidgetItem(""))
                try:
                    attr2 = self_entry.attributes[AttributeTypeEnum.STANDARD_INFORMATION][0]
                    # MFT Modified Time
                    self.logfileTable.setItem(log_row, 2, QTableWidgetItem(datetime.datetime.strftime(attr2.mft_altered_time_datetime, "%Y-%m-%d %H:%M:%S.%f")))
                    self.logfileTable.item(log_row, 2).setTextAlignment(Qt.AlignCenter)
                except Exception as e:
                    self.logfileTable.setItem(log_row, 2, QTableWidgetItem(""))
                self.logfileTable.setItem(log_row, 6, QTableWidgetItem(lsn_data.deriv_redo_operation_type))
                self.logfileTable.setItem(log_row, 7, QTableWidgetItem(lsn_data.deriv_undo_operation_type))
                self.logfileTable.setItem(log_row, 8, QTableWidgetItem(str(lsn_data.mft_cluster_index)))
                self.logfileTable.setItem(log_row, 9, QTableWidgetItem(str(lsn_data.target_vcn)))
                self.logfileTable.item(log_row, 1).setTextAlignment(Qt.AlignCenter)
                self.logfileTable.item(log_row, 8).setTextAlignment(Qt.AlignCenter)
                self.logfileTable.item(log_row, 9).setTextAlignment(Qt.AlignCenter)
                if lsn_data.redo_operation == 3 and lsn_data.undo_operation == 2:
                    if prev_redo == 15 and prev_undo == 14:
                        for i in range(self.logfileTable.columnCount()):
                            self.logfileTable.item(log_row-1, i).setBackground(QColor(255, 0, 0, 30))
                            self.logfileTable.item(log_row, i).setBackground(QColor(255, 0, 0, 30))
                prev_redo = lsn_data.redo_operation
                prev_undo = lsn_data.undo_operation
                log_row += 1

        self.logfileTable.resizeColumnsToContents()
        self.logfileTable.setColumnWidth(2, 170)
        self.logfileTable.setColumnWidth(3, 200)
        self.logfileTable.setColumnWidth(4, 400)
        self.logfileTable.setColumnWidth(5, 170)
        self.logfileTable.setColumnWidth(6, 200)
        self.logfileTable.setColumnWidth(7, 200)


    def enterPressed(self):
        keyword = self.search.text()
        if self.ntfsTabs.currentIndex():
            if not keyword:
                for row in range(len(self.details)):
                    if self.logfileTable.isRowHidden(row):
                        self.logfileTable.showRow(row)
                return
            items = self.logfileTable.findItems(keyword, Qt.MatchContains)
            includedRow = [self.logfileTable.row(item) for item in items]
            for row in range(len(self.logfileTable.rowCount())):
                if row in includedRow:
                    self.logfileTable.showRow(row)
                else:
                    self.logfileTable.hideRow(row)
        else:
            if not keyword:
                if self.selectedBtnNum == 0 or self.selectedBtnNum == 4:
                    for i in range(len(self.details)):
                        if self.usnjrnlTable.isRowHidden(i):
                            self.usnjrnlTable.showRow(i)
                else:
                    checkedKeyword = []
                    if self.createChkBox.isChecked():
                        checkedKeyword.append(self.CREATE_KEYWORD)
                    if self.deleteChkBox.isChecked():
                        checkedKeyword.append(self.DELETE_KEYWORD)
                    if self.overwriteChkBox.isChecked():
                        checkedKeyword.append(self.OVERWRITE_KEYWORD)
                    if self.extendChkBox.isChecked():
                        checkedKeyword.append(self.EXTEND_KEYWORD)
                    for i in range(len(self.details)):
                        if self.details[i][1][3] in checkedKeyword:
                            self.usnjrnlTable.showRow(i)
                return
            items = self.usnjrnlTable.findItems(keyword, Qt.MatchContains)
            includedRow = list(set([self.usnjrnlTable.row(item) for item in items]))
            for row in range(len(self.details)):
                if self.usnjrnlTable.isRowHidden(row):
                    continue
                if row in includedRow:
                    self.usnjrnlTable.showRow(row)
                else:
                    self.usnjrnlTable.hideRow(row)

    def filter(self, b):
        if self.ntfsTabs.currentIndex():
            return
        keyword = self.filteringText[b.text()]
        if b.isChecked():
            filterType = self.ONLY_SHOW if self.selectedBtnNum else self.SIMPLE_SHOW
            self.selectedBtnNum += 1
        else:
            self.selectedBtnNum -= 1
            if self.selectedBtnNum:
                filterType = self.ONLY_HIDE
            else:
                keyword = None
                filterType = self.SIMPLE_SHOW

        if filterType == self.ONLY_SHOW:
            for row in range(len(self.details)):
                if keyword in self.details[row][1][3]:
                    self.usnjrnlTable.showRow(row)
        elif filterType == self.ONLY_HIDE:
            for row in range(len(self.details)):
                if keyword in self.details[row][1][3]:
                    self.usnjrnlTable.hideRow(row)
        elif filterType == self.SIMPLE_SHOW:
            if not keyword:
                for row in range(len(self.details)):
                    if self.usnjrnlTable.isRowHidden(row):
                        self.usnjrnlTable.showRow(row)
            else:
                for row in range(len(self.details)):
                    if self.usnjrnlTable.isRowHidden(row):
                        continue
                    if keyword in self.details[row][1][3]:
                        self.usnjrnlTable.showRow(row)
                    else:
                        self.usnjrnlTable.hideRow(row)

    def showDetail(self, row, column):
        from modules.UI.NTFSDetailViewer import NTFSDetailViewer
        self.ntfsDetailViewer = NTFSDetailViewer()
        self.ntfsDetailViewer.initUI(self.details[row])

    def exportUSN(self):
        self.exportUSNBtn.hide()
        self.optionsLayout.replaceWidget(self.exportUSNBtn, self.exportBar1)
        self.exportBar1.show()
        self.exportThread1.start()

    def exportLSN(self):
        self.exportLSNBtn.hide()
        self.optionsLayout.replaceWidget(self.exportLSNBtn, self.exportBar2)
        self.exportBar2.show()
        self.exportThread2.start()

    def threadFinished(self, msg):
        if not self.exportBar1.isHidden():
            self.exportBar1.hide()
            self.optionsLayout.replaceWidget(self.exportBar1, self.exportUSNBtn)
            self.exportUSNBtn.show()
            self.exportBar1.setValue(0)
        if not self.exportBar2.isHidden():
            self.exportBar2.hide()
            self.optionsLayout.replaceWidget(self.exportBar2, self.exportLSNBtn)
            self.exportLSNBtn.show()
            self.exportBar2.setValue(0)
        QMessageBox.question(self, "Help", msg, QMessageBox.Ok)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setCursor(QCursor(Qt.PointingHandCursor))
        copyAction = QAction("Copy")
        carveAction = QAction("Carve")
        menu.addAction(copyAction)
        menu.addAction(carveAction)
        if self.ntfsTabs.currentIndex() or not self.isCarvingAllowed:
            carveAction.setDisabled(True)
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            table = self.logfileTable if self.ntfsTabs.currentIndex() else self.usnjrnlTable
            selected = table.selectedItems()
            if len(selected) == 1:
                copiedStr = selected[0].text()
            else:
                copiedStr = " ".join(currentQTableWidgetItem.text() for currentQTableWidgetItem in selected)
            import pyperclip
            pyperclip.copy(copiedStr)
        elif action == carveAction:
            if self.carvingThread.isCarving:
                return
            import os
            dirName = os.getcwd() + "\\Carving\\"
            if not os.path.exists(dirName):
                os.mkdir(dirName)
            carving_item = []
            overlap_inum = []
            for item in self.usnjrnlTable.selectedItems():
                row = item.row()
                inum = int(self.details[item.row()][0][0])
                if self.mft.entries[inum].is_directory:
                    msg = "This entry-#{} is about directory not a file.".format(inum)
                    QMessageBox.information(self, "Help", msg, QMessageBox.Ok)
                    continue
                fname_in_usn = self.usnjrnlTable.item(row, 2).text()
                fname_in_mft = self.details[row][0][-1]
                mft_names = [attr[0] for attr in fname_in_mft]
                if not fname_in_mft:
                    msg = '[{}] MFT Entry is changed, but want to recover? ' \
                          'This entry-#{} has not $FileName Attribute. ' \
                          'So, It will be saved as temporary name like "MFT_Entry_#43212"'.format(fname_in_usn, inum)
                    reply = QMessageBox.question(self, "Help", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                    output_name = dirName + "MFT_Entry_#43212"
                elif fname_in_usn not in mft_names:
                    msg = 'MFT Entry is changed, but want to recover? ' \
                          'This entry-#{} has names "{}"\n' \
                          'So, It will be saved as temporary name like "{}"'.format(inum, ', '.join(mft_names), mft_names[0])
                    reply = QMessageBox.question(self, "Help", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                    output_name = dirName + mft_names[0]
                else:
                    output_name = dirName + fname_in_usn
                if inum in overlap_inum:
                    continue
                carving_item.append([fname_in_usn, inum, output_name])
                overlap_inum.append(inum)
            self.carvingThread.setItem(carving_item)
            self.carvingThread.start()

class ExportThread(QThread):
    change_value = pyqtSignal(int)
    exported = pyqtSignal(str)

    def __init__(self, records, type):
        QThread.__init__(self)
        self.records = records
        self.type = type

    def run(self):
        import csv, os, datetime
        datetime_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f")
        msg = ''
        self.isExporting = True
        self.cnt = 0
        self.msleep(500)
        if self.type == NTFSViewer.USNJRNL:
            output_file = "{}\\usnjrnl_{}.csv".format(os.getcwd(), datetime_str)
            msg = "Success! - Export $UsnJrnl as CSV"
            if not self.records:
                return
            first = self.records[0]
            with open(output_file, 'w') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(first.formatted_csv_column_headers())
                for record in self.records:
                    csv_writer.writerow(record.formatted_csv())
                    self.cnt += 1
                    self.change_value.emit(self.cnt)
        elif self.type == NTFSViewer.LOGFILE:
            output_file = "{}\\logfile_{}.csv".format(os.getcwd(), datetime_str)
            msg = "Success! - Export $LogFile as CSV"
            if not self.records:
                return
            first_rcrd = self.records[0]
            header = first_rcrd.formatted_csv_column_headers
            header.extend(first_rcrd.lsn_header_csv_columns)
            header.extend(first_rcrd.lsn_data_csv_columns)
            with open(output_file, 'w') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(header)
                for rcrd in self.records:
                    rcrd.export_csv(csv_writer)
                    self.cnt += 1
                    self.change_value.emit(self.cnt)
        self.exported.emit(msg)


class CarvingThread(QThread):
    carved = pyqtSignal(str)

    def __init__(self, mft):
        QThread.__init__(self)
        self.isCarving= False
        self.mft = mft

    def setItem(self, carvedList):
        self.carvedList = carvedList

    def run(self):
        self.isCarving = True
        msg = ''
        fail_cnt = 0
        for item in self.carvedList:
            print(item)
            rst, output = self.mft.extract_data(inum=item[1], output_file=item[2], stream=0, isCarving=True)
            if not rst:
                msg += "{} can't be carved. cause: {}\n".format(item[0], output)
                fail_cnt += 1
        if not fail_cnt:
            msg = "Success All."
        else:
            msg += "Fail: {}/{}".format(fail_cnt, len(self.carvedList))
        self.isCarving = False
        self.carved.emit(msg)