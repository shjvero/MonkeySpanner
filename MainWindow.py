import sys
import qdarkstyle

from PyQt5.QtGui import QIcon, QPixmap, QMovie, QFont
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
        self.selected = 0
        self.presentSelected = 0
        self.isLoaded = False
        self.timeline = None
        self.setWindowTitle("Monkey Spanner")
        self.setWindowIcon(QIcon("img/favicon2.jpg"))
        # self.loadingImgPath = "img/loading.gif"
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
        self.setMinimumSize(self.width(), self.height()*2)
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(StatusBar())
        self.layout = QVBoxLayout()

        # Set up combo box (Software Selection)
        self.selection = QComboBox(self)
        self.selection.move(10, 45)
        self.selection.setFont(QFont("Times New Roman", 13))
        self.selection.setFixedWidth(220)
        self.selection.addItem("--- Select Software ---")
        self.selection.addItem("Adobe Reader")
        self.selection.addItem("Adobe Flash Player")
        self.selection.addItem("Chrome")
        self.selection.addItem("Edge")
        self.selection.addItem("HWP")
        self.selection.addItem("Internet Explorer")
        self.selection.addItem("MS-Office")
        self.selection.addItem("Local Privilege Escalation")
        self.selection.currentIndexChanged.connect(self.selectSoftware)

        # Set up Table Load Button
        self.loadBtn = QPushButton("GO!", self)
        self.loadBtn.move(self.selection.width() + 30, 45)
        self.loadBtn.setFixedSize(100, self.selection.height())
        self.loadBtn.clicked.connect(self.completeSelection)

        # Set up check box (Filtering)
        groupBox = QGroupBox("Filtering", self)
        chkboxLayout = QHBoxLayout()
        groupBox.setLayout(chkboxLayout)
        groupBox.move(400, 20)
        groupBox.resize(self.w + 220, 65)
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
        self.layout.addWidget(groupBox)

        # Set up text box for Search
        self.search = QLineEdit(self)
        self.search.move(10, 100)
        self.search.setFixedWidth(self.width()*2)
        self.search.setPlaceholderText("Filtering...")
        self.search.editingFinished.connect(self.enterPressed)
        self.search.textChanged.connect(self.textChanged)
        self.layout.addWidget(self.search)

        # Set up Table
        self.table = PrototypeTable(self, self.env)
        # self.table.setParent(self)
        self.table.move(0, 110 + self.search.height())
        self.table.resize(self.search.width() + 20, self.h + 100)
        self.layout.addWidget(self.table)

        # Set up loading
        self.loadingWidget = LoadingWidget(self)

        self.setLayout(self.layout)
        self.showMaximized()

    def selectSoftware(self, i):
        self.selected = i

    def completeSelection(self):
        if self.isLoaded: return
        self.isLoaded = True
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