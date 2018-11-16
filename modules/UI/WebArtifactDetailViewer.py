from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QLabel, QScrollArea, QVBoxLayout, \
    QApplication


class WebArtifactDetailViewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def initUI(self, title, contents):
        self.category = [
            "ID",
            "Container Name",
            "Created Time",
            "Accessed Time",
            "Modified Time",
            "Expires Time",
            "Synced Time",
            "Sync Count",
            "Access Count",
            "URL",
            "File Name",
            "File Size",
            "Directory"
        ]
        # response header
        self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setMinimumSize(self.width(), 370)
        self.table.setRowCount(len(self.category))
        self.table.setColumnCount(2)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        for i in range(len(self.category)):
            self.table.setItem(i, 0, QTableWidgetItem(self.category[i]))
        for i in range(len(contents)-1):
            self.table.setItem(i, 1, QTableWidgetItem(contents[i]))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.verticalHeader().setMaximumSectionSize(28)
        self.table.setColumnWidth(0, 120)

        self.headerLabel = QLabel("Response Header", self)
        self.headerLabel.setFixedHeight(30)
        self.headerLabel.setAlignment(Qt.AlignBottom)

        self.label = QLabel()
        content = contents[-1] if contents[-1] else "None"
        self.label.setText(content)
        self.label.setMargin(10)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.label)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.headerLabel)
        self.layout.addWidget(self.scrollArea)
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
