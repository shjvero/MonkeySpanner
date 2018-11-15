import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtWidgets import *

from modules.UI.MenuBar import MenuBar
from modules.UI.PrototpyeTable import PrototypeTable
from modules.UI.LoadingScreen import LoadingWidget
import modules.constant as CONSTANT

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checkEnv()
        self.w = self.width()
        self.h = self.height()
        self.topWidgetHeight = 40
        self.selectionList = [
            "---- Select Software ----",
            "Adobe Reader", "Adobe Flash Player", "Edge", "HWP",
            "Internet Explorer", "MS-Office", "Kernel(Local Privilege Escalation)"
        ]
        self.OPTIONS = ['None', 'Prefetch', 'Event Log', 'Registry', 'History', 'WebCache', 'WER', 'JumpList[L]', 'JumpList[D]']
        self.selectionWidth = 220
        self.btnNumber = 0
        self.loadBtnWidth = 100
        self.searchWidth = self.w * 2
        self.selected = 0
        self.presentSelected = 0
        self.isLoaded = False
        self.timeline = None

        self.initUI()

    def checkEnv(self):
        import platform, ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Failed")
            msg.setText("Not administrator")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()
        self.env = platform.system() + platform.release()
        if self.env != "Windows7" and self.env != "Windows10":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Not Supported")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()

    def initUI(self):
        # Set up default UI
        self.setWindowTitle("Monkey Spanner")
        self.setWindowIcon(QIcon("logo.ico"))
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(QStatusBar())

        # Set up Layout
        self.screenWidget = QWidget()
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self.screenWidget)
        self.topLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.bottomLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.windowLayout.addLayout(self.topLayout)
        self.windowLayout.addLayout(self.bottomLayout)
        self.screenWidget.setLayout(self.windowLayout)
        self.setCentralWidget(self.screenWidget)

        # Set up combo box (Software Selection)
        self.selection = QComboBox(self)
        self.selection.setFont(QFont('Arial', 12))
        self.selection.setFixedSize(self.selectionWidth, self.topWidgetHeight)
        self.selection.addItems(self.selectionList)
        self.selection.currentIndexChanged.connect(self.selectSoftware)

        # Set up Table Load Button
        self.loadBtn = QPushButton("GO!", self)
        self.loadBtn.setFixedSize(self.loadBtnWidth, self.topWidgetHeight)
        self.loadBtn.clicked.connect(self.completeSelection)
        self.loadBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # Set up check box (Filtering)
        self.groupBox = QGroupBox(self)
        self.groupBox.setFlat(True)
        chkboxLayout = QHBoxLayout()
        self.groupBox.setLayout(chkboxLayout)
        self.option1 = QCheckBox(self.OPTIONS[1])
        self.option1.stateChanged.connect(lambda: self.toggledChkBtn(self.option1))
        chkboxLayout.addWidget(self.option1)
        self.option2 = QCheckBox(self.OPTIONS[2])
        self.option2.stateChanged.connect(lambda: self.toggledChkBtn(self.option2))
        chkboxLayout.addWidget(self.option2)
        self.option3 = QCheckBox(self.OPTIONS[3])
        self.option3.stateChanged.connect(lambda: self.toggledChkBtn(self.option3))
        chkboxLayout.addWidget(self.option3)
        self.option4 = QCheckBox(self.OPTIONS[4])
        self.option4.stateChanged.connect(lambda: self.toggledChkBtn(self.option4))
        chkboxLayout.addWidget(self.option4)
        self.option5 = QCheckBox(self.OPTIONS[5])
        self.option5.stateChanged.connect(lambda: self.toggledChkBtn(self.option5))
        chkboxLayout.addWidget(self.option5)
        self.option6 = QCheckBox(self.OPTIONS[6])
        self.option6.stateChanged.connect(lambda: self.toggledChkBtn(self.option6))
        chkboxLayout.addWidget(self.option6)
        self.option7 = QCheckBox(self.OPTIONS[7])
        self.option7.stateChanged.connect(lambda: self.toggledChkBtn(self.option7))
        chkboxLayout.addWidget(self.option7)
        self.option8 = QCheckBox(self.OPTIONS[8])
        self.option8.stateChanged.connect(lambda: self.toggledChkBtn(self.option8))
        chkboxLayout.addWidget(self.option8)

        # Set up text box for Search
        self.search = QLineEdit(self)
        self.search.setFixedHeight(35)
        self.search.showMaximized()
        self.search.setPlaceholderText("Search")
        self.search.editingFinished.connect(self.enterPressed)

        self.loadingWidget = LoadingWidget(self)
        self.table = PrototypeTable(self, self.env)

        self.topLayout.addWidget(self.selection, alignment=Qt.AlignBottom)
        self.topLayout.addWidget(self.loadBtn, alignment=Qt.AlignBottom)
        self.topLayout.addWidget(self.groupBox, alignment=Qt.AlignBottom)
        self.bottomLayout.addWidget(self.search)
        self.bottomLayout.addWidget(self.table)
        self.showMaximized()

    def selectSoftware(self, i):
        self.selected = i

    def completeSelection(self):
        if self.isLoaded: return
        self.isLoaded = True
        self.bottomLayout.removeWidget(self.table)
        self.bottomLayout.addWidget(self.loadingWidget)
        self.table.hide()
        self.loadingWidget.start()
        from threading import Thread
        t = Thread(target=self.loadData, args=())
        t.start()

    def loadData(self):
        if self.table.prototype:
            self.table.prototype.clear()
            self.table.clearContents()
        self.table.load(self.selected, self.timeline)
        self.loadingWidget.resume()
        self.presentSelected = self.selected
        self.timeline = None
        self.isLoaded = False
        self.bottomLayout.removeWidget(self.loadingWidget)
        self.bottomLayout.addWidget(self.table)
        self.table.show()

        if self.presentSelected == CONSTANT.ADOBE_FLASH_PLAYER:
            print()
        elif self.presentSelected in [CONSTANT.IE, CONSTANT.EDGE]:
            self.option4.setDisabled(False)
            self.option5.setDisabled(False)
            self.option7.setDisabled(True)
            self.option8.setDisabled(True)
        elif self.presentSelected in [CONSTANT.ADOBE_READER, CONSTANT.OFFICE]:
            self.option4.setDisabled(True)
            self.option5.setDisabled(False)
            self.option7.setDisabled(False)
            self.option8.setDisabled(False)
        elif self.presentSelected == CONSTANT.HWP:
            self.option4.setDisabled(True)
            self.option5.setDisabled(True)

    def toggledChkBtn(self, b):
        msg = b.text()
        self.statusBar().showMessage(msg)
        if self.presentSelected == 0: return

        if msg == self.OPTIONS[1]:
            if self.option1.isChecked():
                if self.btnNumber:
                    self.table.filtering(1, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(1, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(1, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[2]:
            if self.option2.isChecked():
                if self.btnNumber:
                    self.table.filtering(2, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(2, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(2, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[3]:
            if self.option3.isChecked():
                if self.btnNumber:
                    self.table.filtering(3, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(3, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(3, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[4]:
            if self.option4.isChecked():
                if self.btnNumber:
                    self.table.filtering(4, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(4, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(4, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[5]:
            if self.option5.isChecked():
                if self.btnNumber:
                    self.table.filtering(5, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(5, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(5, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[6]:
            if self.option6.isChecked():
                if self.btnNumber:
                    self.table.filtering(6, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(6, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(6, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[7]:
            if self.option7.isChecked():
                if self.btnNumber:
                    self.table.filtering(7, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(7, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(7, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)
        elif msg == self.OPTIONS[8]:
            if self.option8.isChecked():
                if self.btnNumber:
                    self.table.filtering(8, PrototypeTable.ONLY_SHOW)
                else:
                    self.table.filtering(8, PrototypeTable.SIMPLE_SHOW)
                self.btnNumber += 1
            else:
                self.btnNumber -= 1
                if self.btnNumber:
                    self.table.filtering(8, PrototypeTable.ONLY_HIDE)
                else:
                    self.table.filtering(0)

    def enterPressed(self):
        if self.isLoaded:
            return
        if self.btnNumber:
            self.table.search(self.search.text(), True)
        else:
            self.table.search(self.search.text())
