from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QLabel, QScrollArea, QVBoxLayout, \
    QApplication


class JumpListDetailViewer(QWidget):
    LNK_FILE = 0
    DEST_LIST = 1

    def __init__(self):
        QWidget.__init__(self)
        self.basicCategory = ["JumpList Name", "Software Name", "Type",]
        self.dataCategory = [
            [
                "Local Base Path",
                "Modified Time",
                "Accessed Time",
                "Created Time",
                "File Size",
                "Drive Type",
                "Volumn Name",
                "Serial Number",
            ],
            [
                "Entry ID (E.NO)",
                "File Path",
                "Last Recorded Time",
                "Access Count",
                "New (Timestamp)",
                "New (MAC)",
                "Birth (Timestamp)",
                "Birth (MAC)",
                "NetBIOSName",
                "Sequence No",
            ]
        ]

    def initUI(self, type, contents):
        '''
        LNK: [
            [0] JumpList File Name
            [1] Software,
            [2] Type,
            [3] lnk_header
                    [0] Modified Time
                    [1] Accessed Time
                    [2] Created Time
                    [3] File Size
                lnk_after_header
                    [4] Drive Type
                    [5] Volumn Name
                    [6] Drive Serial Number
                    [7] LocalBasePath
        ]

        Dest: [
            [0] JumpList File Name
            [1] Software,
            [2] Type,
            [3] Data
                    [0] Accessed Time,
                    [1] Full Path
                    [2] Entry ID Number (E.NO)
                    [3] Access Count
                    [4] NetBIOSName
                    [5] New (timestamp)
                    [6] New (MAC)
                    [7] Sequence Number
                    [8] Birth (timestamp)
                    [9] Birth (MAC)
        ]
        '''

        if type == JumpListDetailViewer.LNK_FILE:
            self.setWindowTitle("JumpList Link-File")
        elif type == JumpListDetailViewer.DEST_LIST:
            self.setWindowTitle("JumpList Dest-List")

        self.layout = QVBoxLayout(self)
        self.basicLabel = QLabel("Basic Information", self)

        self.basicTable = QTableWidget(self)
        self.basicTable.setFixedHeight(90)
        self.basicTable.setRowCount(len(self.basicCategory))
        self.basicTable.setColumnCount(2)
        self.basicTable.verticalHeader().setVisible(False)
        self.basicTable.horizontalHeader().setVisible(False)
        for i in range(len(self.basicCategory)):
            self.basicTable.setItem(i, 0, QTableWidgetItem(self.basicCategory[i]))
        for i in range(len(self.basicCategory)):
            self.basicTable.setItem(i, 1, QTableWidgetItem(contents[i]))
        self.basicTable.verticalHeader().setDefaultSectionSize(28)
        self.basicTable.verticalHeader().setMaximumSectionSize(28)
        self.basicTable.horizontalHeader().setStretchLastSection(True)
        self.basicTable.verticalHeader().setStretchLastSection(True)
        self.basicTable.setColumnWidth(0, 120)

        self.dataLabel = QLabel("JumpList Information", self)
        self.dataLabel.setFixedHeight(30)
        self.dataLabel.setAlignment(Qt.AlignBottom)

        self.dataTable = QTableWidget(self)
        self.dataTable.setRowCount(len(self.dataCategory[type]))
        self.dataTable.setColumnCount(2)
        self.dataTable.verticalHeader().setVisible(False)
        self.dataTable.horizontalHeader().setVisible(False)
        for i in range(len(self.dataCategory[type])):
            self.dataTable.setItem(i, 0, QTableWidgetItem(self.dataCategory[type][i]))
        if type == JumpListDetailViewer.LNK_FILE:
            self.dataTable.setMinimumSize(self.width(), 230)
            self.dataTable.setItem(0, 1, QTableWidgetItem(contents[3][-1]))
            for i in range(len(contents[3])-1):
                self.dataTable.setItem(i + 1, 1, QTableWidgetItem(contents[3][i]))
        elif type == JumpListDetailViewer.DEST_LIST:
            self.dataTable.setMinimumSize(self.width(), 290)
            self.dataTable.setItem(0, 1, QTableWidgetItem(contents[3][2]))
            self.dataTable.setItem(1, 1, QTableWidgetItem(contents[3][1]))
            self.dataTable.setItem(2, 1, QTableWidgetItem(contents[3][0]))
            self.dataTable.setItem(3, 1, QTableWidgetItem(contents[3][3]))
            self.dataTable.setItem(4, 1, QTableWidgetItem(contents[3][5]))
            self.dataTable.setItem(5, 1, QTableWidgetItem(contents[3][6]))
            self.dataTable.setItem(6, 1, QTableWidgetItem(contents[3][8]))
            self.dataTable.setItem(7, 1, QTableWidgetItem(contents[3][9]))
            self.dataTable.setItem(8, 1, QTableWidgetItem(contents[3][4]))
            self.dataTable.setItem(9, 1, QTableWidgetItem(contents[3][7]))

        self.dataTable.verticalHeader().setDefaultSectionSize(28)
        self.dataTable.verticalHeader().setMaximumSectionSize(28)
        self.dataTable.horizontalHeader().setStretchLastSection(True)
        self.dataTable.verticalHeader().setStretchLastSection(True)
        self.dataTable.setColumnWidth(0, 120)

        self.layout.addWidget(self.basicLabel)
        self.layout.addWidget(self.basicTable)
        self.layout.addWidget(self.dataLabel)
        self.layout.addWidget(self.dataTable)

        self.show()

    def contextMenuEvent(self, event):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
                # 에러나는 이유는,, \n가 있어서 -- 어찌할건가?
