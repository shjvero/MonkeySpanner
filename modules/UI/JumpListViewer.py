import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

class JumpListViewer(QWidget):
    def __init__(self, content):
        super().__init__()
        self.contents = content

    def show(self):
        self.setWindowTitle("JumpList")
        self.setWindowIcon("../../img/logo.png")
        self.setMinimumSize(800, self.height()+200)
        self.loadJumpList()
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
        # self.label1.resize(self.label1.sizeHint())
        self.LinkFilesTable.move(10, 40)
        self.LinkFilesTable.setMinimumSize(800, 300)
        self.LinkFilesTable.resizeColumnsToContents()
        self.LinkFilesTable.verticalHeader().setDefaultSectionSize(28)
        self.LinkFilesTable.verticalHeader().setMaximumSectionSize(28)
        self.LinkFilesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LinkFilesTable.verticalHeader().setVisible(False)

        self.label2 = QLabel("Dest List:", self)
        self.label2.move(10, self.LinkFilesTable.height()+70)
        self.DestListTable.move(10, self.LinkFilesTable.height()+90)
        self.DestListTable.setMinimumSize(800, 300)
        self.DestListTable.verticalHeader().setDefaultSectionSize(28)
        self.DestListTable.verticalHeader().setMaximumSectionSize(28)
        self.DestListTable.resizeColumnsToContents()
        self.DestListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.DestListTable.verticalHeader().setVisible(False)
        self.show()


