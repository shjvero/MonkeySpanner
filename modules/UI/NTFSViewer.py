from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *


class NTFSViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.w = self.width()
        self.h = self.height()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File System Log")
        self.setMinimumSize(self.w, self.h)

        # Layout
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.dummyLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.windowLayout.addLayout(self.dummyLayout)
        self.setLayout(self.windowLayout)

        # Set up Filtering
        self.groupBox = QGroupBox(self)
        chkLayout = QHBoxLayout()
        self.groupBox.setLayout(chkLayout)

        self.allChkBox = QCheckBox('ALL', self)
        self.createChkBox = QCheckBox('File Create', self)
        self.modifiyChkBox = QCheckBox('File Modifiy', self)
        self.deleteChkBox = QCheckBox('File Delete', self)
        chkLayout.addWidget(self.allChkBox)
        chkLayout.addWidget(self.createChkBox)
        chkLayout.addWidget(self.modifiyChkBox)
        chkLayout.addWidget(self.deleteChkBox)
        self.dummyLayout.addWidget(self.groupBox)

        self.search = QLineEdit(self)
        self.search.setFixedHeight(self.groupBox.height())
        self.search.showMaximized()
        self.search.setPlaceholderText("Search")
        self.search.editingFinished.connect(self.enterPressed)
        self.dummyLayout.addWidget(self.search)

        # Set up Export Button
        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.setFixedSize(120, self.groupBox.height())
        self.exportBtn.setStyleSheet("background-color: darkslategray;")
        self.exportBtn.clicked.connect(self.btnClicked)
        self.exportBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.dummyLayout.addWidget(self.exportBtn)

        # Set up NTFS Table
        self.ntfsTable = QTableWidget(self)
        # self.ntfsTable.setHorizontalHeaderLabels()
        ntfsTableHeader = self.ntfsTable.verticalHeader()
        ntfsTableHeader.setDefaultSectionSize(28)
        ntfsTableHeader.setMaximumSectionSize(28)
        self.ntfsTable.horizontalHeader().setStretchLastSection(True)
        self.ntfsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ntfsTable.verticalHeader().setVisible(False)
        self.windowLayout.addWidget(self.ntfsTable)

        self.show()

    def enterPressed(self, keyword):
        print(keyword)

    def btnClicked(self):
        print(self.selected)
        if self.selected == -1:
            QMessageBox.question(self, "Help", "Please select in above list.", QMessageBox.Ok)
            return
        self.export()

    def export(self):
        import os, csv
        # Export Link File List
        msg = "Success ! - hsah: " + self.hashLabel.text()
        try:
            fileName = self.hashLabel.text() + "-LinkFiles.csv"
            newpath = os.getcwd() + "\\" + fileName
            csvfile = open(newpath, 'w')
            lnk_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',
                                        fieldnames=self.linkFilesHeaderItems)
            lnk_writer.writeheader()
            for rowData in self.hashList[self.selected][2]["LinkFiles"]:
                try:
                    _dict = {self.linkFilesHeaderItems[n]: rowData[n] for n in range(len(rowData))}
                    lnk_writer.writerow(_dict)
                except Exception as e:
                    print(e)
                    pass

            # Export Dest List
            fileName = self.hashLabel.text() + "-DestList.csv"
            newpath = os.getcwd() + "\\" + fileName
            csvfile = open(newpath, 'w')
            destlist_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',
                                             fieldnames=self.destListHeaderItems)
            destlist_writer.writeheader()
            for rowData in self.hashList[self.selected][2]["DestList"]:
                try:
                    _dict = {self.destListHeaderItems[n]: rowData[n] for n in range(len(rowData))}
                    destlist_writer.writerow(_dict)
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            msg = "{}".format(e)
        QMessageBox.question(self, "Help", msg, QMessageBox.Ok)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = NTFSViewer()
    sys.exit(app.exec_())