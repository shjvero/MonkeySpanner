import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtWidgets import *

from modules.UI.MenuBar import MenuBar
from modules.UI.PrototpyeTable import PrototypeTable
from modules.UI.LoadingScreen import LoadingWidget
from modules.UI.FilteringWidget import FilteringWidget
import modules.constant as CONSTANT

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checkEnv()
        self.w = self.width()
        self.h = self.height()
        self.topWidgetHeight = 35
        self.btnNumber = 0
        self.selected = 0
        self.presentSelected = 0
        self.isLoaded = False
        self.timeline = None
        self.pointerCursor = QCursor(Qt.PointingHandCursor)

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
        if self.env != CONSTANT.WIN7 and self.env != CONSTANT.WIN10:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Not Supported")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()

    def initUI(self):
        # Set up default UI
        self.setWindowTitle(CONSTANT.TITLE)
        self.setWindowIcon(QIcon(CONSTANT.ICON_PATH))
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(QStatusBar())

        # Set up Layout
        self.screenWidget = QWidget()
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self.screenWidget)
        self.windowLayout.addItem(QSpacerItem(10, 5))
        self.topLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.bottomLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.windowLayout.addLayout(self.topLayout)
        self.windowLayout.addLayout(self.bottomLayout)
        self.screenWidget.setLayout(self.windowLayout)
        self.setCentralWidget(self.screenWidget)

        # Set up combo box (Software Selection)
        self.selection = QComboBox(self)
        self.selection.setFont(QFont('Arial', 11))
        self.selection.setFixedHeight(self.topWidgetHeight)
        self.selection.addItems(CONSTANT.SOFTWARE_SELECTION)
        self.selection.currentIndexChanged.connect(self.selectSoftware)
        self.selection.setCursor(self.pointerCursor)

        # Set up Table Load Button
        self.loadBtn = QPushButton(self)
        self.loadBtn.setIcon(QIcon("img/logo.png"))
        self.loadBtn.setFixedSize(self.topWidgetHeight, self.topWidgetHeight)
        self.loadBtn.setStyleSheet("background-color: darkslategray;")
        self.loadBtn.clicked.connect(self.completeSelection)
        self.loadBtn.setCursor(self.pointerCursor)

        # Set up check box (Filtering)
        self.filteringBtn = QPushButton(self)
        self.filteringBtn.setIcon(QIcon("img/filter.png"))
        self.filteringBtn.setFixedSize(self.topWidgetHeight, self.topWidgetHeight)
        self.filteringBtn.setStyleSheet("background-color: lightsteelblue")
        self.filteringBtn.setShortcut("Ctrl+D")
        self.filteringBtn.clicked.connect(self.filtering)
        self.filteringBtn.setCursor(self.pointerCursor)

        # Set up text box for Search
        self.search = QLineEdit(self)
        self.search.setFixedHeight(self.topWidgetHeight)
        self.search.showMaximized()
        self.search.setFont(QFont("Arial", 12))
        self.search.setPlaceholderText("Search")
        self.search.returnPressed.connect(self.enterPressed)

        self.table = PrototypeTable(self, self.env)

        self.loadingWidget = LoadingWidget(self)
        self.loadingWidget.complete.connect(self.loadingFinished)

        self.filteringWidget = FilteringWidget()
        self.filteringWidget.itemChanged.connect(self.table.filter)


        self.topLayout.addWidget(self.selection)
        self.topLayout.addWidget(self.loadBtn)
        self.topLayout.addItem(QSpacerItem(10, self.topWidgetHeight))
        self.topLayout.addWidget(self.filteringBtn)
        self.topLayout.addItem(QSpacerItem(10, self.topWidgetHeight))
        self.topLayout.addWidget(self.search)
        self.bottomLayout.addWidget(self.table)

        self.showMaximized()

    def filtering(self):
        self.filteringWidget.show()

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

    def loadingFinished(self):
        self.presentSelected = self.selected
        self.timeline = None
        self.isLoaded = False
        self.loadingWidget.hide()
        self.bottomLayout.removeWidget(self.loadingWidget)
        self.bottomLayout.addWidget(self.table)
        self.table.show()

    def enterPressed(self):
        if self.isLoaded:
            return
        keyword = self.search.text()
        if not keyword:
            self.table.search(keyword, self.filteringWidget.presentCheckedItems())
        else:
            self.table.search(keyword)
