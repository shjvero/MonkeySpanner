from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import *
from libs.ParseNTFS import MFT, LogFile, UsnJrnl, AttributeTypeEnum
import datetime

class NTFSViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.w = self.width()
        self.h = self.height()
        self.usnjrnlTableHeaderItems = ['Timestamp',
                                        'USN',
                                        'File Name',
                                        'Full Path',
                                        'Reason',
                                        'File Attributes',
                                        'Source Info']
        self.logfileTableHeaderItems = ['LSN',
                                        'Type',
                                        'Redo Operation',
                                        'Undo Operation',
                                        'File Name',
                                        'Full Path',
                                        'Created Time',
                                        'Modified Time',
                                        'MFT Modified Time',
                                        'Accessed Time',
                                        'Cluster Index',
                                        'Target VCN']
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File System Log")
        self.setMinimumSize(self.w, self.h)

        # Layout
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.optionsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.windowLayout.addLayout(self.optionsLayout)

        # Set up Filtering
        self.groupBox = QGroupBox(self)
        chkLayout = QHBoxLayout()
        self.groupBox.setLayout(chkLayout)
        self.allChkBox = QCheckBox('ALL', self)
        self.createChkBox = QCheckBox('File Create', self)
        self.modifiyChkBox = QCheckBox('File Modifiy', self)
        self.deleteChkBox = QCheckBox('File Delete', self)
        self.allChkBox.stateChanged.connect(lambda: self.filtering(self.allChkBox))
        self.createChkBox.stateChanged.connect(lambda: self.filtering(self.createChkBox))
        self.modifiyChkBox.stateChanged.connect(lambda: self.filtering(self.modifiyChkBox))
        self.deleteChkBox.stateChanged.connect(lambda: self.filtering(self.deleteChkBox))
        chkLayout.addWidget(self.allChkBox)
        chkLayout.addWidget(self.createChkBox)
        chkLayout.addWidget(self.modifiyChkBox)
        chkLayout.addWidget(self.deleteChkBox)

        # Set up Button
        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.setFixedSize(120, 40)
        self.exportBtn.setStyleSheet("background-color: darkslategray;")
        self.exportBtn.clicked.connect(self.export)
        self.exportBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.carveBtn = QPushButton("Carving", self)
        self.carveBtn.setFixedSize(120, 40)
        self.carveBtn.setStyleSheet("background-color: darkslategray;")
        self.carveBtn.clicked.connect(self.carve)
        self.carveBtn.setCursor(QCursor(Qt.PointingHandCursor))

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
        self.logfileTable.setColumnCount(7)
        self.logfileTable.setHorizontalHeaderLabels(self.logfileTableHeaderItems)
        self.logfileTable.horizontalHeader().setStretchLastSection(True)
        self.logfileTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.logfileTable.verticalHeader().setVisible(False)

        # Set up Tab Widget
        self.ntfsTabs = QTabWidget()
        self.ntfsTabs.addTab(self.usnjrnlTable, "$UsnJrnl")
        self.ntfsTabs.addTab(self.logfileTable, "$LogFile")

        self.optionsLayout.addWidget(self.groupBox)
        self.optionsLayout.addWidget(self.exportBtn, alignment=Qt.AlignBottom)
        self.optionsLayout.addWidget(self.carveBtn, alignment=Qt.AlignBottom)
        self.windowLayout.addWidget(self.search)
        self.windowLayout.addWidget(self.ntfsTabs)
        self.setLayout(self.windowLayout)

    def check(self, path):
        import os
        dump_dir = os.getcwd() + "\\errorpages"
        try:
            self.mft = MFT(image_name=path[0])
            self.usnjrnl = UsnJrnl(path[1])
            self.logfile = LogFile(dump_dir=dump_dir, file_name=path[2])
        except Exception as e:
            return False, "{}".format(e)
        return True, None

    def load(self):
        from threading import Thread
        tArr = []
        tArr.append(Thread(target=self.mft.parse_all, args=()))
        tArr.append(Thread(target=self.usnjrnl.parse, args=()))
        tArr.append(Thread(target=self.logfile.parse_all, args=()))

        for t in tArr:
            t.start()

        for t in tArr:
            t.join()

        self.logfile.connect_transactions()

        self.details = []
        row = 0
        self.usnjrnlTable.setRowCount(len(self.usnjrnl.records))
        self.logfileTable.setRowCount(len(self.logfile.rcrd_records))
        for record in self.usnjrnl.records:
            detail = []  # [ mft, usn record, logfile transaction ]
            self_entry = self.mft.entries[record.file_reference_mft_entry]
            detail.append(self_entry.detail())

            parent_ref_entry_num = record.parent_file_reference_mft_entry
            if parent_ref_entry_num != record.file_reference_mft_entry:
                full_path = (self.mft.getFullPath(parent_ref_entry_num) + "\\" + record.file_name).replace(".\\", "C:\\")
            else:
                if self_entry.is_base_entry:
                    full_path = record.file_name
                else:
                    full_path = "~unknown-ENTRY[{}]\\{}".format(self_entry.inum, record.file_name)

            self.usnjrnlTable.setItem(row, 0, QTableWidgetItem("{}".format(record.timestamp_datetime)))
            self.usnjrnlTable.setItem(row, 1, QTableWidgetItem(str(record.usn)))
            self.usnjrnlTable.setItem(row, 2, QTableWidgetItem(record.file_name))
            self.usnjrnlTable.setItem(row, 3, QTableWidgetItem(full_path))
            self.usnjrnlTable.setItem(row, 4, QTableWidgetItem(record.reason_string))
            self.usnjrnlTable.setItem(row, 5, QTableWidgetItem(record.file_attributes_string))
            self.usnjrnlTable.setItem(row, 6, QTableWidgetItem("OS" if record.source_info else "User"))

            self.usnjrnlTable.item(row, 0).setTextAlignment(Qt.AlignCenter)
            self.usnjrnlTable.item(row, 1).setTextAlignment(Qt.AlignCenter)
            self.usnjrnlTable.item(row, 6).setTextAlignment(Qt.AlignCenter)

            detail.append([
                "{}".format(record.timestamp),
                str(record.usn),
                record.file_name,
                full_path,
                record.reason_string,
                record.file_attributes_string,
                record.source_info,
            ])

            # if record.parent_file_reference_sequence_number == self_entry.sequence_value:
            if self_entry.lsn in self.logfile.transactions.keys():
                transaction = self.logfile.transactions[self_entry.lsn]
                if transaction.contains_usn:
                    for usn in transaction.usns:
                        if usn[1] == record.usn:
                            # for lsn, redo_op, undo_op in transaction.all_opcodes:
                            #     print(lsn, redo_op, undo_op)
                            detail.append([
                                transaction.transaction_num,
                                transaction.all_opcodes,
                            ])
                            for c in range(self.usnjrnlTable.columnCount()):  # Adjust COLOR of Row
                                self.usnjrnlTable.item(row, c).setBackground(QColor(125, 125, 125, 30))
            self.details.append(detail)
            row += 1

        self.usnjrnlTable.horizontalHeader().setStretchLastSection(True)
        self.usnjrnlTable.resizeColumnsToContents()
        self.usnjrnlTable.setColumnWidth(1, 100)
        self.usnjrnlTable.setColumnWidth(2, 150)
        self.usnjrnlTable.setColumnWidth(3, 400)
        self.usnjrnlTable.setColumnWidth(4, 300)
        self.usnjrnlTable.setColumnWidth(5, 150)


        # LogFile


        print("MFT total entry: {}".format(len(self.mft.entries)))
        print("UsnJrnl total record: {}".format(len(self.usnjrnl.records)))
        print("LogFile total record: {}".format(len(self.logfile.rcrd_records)))
        print("Transaction total: {}".format(len(self.logfile.transactions)))
        self.show()

    def enterPressed(self):
        print(self.ntfsTabs.currentIndex())
        keyword = self.search.text()
        print(keyword)

        if self.ntfsTabs.currentIndex() == 0:   # UsnJrnl Tab
            if not keyword:
                for i in range(len(self.details)):
                    if self.usnjrnlTable.isRowHidden(i):
                        self.usnjrnlTable.showRow(i)
            else:
                items = self.usnjrnlTable.findItems(keyword, Qt.MatchContains)
                includedRow = list(set([self.usnjrnlTable.row(item) for item in items]))
                for i in range(len(self.details)):
                    if i not in includedRow:
                        self.usnjrnlTable.hideRow(i)
                    elif self.usnjrnlTable.isRowHidden(i):
                        self.usnjrnlTable.showRow(i)
            return
        else:   # LogFile Tab
            print()

    def filtering(self, b):
        msg = b.text()
        print(msg)

    def showDetail(self, row, column):
        from modules.UI.NTFSDetailViewer import NTFSDetailViewer
        self.viewer = NTFSDetailViewer(self.details[row])

    def export(self):
        print(self.exportBtn.text())

    def carve(self):
        print(self.carveBtn.text())

if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = NTFSViewer()
    dir_path = "C:\\Users\\asdzx\\Desktop\\ntfs_parse\\sample\\"
    _path = [
        dir_path + "MFT",
        dir_path + "usnjrnl",
        dir_path + "LogFile",
    ]
    rst, msg = w.check(_path)
    if rst:
        w.load()
        # w.resume()
        w.show()
    sys.exit(app.exec_())