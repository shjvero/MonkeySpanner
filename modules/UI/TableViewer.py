import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

class TableViewer(QWidget):
    def __init__(self):
        super().__init__()

    def showUsnjrnl(self):
        print("Show $usnjrnl: " + self.path)
        self.initUI()

    def showMFT(self):
        print("Show $MFT: " + self.path)
        self.initUI()

    def showLogFile(self):
        print("Show $LogFile: " + self.path)
        self.initUI(2)

    def showJumpList(self, content):
        self.contents = content
        self.initUI(2)

    def initUI(self, type):
        self.setWindowTitle("JumpList")
        self.setWindowIcon(QIcon("../../img/logo.png"))
        self.setMinimumSize(800, self.height()+200)
        if type == 2:
            self.loadJumpList()
        else:
            self.table = QTableWidget(self)
            print("FileSystem")
        self.show()

    def loadJumpList(self):
        print("loadJumpList")
        LinkFiles = self.contents["LinkFiles"]
        DestList = self.contents["DestList"]

        self.LinkFilesTable = QTableWidget(self)
        self.LinkFilesTable.setRowCount(len(LinkFiles))
        self.LinkFilesTable.setColumnCount(len(LinkFiles[0]))
        self.DestListTable = QTableWidget(self)
        self.DestListTable.setRowCount(len(DestList))
        self.DestListTable.setColumnCount(len(DestList[0]))
        self.LinkFilesTable.setHorizontalHeaderLabels(["Modified Time", "Accessed Time", "Created Time", "LocalBasePath", "Size", "E.No.", "Drive Type", "VolumnName", "Serial No."])
        self.DestListTable.setHorizontalHeaderLabels(["Last Recorded Access", "Data", "E.No.", "Access Count", "NetBIOSName", "New (Timestamp)", "New (MAC)", "Seq No.", "Birth (Timestamp)", "Birth (MAC)"])
        r = 0
        for item in LinkFiles:
            for c in range(self.LinkFilesTable.columnCount()):
               self.LinkFilesTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1

        r = 0
        for item in DestList:
            for c in range(self.DestListTable.columnCount()):
               self.DestListTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1

        self.label1 = QLabel("Link Files:", self)
        self.label1.move(10, 15)
        # self.label.resize(self.label1.sizeHint())
        self.LinkFilesTable.move(10, 40)
        self.LinkFilesTable.setMinimumSize(800, 300)
        self.LinkFilesTable.resizeColumnsToContents()
        self.LinkFilesTable.verticalHeader().setDefaultSectionSize(24)
        self.LinkFilesTable.verticalHeader().setMaximumSectionSize(24)
        self.LinkFilesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LinkFilesTable.verticalHeader().setVisible(False)

        self.label2 = QLabel("Dest List:", self)
        self.label2.move(10, self.LinkFilesTable.height()+70)
        self.DestListTable.move(10, self.LinkFilesTable.height()+90)
        self.DestListTable.setMinimumSize(800, 300)
        self.DestListTable.verticalHeader().setDefaultSectionSize(24)
        self.DestListTable.verticalHeader().setMaximumSectionSize(24)
        self.DestListTable.resizeColumnsToContents()
        self.DestListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.DestListTable.verticalHeader().setVisible(False)


