from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from libs.ParseNTFS import MFT, LogFile, UsnJrnl, AttributeTypeEnum
import datetime
from threading import Thread


class NTFSViewer(QWidget):
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
        self.btnNum = 0
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

    def ready(self):
        _path = [
            self.ntfsDialog.mftPathTextBox.text(),
            self.ntfsDialog.usnjrnlPathTextBox.text(),
            self.ntfsDialog.logfilePathTextBox.text()
        ]
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
            self.ntfsDialog.complete.connect(self.showViewer)
        else:
            QMessageBox.critical(self, "Error", msg, QMessageBox.Ok)
            self.ntfsDialog.accept()

    def showViewer(self):
        self.ntfsDialog.accept()
        self.showMaximized()

    def check(self, path):
        for p in path:
            if not p:
                return False, "Please import log file."
        self.mft = MFT(image_name=path[0])
        if not self.mft.mft.is_valid:
            return False, "Not $MFT file"
        self.usnjrnl = UsnJrnl(path[1])
        self.logfile = LogFile(dump_dir="errorpages", file_name=path[2])
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
        self.createChkBox = QCheckBox('File Create', self)
        self.deleteChkBox = QCheckBox('File Delete', self)
        self.extendChkBox = QCheckBox('Data Extend', self)
        self.overwriteChkBox = QCheckBox("Data Overwrite", self)
        self.createChkBox.stateChanged.connect(lambda: self.filtering(self.createChkBox))
        self.deleteChkBox.stateChanged.connect(lambda: self.filtering(self.deleteChkBox))
        self.extendChkBox.stateChanged.connect(lambda: self.filtering(self.extendChkBox))
        self.overwriteChkBox.stateChanged.connect(lambda: self.filtering(self.overwriteChkBox))
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
        self.search.setPlaceholderText("Search")
        self.search.editingFinished.connect(self.enterPressed)

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

        self.optionsLayout.addWidget(self.groupBox)
        self.optionsLayout.addWidget(self.exportUSNBtn, alignment=Qt.AlignBottom)
        self.optionsLayout.addWidget(self.exportLSNBtn, alignment=Qt.AlignBottom)
        self.windowLayout.addWidget(self.search)
        self.windowLayout.addWidget(self.ntfsTabs)
        self.setLayout(self.windowLayout)

    def load(self):
        tArr = []
        try:
            tArr.append(Thread(target=self.mft.parse_all, args=()))
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
        except Exception as e:
            raise Exception(e)
        print("MFT total entry: {}".format(len(self.mft.entries)))
        print("UsnJrnl total record: {}".format(self.usnjrnl_len))
        print("LogFile total record: {}".format(self.logfile_len))
        print("Transaction total: {}".format(len(self.logfile.transactions)))
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
                    print(e)
                    self.logfileTable.setItem(log_row, 3, QTableWidgetItem(""))
                    self.logfileTable.setItem(log_row, 4, QTableWidgetItem(""))
                    self.logfileTable.setItem(log_row, 5, QTableWidgetItem(""))
                try:
                    attr2 = self_entry.attributes[AttributeTypeEnum.STANDARD_INFORMATION][0]
                    # MFT Modified Time
                    self.logfileTable.setItem(log_row, 2, QTableWidgetItem(datetime.datetime.strftime(attr2.mft_altered_time_datetime, "%Y-%m-%d %H:%M:%S.%f")))
                    self.logfileTable.item(log_row, 2).setTextAlignment(Qt.AlignCenter)
                except Exception as e:
                    print(e)
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

        print("log_row: {}".format(log_row))
        self.logfileTable.resizeColumnsToContents()
        self.logfileTable.setColumnWidth(2, 170)
        self.logfileTable.setColumnWidth(3, 200)
        self.logfileTable.setColumnWidth(4, 400)
        self.logfileTable.setColumnWidth(5, 170)
        self.logfileTable.setColumnWidth(6, 200)
        self.logfileTable.setColumnWidth(7, 200)


    def enterPressed(self):
        keyword = self.search.text()
        self.Search(keyword, NTFSViewer.SIMPLE_SHOW)


    def Search(self, keyword, type=None):
        table = self.logfileTable if self.ntfsTabs.currentIndex() else self.usnjrnlTable
        if not keyword:
            for i in range(len(self.details)):
                if table.isRowHidden(i):
                    table.showRow(i)
        else:
            items = table.findItems(keyword, Qt.MatchContains)
            includedRow = list(set([table.row(item) for item in items]))
            if type == NTFSViewer.ONLY_SHOW:
                for i in range(len(self.details)):
                    if i in includedRow:
                        table.showRow(i)
            elif type == NTFSViewer.ONLY_HIDE:
                for i in range(len(self.details)):
                    if i in includedRow:
                        table.hideRow(i)
            elif type == NTFSViewer.SIMPLE_SHOW:
                for i in range(len(self.details)):
                    if i not in includedRow:
                        table.hideRow(i)
                    elif table.isRowHidden(i):
                        table.showRow(i)


    def filtering(self, b):
        msg = b.text()
        if self.ntfsTabs.currentIndex():
            return
        if msg == "File Create":
            if self.createChkBox.isChecked():
                if self.btnNum:
                    self.Search(NTFSViewer.CREATE_KEYWORD, NTFSViewer.ONLY_SHOW)
                else:
                    self.Search(NTFSViewer.CREATE_KEYWORD, NTFSViewer.SIMPLE_SHOW)
                self.btnNum += 1
            else:
                self.btnNum -= 1
                if self.btnNum:
                    self.Search("", NTFSViewer.SIMPLE_SHOW)
                else:
                    self.Search(NTFSViewer.CREATE_KEYWORD, NTFSViewer.ONLY_HIDE)
        elif msg == "File Delete":
            if self.deleteChkBox.isChecked():
                if self.btnNum:
                    self.Search(NTFSViewer.DELETE_KEYWORD, NTFSViewer.ONLY_SHOW)
                else:
                    self.Search(NTFSViewer.DELETE_KEYWORD, NTFSViewer.SIMPLE_SHOW)
                self.btnNum += 1
            else:
                self.btnNum -= 1
                if self.btnNum:
                    self.Search("", NTFSViewer.SIMPLE_SHOW)
                else:
                    self.Search(NTFSViewer.DELETE_KEYWORD, NTFSViewer.ONLY_HIDE)
        elif msg == "Data Extend":
            if self.extendChkBox.isChecked():
                if self.btnNum:
                    self.Search(NTFSViewer.EXTEND_KEYWORD, NTFSViewer.ONLY_SHOW)
                else:
                    self.Search(NTFSViewer.EXTEND_KEYWORD, NTFSViewer.SIMPLE_SHOW)
                self.btnNum += 1
            else:
                self.btnNum -= 1
                if self.btnNum:
                    self.Search("", NTFSViewer.SIMPLE_SHOW)
                else:
                    self.Search("DATA_EXTEND", NTFSViewer.ONLY_HIDE)
        elif msg == "Data Overwrite":
            if self.extendChkBox.isChecked():
                if self.btnNum:
                    self.Search(NTFSViewer.OVERWRITE_KEYWORD, NTFSViewer.ONLY_SHOW)
                else:
                    self.Search(NTFSViewer.OVERWRITE_KEYWORD, NTFSViewer.SIMPLE_SHOW)
                self.btnNum += 1
            else:
                self.btnNum -= 1
                if self.btnNum:
                    self.Search("", NTFSViewer.SIMPLE_SHOW)
                else:
                    self.Search(NTFSViewer.OVERWRITE_KEYWORD, NTFSViewer.ONLY_HIDE)


    def showDetail(self, row, column):
        from modules.UI.NTFSDetailViewer import NTFSDetailViewer
        print(self.details[row])
        self.parent().ntfsDetailViewer = NTFSDetailViewer(self.details[row])


    def exportUSN(self):
        import os, datetime
        datetime_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%F")
        new_path = "{}\\usnjrnl_{}.csv".format(os.getcwd(), datetime_str)
        self.usnjrnl.export_csv(new_path)
        QMessageBox.question(self, "Help", "Success! - Export $UsnJrnl as CSV", QMessageBox.Ok)


    def exportLSN(self):
        import os, datetime
        datetime_str = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%F")
        new_path = "{}\\logfile_{}.csv".format(os.getcwd(), datetime_str)
        self.logfile.export_csv(new_path)
        QMessageBox.question(self, "Help", "Success! - Export $LogFile as CSV", QMessageBox.Ok)

    def contextMenuEvent(self, event):
        import os
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        if not self.ntfsTabs.currentIndex():
            carveAction = menu.addAction("Carve")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            table = self.logfileTable if self.ntfsTabs.currentIndex() else self.usnjrnlTable
            selected = table.selectedItems()
            if len(selected) == 1:
                copiedStr = selected[0].text()
            else:
                copiedStr = " ".join(currentQTableWidgetItem.text() for currentQTableWidgetItem in selected)
            os.system("echo {} | clip".format(copiedStr))
        elif action == carveAction:
            self.carve()

    def carve(self):
        print("carve")
