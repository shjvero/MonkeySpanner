from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QBoxLayout, QLineEdit, QPushButton, \
    QTableWidgetItem
from libs.ParseRegistry.Amcache import FIELDS


class TableViewer(QWidget):
    def __init__(self, title, contents):
        QWidget.__init__(self)
        self.columnHeader = list(map(lambda e: e.name, FIELDS))
        self.title = title
        self.contents = contents
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(self.width(), self.height())
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.topLayout = QBoxLayout(QBoxLayout.LeftToRight, self)

        self.search = QLineEdit(self)
        self.search.returnPressed.connect(self.enterPressed)
        self.search.setFixedHeight(30)
        self.search.setPlaceholderText("Search")

        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.setFixedHeight(30)
        self.exportBtn.clicked.connect(self.export)
        self.exportBtn.setFixedWidth(150)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.columnHeader))
        self.table.setHorizontalHeaderLabels(self.columnHeader)
        self.table.verticalHeader().setVisible(False)

        for row in range(len(self.contents)):
            self.table.insertRow(row)
            for col in range(len(self.columnHeader)):
                self.table.setItem(row, col, QTableWidgetItem(self.contents[row][col]))
                self.table.item(row, col).setTextAlignment(Qt.AlignCenter)
            self.table.item(row, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.topLayout.addWidget(self.search)
        self.topLayout.addWidget(self.exportBtn)
        self.layout.addLayout(self.topLayout)
        self.layout.addWidget(self.table)

        self.show()

    def enterPressed(self):
        keyword = self.search.text()
        if not keyword:
            for row in range(len(self.contents)):
                if self.table.isRowHidden(row):
                    self.table.showRow(row)
            return
        items = self.table.findItems(keyword, Qt.MatchContains)
        includedRow = list(set([self.table.row(item) for item in items]))
        for row in range(len(self.contents)):
            if row in includedRow:
                self.table.showRow(row)
            else:
                self.table.hideRow(row)

    def export(self):
        import os, csv, datetime

        csv_name = os.getcwd() + "\\amcache_{}.csv".format(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f"))
        with open(csv_name, 'w', encoding='utf-8', newline='') as csv_file:
            w = csv.writer(csv_file)
            w.writerow(map(lambda e: e.name, FIELDS))
            for e in self.contents:
                w.writerow(map(lambda i: getattr(e, i.name), FIELDS))


    def contextMenuEvent(self, event):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            selected = self.table.selectedItems()
            if len(selected) == 1:
                copiedStr = selected[0].text()
            else:
                copiedStr = " ".join(currentQTableWidgetItem.text() for currentQTableWidgetItem in selected)
            import pyperclip
            pyperclip.copy(copiedStr)
