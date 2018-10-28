import sys
import qdarkstyle

from PyQt5.QtGui import QIcon, QPixmap, QMovie, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt
from modules.UI.MenuBar import MenuBar
from modules.UI.StatusBar import StatusBar
from modules.UI.PrototpyeTable import PrototypeTable

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
        self.loadingImgPath = "img/loading2.gif"
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
            QCheckBox('Filtering D', self),
            QCheckBox('Filtering E', self),
            QCheckBox('Filtering F', self),
            QCheckBox('Filtering G', self),
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
        self.table = PrototypeTable(self.env)
        self.table.setParent(self)
        self.table.move(0, 110 + self.search.height())
        self.table.resize(self.search.width() + 20, self.h + 100)
        self.layout.addWidget(self.table)

        # Set up loading
        self.loadingWidget = QWidget(self)
        loadingLayout = QFormLayout()
        self.loadingMovie = QMovie(self.loadingImgPath)
        self.loadingImg = QLabel(self.loadingWidget)
        self.loadingImg.setMovie(self.loadingMovie)
        self.loadingImg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.loadingImg.setAlignment(Qt.AlignCenter)
        self.loadingWidget.show()
        loadingLayout.addWidget(self.loadingImg)

        self.loadingBar = QProgressBar(self.loadingWidget)
        self.loadingBar.setFixedSize(self.w, 20)
        self.loadingBar.setTextVisible(False)
        loadingLayout.addWidget(self.loadingBar)

        self.loadingWidget.setLayout(loadingLayout)
        self.loadingWidget.move(self.w/2, 180 + self.search.height())
        self.loadingWidget.setFixedSize(self.w, self.h/2)
        self.loadingWidget.setStyleSheet("background-color: transparent;")
        self.loadingWidget.hide()

        self.setLayout(self.layout)
        self.showMaximized()

    def selectSoftware(self, i):
        if i == 0: return
        self.selected = i

    def completeSelection(self):
        if self.isLoaded: return
        self.isLoaded = True
        self.table.setGraphicsEffect(QGraphicsBlurEffect())
        self.loadingMovie.start()
        self.loadingWidget.show()

        for i in range(1, 51):
            self.loadingBar.setValue(i)
        # self.table.load(self.selected, self.timeline)
        self.statusBar().showMessage("Ready!")
        for i in range(51, 101):
            self.loadingBar.setValue(i)

        self.timeline = None
        self.loadingWidget.hide()
        self.loadingMovie.stop()
        self.table.setGraphicsEffect(None)
        self.isLoaded = False
        self.presentSelected = self.selected

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