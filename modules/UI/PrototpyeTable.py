import os, sys
from PyQt5.Qt import *
import modules.IE.Prototype as PrototypeForIE

class PrototypeTable(QTableWidget):
    def __init__(self, parent, env):
        super().__init__()
        self.setParent(parent)
        self.env = env
        self.prototype = []
        self.COLOR = [
            QColor(125, 125, 125, 30),
            QColor(255, 0, 0, 30),
            QColor(255, 125, 0, 30),
            QColor(255, 225, 0, 30),
            QColor(0, 255, 0, 30),
            QColor(0, 125, 255, 30),
            QColor(0, 0, 155, 30),
            QColor(155, 0, 225, 30),
        ]

    def load(self, sw, timeline=None):
        if sw == 1:
            print("Adobe Reader")
        elif sw == 2:
            print("Adobe Flash Player")
        elif sw == 3:
            print("Chrome")
        elif sw == 4:
            print("Edge")
        elif sw == 5:
            print("HWP")
        elif sw == 6:
            result, stuff = PrototypeForIE.getPrototype(self.env)
            if not result:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error")
                msg.setText(stuff)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(qApp.exit)
                msg.exec_()
                return
            self.prototype = stuff
            self.customHeaders = PrototypeForIE.getColumnHeader()
        elif sw == 7:
            print("Office")
        elif sw == 8:
            print("Local Privilege Escalation")
        else:
            print("기존 SW: {}".format(self.sw))
        if timeline:
            print("타임라인 설정 O")
        else:
            print("타임라인 설정 X")
        self.initUI()

    def initUI(self):
        print("initUI")
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["", "", "", "", "", ""])
        self.setRowCount(len(self.prototype))
        row = 0
        for list in self.prototype:
            self.setVerticalHeaderItem(row, QTableWidgetItem(list[0][0]))
            self.setItem(row, 0, QTableWidgetItem(list[1]))
            self.setItem(row, 1, QTableWidgetItem(list[2]))
            self.setItem(row, 2, QTableWidgetItem(list[3]))
            if list[0][0] == "History":
                self.item(row, 2).setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 3, QTableWidgetItem(""))
                self.setItem(row, 4, QTableWidgetItem(""))
            elif list[0][0] == "Prefetch":
                self.setItem(row, 3, QTableWidgetItem(list[4]))
                self.item(row, 3).setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 4, QTableWidgetItem(""))
            else:
                self.setItem(row, 3, QTableWidgetItem(list[4]))
                self.item(row, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
                self.setItem(row, 4, QTableWidgetItem(list[5]))

            self.item(row, 0).setTextAlignment(Qt.AlignCenter)
            self.item(row, 4).setTextAlignment(Qt.AlignCenter)
            self.verticalHeaderItem(row).setTextAlignment(Qt.AlignRight)
            for c in range(self.columnCount()):  # Adjust COLOR of Row
                self.item(row, c).setBackground(self.COLOR[list[0][1]])
            row += 1

        # Align Column header
        for c in range(self.columnCount()):
            self.horizontalHeaderItem(c).setTextAlignment(Qt.AlignCenter)

        # Adjust column width
        self.resizeColumnsToContents()
        header = self.horizontalHeader()
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 600)
        self.setColumnWidth(2, 180)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # Adjust row height
        self.verticalHeader().setDefaultSectionSize(28)
        self.verticalHeader().setMaximumSectionSize(28)

        # Handle event
        self.cellClicked.connect(self.changeColumnHeader)  # One-Click
        self.cellDoubleClicked.connect(self.showDetail)  # Double-Click
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def search(self, keyword):
        if keyword:
            for i in range(len(self.prototype)):
                self.showRow(i)
        items = self.findItems(keyword, Qt.MatchContains)
        includedRow = list(set([ self.row(item) for item in items ]))
        print(includedRow)
        for i in range(len(self.prototype)):
            if i not in includedRow:
                self.hideRow(i)
            elif self.isRowHidden(i):
                self.showRow(i)

    # @pyqtSlot()
    def changeColumnHeader(self, row, column):
        _header = self.verticalHeaderItem(row).text()
        self.setHorizontalHeaderLabels(self.customHeaders[_header])

    # @pyqtSlot()
    def showDetail(self, row, column):
        print(row, column)
        viewerTitle = self.verticalHeaderItem(row).text()
        print(viewerTitle)
        viewerContent = self.prototype[row][-1]
        print(viewerContent)

        from modules.UI.TextViewer import TextViewer
        self.viewer = TextViewer()
        self.viewer.initUI(viewerTitle, viewerContent)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()
        elif action == copyAction:
            selected = self.selectedItems()
            if len(selected) == 1:
                copiedStr = selected[0].text()
            else:
                copiedStr = " ".join(currentQTableWidgetItem.text() for currentQTableWidgetItem in selected)
            os.system("echo {} | clip".format(copiedStr))
            print(copiedStr)
