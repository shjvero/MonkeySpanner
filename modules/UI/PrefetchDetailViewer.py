from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *

class PrefetchDetailViewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def initUI(self, viewerTitle, viewerContent):
        '''
        viewerContent = [
            [0] => FileName
            [1] => [Exec name, Run Cnt]
            [2] => [MFT seq #, MFT entry #]
            [3] => [ executed time list ]
            [4] => [vol name, create date, serial num]
            [5] => [ directory strings list ]
            [6] => [ Resources loaded ]
        ]
        '''
        self.content = viewerContent
        self.setWindowTitle(viewerTitle)
        self.setMinimumHeight(self.height() + 200)

        self.layout = QFormLayout(self)

        # File Name
        self.fnameLabel = QLabel(viewerContent[0], self)
        self.fnameLabel.setFixedHeight(40)
        self.fnameLabel.setAlignment(Qt.AlignCenter)

        # Prefetch Information
        self.pfInfoTable = QTableWidget(self)
        self.pfInfoTable.setMinimumSize(350, 65)
        self.pfInfoTable.setMaximumSize(self.width(), 65)
        self.pfInfoTable.setRowCount(2)
        self.pfInfoTable.setColumnCount(2)
        self.pfInfoTable.setItem(0, 0, QTableWidgetItem("Executable Name  "))
        self.pfInfoTable.setItem(1, 0, QTableWidgetItem("Run Count"))
        self.pfInfoTable.setItem(0, 1, QTableWidgetItem(viewerContent[1][0]))
        self.pfInfoTable.setItem(1, 1, QTableWidgetItem(viewerContent[1][1]))
        self.pfInfoTable.verticalHeader().setVisible(False)
        self.pfInfoTable.horizontalHeader().setVisible(False)
        self.pfInfoTable.resizeColumnsToContents()
        self.pfInfoTable.verticalHeader().setStretchLastSection(True)
        self.pfInfoTable.horizontalHeader().setStretchLastSection(True)

        # MFT Information
        self.mftInfoTable = QTableWidget(self)
        self.mftInfoTable.setMinimumSize(350, 65)
        self.mftInfoTable.setMaximumSize(self.width(), 65)
        self.mftInfoTable.setRowCount(2)
        self.mftInfoTable.setColumnCount(2)
        self.mftInfoTable.setItem(0, 0, QTableWidgetItem("MFT Sequence Number  "))
        self.mftInfoTable.setItem(1, 0, QTableWidgetItem("MFT Entry Number"))
        self.mftInfoTable.setItem(0, 1, QTableWidgetItem(viewerContent[2][0]))
        self.mftInfoTable.setItem(1, 1, QTableWidgetItem(viewerContent[2][1]))
        self.mftInfoTable.verticalHeader().setVisible(False)
        self.mftInfoTable.horizontalHeader().setVisible(False)
        self.mftInfoTable.resizeColumnsToContents()
        self.mftInfoTable.verticalHeader().setStretchLastSection(True)
        self.mftInfoTable.horizontalHeader().setStretchLastSection(True)

        # Execution Time
        self.timeLabel = QLabel("Executed Time", self)
        self.timeLabel.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

        self.timeList = QListView(self)
        self.timeList.setFixedHeight(120)
        self.timeListModel = QStandardItemModel()
        for i in range(len(viewerContent[3])):
            item = QStandardItem(viewerContent[3][i])
            item.setTextAlignment(Qt.AlignCenter)
            self.timeListModel.appendRow(item)
        self.timeList.setModel(self.timeListModel)

        # Volumn Information
        self.volLabel = QLabel("Volumn Information", self)
        self.volLabel.setFixedHeight(30)
        self.volLabel.setAlignment(Qt.AlignBottom)

        self.volTable = QTableWidget(self)
        self.volTable.setFixedHeight(93)
        self.volTable.setRowCount(3)
        self.volTable.setColumnCount(2)
        self.volTable.setItem(0, 0, QTableWidgetItem("Volumn Name  "))
        self.volTable.setItem(0, 1, QTableWidgetItem(viewerContent[4][0]))
        self.volTable.setItem(1, 0, QTableWidgetItem("Creation Date  "))
        self.volTable.setItem(1, 1, QTableWidgetItem(viewerContent[4][1]))
        self.volTable.setItem(2, 0, QTableWidgetItem("Serial Number  "))
        self.volTable.setItem(2, 1, QTableWidgetItem(viewerContent[4][2]))
        self.volTable.verticalHeader().setVisible(False)
        self.volTable.horizontalHeader().setVisible(False)
        self.volTable.setColumnWidth(0, 150)
        self.volTable.verticalHeader().setStretchLastSection(True)
        self.volTable.horizontalHeader().setStretchLastSection(True)

        # Directory Strings
        self.dirStrLabel = QLabel("Directory Strings", self)
        self.dirStrLabel.setFixedHeight(30)
        self.dirStrLabel.setAlignment(Qt.AlignBottom)

        self.dirStrList = QListView()
        self.dirStrList.setMinimumWidth(self.width())
        self.dirStrListModel = QStandardItemModel()
        for i in range(len(viewerContent[5])):
            self.dirStrListModel.appendRow(QStandardItem(viewerContent[5][i]))
        self.dirStrList.setModel(self.dirStrListModel)

        self.rscLoadedLabel = QLabel("Resources Loaded", self)
        self.rscLoadedLabel.setFixedHeight(30)
        self.rscLoadedLabel.setAlignment(Qt.AlignBottom)

        self.rscLoadedList = QListView()
        self.rscLoadedListModel = QStandardItemModel()
        self.rscLoadedList.setMinimumWidth(self.width())
        for i in range(len(viewerContent[6])):
            self.rscLoadedListModel.appendRow(QStandardItem(viewerContent[6][i]))
        self.rscLoadedList.setModel(self.rscLoadedListModel)

        # Resource DLL loading
        self.childLayout1 = QBoxLayout(QBoxLayout.TopToBottom)
        self.childLayout2 = QBoxLayout(QBoxLayout.TopToBottom)
        self.childLayout1.addWidget(self.pfInfoTable)
        self.childLayout1.addWidget(self.mftInfoTable)
        self.childLayout2.addWidget(self.timeLabel)
        self.childLayout2.addWidget(self.timeList)
        self.childLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.childLayout.addLayout(self.childLayout1)
        self.childLayout.addLayout(self.childLayout2)

        self.layout.addRow(self.fnameLabel)
        self.layout.addRow(self.childLayout)
        self.layout.addRow(self.volLabel)
        self.layout.addRow(self.volTable)
        self.layout.addRow(self.dirStrLabel)
        self.layout.addRow(self.dirStrList)
        self.layout.addRow(self.rscLoadedLabel)
        self.layout.addRow(self.rscLoadedList)
        self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
                # 에러나는 이유는,, \n가 있어서 -- 어찌할건가?

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = PrefetchDetailViewer()
    sys.exit(app.exec_())