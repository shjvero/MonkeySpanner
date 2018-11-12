from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import *

class JumpListViewer(QWidget):
    def __init__(self, hashList):
        super().__init__()
        self.hashList = hashList
        self.w = self.width()
        self.h = self.height()
        self.listViewWidth = 180
        self.linkFilesHeaderItems = ["Modified Time", "Accessed Time", "Created Time", "LocalBasePath", "Size", "E.No.",
             "Drive Type", "VolumnName", "Serial No."]
        self.destListHeaderItems = ["Last Recorded Access", "Data", "E.No.", "Access Count", "NetBIOSName", "New (Timestamp)",
             "New (MAC)", "Seq No.", "Birth (Timestamp)", "Birth (MAC)"]
        self.selected = -1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JumpList")
        self.setMinimumSize(self.w, self.h)

        # Layout
        self.windowLayout = QBoxLayout(QBoxLayout.LeftToRight, self)
        self.leftLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.rightLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.windowLayout.addLayout(self.leftLayout)
        self.windowLayout.addLayout(self.rightLayout)
        self.setLayout(self.windowLayout)

        # Set up Label
        self.hashTitleLabel = QLabel("Hash: ", self)
        self.hashLabel = QLabel(self)
        self.hashLabel.setFixedWidth(self.listViewWidth)
        self.hashLabel.setAlignment(Qt.AlignCenter)

        # Set up ListView
        self.hashListView = QListView(self)
        self.model = QStandardItemModel()
        for h in self.hashList:
            self.model.appendRow(QStandardItem(h[0]))
        self.hashListView.setModel(QStandardItemModel())
        self.hashListView.setMaximumWidth(self.listViewWidth)
        self.hashListView.clicked.connect(self.selectedHash)
        self.hashListView.setModel(self.model)
        
        # Set up Export Button
        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.setFixedSize(self.listViewWidth, 40)
        self.exportBtn.setStyleSheet("background-color: darkslategray;")
        self.exportBtn.clicked.connect(self.btnClicked)
        self.exportBtn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Set up LinkFiles Table
        self.LinkFileLabel = QLabel("Link Files:", self)
        self.LinkFilesTable = QTableWidget(self)
        linkFilesHeader = self.LinkFilesTable.verticalHeader()
        linkFilesHeader.setDefaultSectionSize(28)
        linkFilesHeader.setMaximumSectionSize(28)
        self.LinkFilesTable.horizontalHeader().setStretchLastSection(True)
        self.LinkFilesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LinkFilesTable.verticalHeader().setVisible(False)
        self.LinkFilesTable.setColumnCount(len(self.linkFilesHeaderItems))
        self.LinkFilesTable.setHorizontalHeaderLabels(self.linkFilesHeaderItems)

        # Set up DestList Table
        self.DestListLabel = QLabel("Dest List:", self)
        self.DestListTable = QTableWidget(self)
        destListHeader = self.DestListTable.verticalHeader()
        destListHeader.setDefaultSectionSize(28)
        destListHeader.setMaximumSectionSize(28)
        self.DestListTable.horizontalHeader().setStretchLastSection(True)
        self.DestListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.DestListTable.verticalHeader().setVisible(False)
        self.DestListTable.setColumnCount(len(self.destListHeaderItems))
        self.DestListTable.setHorizontalHeaderLabels(self.destListHeaderItems)

        self.leftLayout.addWidget(self.hashTitleLabel)
        self.leftLayout.addWidget(self.hashLabel)
        self.leftLayout.addWidget(self.hashListView)
        self.leftLayout.addWidget(self.exportBtn)
        self.rightLayout.addWidget(self.LinkFileLabel)
        self.rightLayout.addWidget(self.LinkFilesTable)
        self.rightLayout.addWidget(self.DestListLabel)
        self.rightLayout.addWidget(self.DestListTable)

        self.show()

    def selectedHash(self, i):
        self.selected = self.model.itemFromIndex(i).row()
        self.hashLabel.setText(self.hashList[self.selected][1])
        self.loadData(self.hashList[self.selected][2])

    def loadData(self, logList):
        LinkFiles = logList["LinkFiles"]
        DestList = logList["DestList"]
        self.LinkFilesTable.clearContents()
        self.LinkFilesTable.setRowCount(len(LinkFiles))
        self.DestListTable.clearContents()
        self.DestListTable.setRowCount(len(DestList))
        r = 0
        for item in LinkFiles:
            for c in range(self.LinkFilesTable.columnCount()):
                self.LinkFilesTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1
        r = 0
        self.LinkFilesTable.resizeColumnsToContents()

        for item in DestList:
            for c in range(self.DestListTable.columnCount()):
                self.DestListTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1
        self.DestListTable.resizeColumnsToContents()

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
            lnk_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.linkFilesHeaderItems)
            lnk_writer.writeheader()
            for rowData in self.hashList[self.selected][2]["LinkFiles"]:
                try:
                    _dict = { self.linkFilesHeaderItems[n]:rowData[n] for n in range(len(rowData)) }
                    lnk_writer.writerow(_dict)
                except Exception as e:
                    print(e)
                    pass

            # Export Dest List
            fileName = self.hashLabel.text() + "-DestList.csv"
            newpath = os.getcwd() + "\\" + fileName
            csvfile = open(newpath, 'w')
            destlist_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.destListHeaderItems)
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
