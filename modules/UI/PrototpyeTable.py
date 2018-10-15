import os, sys
from PyQt5.Qt import *
import modules.IE.Prototype as InternetExplorerPrototype

class PrototypeTable(QTableWidget):
    def __init__(self, sw, env):
        super().__init__()
        self.sw = sw
        self.env = env
        self.prototype = []
        self.colors = {
            "Prefetch": QColor(255, 0, 0, 30),
            "EventLog": QColor(0, 255, 0, 30),
            "History": QColor(0, 0, 255, 30),
            "Cache": QColor(125, 125, 125, 30)
        }
        self.load(sw)

    def load(self, sw=None, timeline=None):
        if sw == 1:
            print("Adobe Flash Player")
        elif sw == 2:
            print("HWP")
        elif sw == 3:
            self.prototype, self.row = InternetExplorerPrototype.getPrototype(self.env)
            self.customHeaders = InternetExplorerPrototype.getColumnHeader()
        elif sw == 4:
            print("Office")
        elif sw == 5:
            print("PDF")
        else:
            print("기존 SW: {}".format(self.sw))
        if timeline:
            print("타임라인 설정 O")
        else:
            print("타임라인 설정 X")

    def initUI(self):
        print("initUI")
        self.setColumnCount(5)
        self.setRowCount(self.row)
        self.setHorizontalHeaderLabels(["", "", "", "", "", ""])
        row = 0
        for header, list in self.prototype.items():
            for prototypeItem in list:
                self.setVerticalHeaderItem(row, QTableWidgetItem(header))
                self.setItem(row, 0, QTableWidgetItem(prototypeItem[0]))
                self.setItem(row, 1, QTableWidgetItem(prototypeItem[1]))
                self.setItem(row, 2, QTableWidgetItem(prototypeItem[2]))
                if header == "History":
                    # print(prototypeItem)
                    self.item(row, 2).setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, 3, QTableWidgetItem(""))
                    self.setItem(row, 4, QTableWidgetItem(""))
                elif header == "Prefetch":
                    self.setItem(row, 3, QTableWidgetItem(prototypeItem[3]))
                    self.item(row, 3).setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, 4, QTableWidgetItem(""))
                else:
                    self.setItem(row, 3, QTableWidgetItem(prototypeItem[3]))
                    self.item(row, 3).setTextAlignment(Qt.AlignRight)
                    self.setItem(row, 4, QTableWidgetItem(prototypeItem[4]))
                    self.item(row, 4).setTextAlignment(Qt.AlignCenter)
                for c in range(self.columnCount()):                     # Adjust Color of Row
                    self.item(row, c).setBackground(self.colors[header])
                self.item(row, 0).setTextAlignment(Qt.AlignCenter)      # `Timeline` Text Alignment
                self.verticalHeaderItem(row).setTextAlignment(Qt.AlignRight)
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
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setMaximumSectionSize(24)

        # Handle event
        self.clicked.connect(self.changeColumnHeader)  # One-Click
        self.doubleClicked.connect(self.showDetail)  # Double-Click
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def search(self, keyword):
        print("search: " + keyword)

    @pyqtSlot()
    def changeColumnHeader(self):
        for currentQTableWidgetItem in self.selectedItems():
            self.parentWidget().statusBar().showMessage(currentQTableWidgetItem.text())
            _header = self.verticalHeaderItem(currentQTableWidgetItem.row()).text()
            self.setHorizontalHeaderLabels(self.customHeaders[_header])

    @pyqtSlot()
    def showDetail(self):
        print("showDetail")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()
        elif action == copyAction:
            copiedStr = " ".join(currentQTableWidgetItem.text() for currentQTableWidgetItem in self.selectedItems())
            os.system("echo {} | clip".format(copiedStr))
            print(copiedStr)        # Not copy multiple row