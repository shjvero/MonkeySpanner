import sys
import qdarkstyle
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtWidgets import *
from modules.UI.MenuBar import MenuBar
from modules.UI.StatusBar import StatusBar
from modules.UI.PrototpyeTable import PrototypeTable
from modules.UI.LoadingScreen import LoadingWidget

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checkEnv()
        self.w = self.width()
        self.h = self.height()
        self.selectionList = [
            "---- Select Software ----",
            "Adobe Reader", "Adobe Flash Player", "Chrome", "Edge", "HWP",
            "Internet Explorer", "MS-Office", "Kernel(Local Privilege Escalation)"
        ]
        self.selectionWidth = 220
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
        self.setWindowIcon(QIcon("img/favicon2.jpg"))
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(StatusBar())

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
        self.selection.setContentsMargins(10, 10, 10, 10)
        self.selection.setFont(QFont("Times New Roman", 12))
        self.selection.setFixedWidth(self.selectionWidth)
        self.selection.addItems(self.selectionList)
        self.selection.currentIndexChanged.connect(self.selectSoftware)

        # Set up Table Load Button
        self.loadBtn = QPushButton("GO!", self)
        self.loadBtn.setFixedSize(self.loadBtnWidth, self.selection.height())
        self.loadBtn.setStyleSheet("background-color: darkslategray;")
        self.loadBtn.clicked.connect(self.completeSelection)
        self.loadBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # Set up check box (Filtering)
        self.groupBox = QGroupBox(self)
        chkboxLayout = QHBoxLayout()
        self.groupBox.setLayout(chkboxLayout)
        self.options = [
            QCheckBox('Filtering A', self),
            QCheckBox('Filtering B', self),
            QCheckBox('Filtering C', self),
            QCheckBox('Filtering D', self),
            QCheckBox('Filtering E', self),
            QCheckBox('Filtering F', self),
        ]
        for option in self.options:
            option.stateChanged.connect(lambda: self.toggledChkBtn(option))
            chkboxLayout.addWidget(option)

        # Set up text box for Search
        self.search = QLineEdit(self)
        self.search.showMaximized()
        self.search.setPlaceholderText("Filtering...")
        self.search.editingFinished.connect(self.enterPressed)
        self.search.textChanged.connect(self.textChanged)

        # Set up loading
        self.loadingWidget = LoadingWidget(self)

        # Set up Table
        self.table = PrototypeTable(self, self.env)

        self.topLayout.addWidget(self.selection)
        self.topLayout.addWidget(self.loadBtn)
        self.topLayout.addWidget(self.groupBox)
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
        self.table.load(self.selected, self.timeline)
        self.loadingWidget.resume()
        self.presentSelected = self.selected
        self.timeline = None
        self.isLoaded = False
        self.bottomLayout.removeWidget(self.loadingWidget)
        self.bottomLayout.addWidget(self.table)
        self.table.show()

    def toggledChkBtn(self, b): # timeline set...?
        msg = b.text()
        if msg == "Filtering A":
            if self.filtering1.isChecked():
                msg += " is checked"
                self.btnNumber = 1
            else:
                msg += " isn't checked"
        elif msg == "Filtering B":
            if self.filtering2.isChecked():
                msg += " is checked"
                self.btnNumber = 2
            else:
                msg += " isn't checked"
        elif msg == "Filtering C":
            if self.filtering3.isChecked():
                msg += " is checked"
                self.btnNumber = 3
            else:
                msg += " isn't checked"
        self.statusBar().showMessage(msg)

    def textChanged(self):
        if self.isLoaded:
            return
        # print("Load End.")
        # self.table.search(self.search.text())

    def enterPressed(self):
        if self.isLoaded:
            return
        print("Load End.")
        self.table.search(self.search.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = Main()
    sys.exit(app.exec_())