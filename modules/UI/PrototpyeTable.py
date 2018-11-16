import os
from PyQt5.Qt import *
import modules.AnalyzerForHWP as HWP
import modules.AnalyzerForIE as IE
import modules.AnalyzerForOffice as Office
import modules.AnalyzerForEdge as Edge
import modules.AnalyzerForFlash as Flash
import modules.AnalyzerForKernel as Kernel
import modules.constant as CONSTANT

class PrototypeTable(QTableWidget):
    ONLY_HIDE = 1
    ONLY_SHOW = 2
    SIMPLE_SHOW = 3

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
        if sw == CONSTANT.ADOBE_READER:
            QMessageBox.information(self, "Help", "Preparing...[Adobe Reader]", QMessageBox.Ok)
            return
        elif sw == CONSTANT.ADOBE_FLASH_PLAYER:
            QMessageBox.information(self, "Help", "Preparing...[Adobe Flash Player]", QMessageBox.Ok)
            return
        elif sw == CONSTANT.EDGE:
            QMessageBox.information(self, "Help", "Preparing...[Microsoft Edge]", QMessageBox.Ok)
            return
        elif sw == CONSTANT.HWP:
            self.prototype = HWP.getPrototype(self.env)
            self.customHeaders = HWP.getColumnHeader()
        elif sw == CONSTANT.IE:
            result, stuff = IE.getPrototype(self.env)
            if not result:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(stuff)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(qApp.exit)
                msg.exec_()
                return
            self.prototype = stuff
            self.customHeaders = IE.getColumnHeader()
        elif sw == CONSTANT.OFFICE:
            office_msg = None
            result, self.prototype = Office.getPrototype(self.env, office_msg)
            if office_msg:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Warning")
                msg.setText(office_msg)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            self.customHeaders = Office.getColumnHeader()
        elif sw == CONSTANT.LPE:
            QMessageBox.information(self, "Help", "Preparing...[Kerenl]", QMessageBox.Ok)
            return
        else:
            print("기존 SW: {}".format(sw))
        if timeline:
            print("타임라인 설정 O")
        else:
            print("타임라인 설정 X")
        self.initUI()

    def initUI(self):
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
        self.resizeRowsToContents()
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

    def search(self, keyword, btnChecked=False):
        if not keyword:
            if not btnChecked:
                for i in range(len(self.prototype)):
                    self.showRow(i)
            return
        items = self.findItems(keyword, Qt.MatchContains)
        includedRow = list(set([self.row(item) for item in items]))
        for i in range(len(self.prototype)):
            if i not in includedRow:
                self.hideRow(i)
            elif self.isRowHidden(i):
                if btnChecked:
                    continue
                else:
                    self.showRow(i)

    def filtering(self, type, state=0):
        target = None
        if type == 0:
            self.search("")
            return
        elif type == 1:
            target = CONSTANT.PREFETCH_KEYWORD
        elif type == 2:
            target = CONSTANT.EVENTLOG_KEYWORD
        elif type == 3:
            target = CONSTANT.REGISTRY_KEYWORD
        elif type == 4:
            target = CONSTANT.HISTORY_KEYWORD
        elif type == 5:
            target = CONSTANT.CACHE_KEYWORD
        elif type == 6:
            target = CONSTANT.WER_KEYWORD
        elif type == 7:
            target = CONSTANT.LNKFILE_KEYWORD
        elif type == 8:
            target = CONSTANT.DESTLIST_KEYWORD
        if state == PrototypeTable.ONLY_HIDE:
            for row in range(len(self.prototype)):
                if self.prototype[row][0][0] == target:
                    self.hideRow(row)
        elif state == PrototypeTable.ONLY_SHOW:
            for row in range(len(self.prototype)):
                if self.prototype[row][0][0] == target:
                    self.showRow(row)
        elif state == PrototypeTable.SIMPLE_SHOW:
            for row in range(len(self.prototype)):
                if self.prototype[row][0][0] == target:
                    self.showRow(row)
                else:
                    self.hideRow(row)

    def changeColumnHeader(self, row, column):
        _header = self.verticalHeaderItem(row).text()
        self.setHorizontalHeaderLabels(self.customHeaders[_header])

    def showDetail(self, row, column):
        viewerTitle = self.verticalHeaderItem(row).text()
        viewerContent = self.prototype[row][-1]
        if viewerTitle == CONSTANT.PREFETCH_KEYWORD:
            from modules.UI.PrefetchDetailViewer import PrefetchDetailViewer
            self.pdv = PrefetchDetailViewer()
            self.pdv.initUI(viewerTitle, viewerContent)
        elif viewerTitle in [CONSTANT.EVENTLOG_KEYWORD, CONSTANT.WER_KEYWORD, CONSTANT.REGISTRY_KEYWORD]:
            from modules.UI.TextViewer import TextViewer
            self.viewer = TextViewer()
            self.viewer.initUI(viewerTitle, viewerContent)
        elif viewerTitle in [CONSTANT.HISTORY_KEYWORD, CONSTANT.CACHE_KEYWORD]:
            from modules.UI.WebArtifactDetailViewer import WebArtifactDetailViewer
            self.wadv = WebArtifactDetailViewer()
            self.wadv.initUI(viewerTitle, viewerContent)
        elif viewerTitle == CONSTANT.LNKFILE_KEYWORD:
            from modules.UI.JumpListDetailViewer import JumpListDetailViewer
            self.jldv = JumpListDetailViewer()
            self.jldv.initUI(JumpListDetailViewer.LNK_FILE, viewerContent)
        elif viewerTitle == CONSTANT.DESTLIST_KEYWORD:
            from modules.UI.JumpListDetailViewer import JumpListDetailViewer
            self.jldv = JumpListDetailViewer()
            self.jldv.initUI(JumpListDetailViewer.DEST_LIST, viewerContent)

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
            import subprocess
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            command = 'echo "{}" | clip'.format(copiedStr)
            subprocess.call(command, startupinfo=si)
