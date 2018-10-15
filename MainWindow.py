import sys
import qdarkstyle

from threading import Thread
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt
from modules.UI.MenuBar import MenuBar
from modules.UI.StatusBar import StatusBar
from modules.UI.PrototpyeTable import PrototypeTable

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        import platform
        self.env = platform.system() + platform.release()
        if self.env != "Windows7" and self.env != "Windows10":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Not Supported")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()
        self.w = self.width()
        self.h = self.height()
        self.initUI()

    def initUI(self):
        # Set up default UI
        self.setWindowTitle("Monkey Spanner")
        self.setWindowIcon(QIcon("img/logo.png"))
        self.setMinimumSize(self.width(), self.height()*2)
        self.setMenuBar(MenuBar())
        self.setStatusBar(StatusBar())

        # Set up radio button (Select Software)
        self.layout = QVBoxLayout()
        groupBox = QGroupBox("Select Software", self)
        radioLayout = QHBoxLayout()
        groupBox.setLayout(radioLayout)
        groupBox.move(10, 20)
        groupBox.resize(self.w * 2, 65)
        self.btnFlash = QRadioButton('Adobe Flash Player', self)
        self.btnFlash.toggled.connect(lambda: self.toggledRadioBtn(self.btnFlash))
        radioLayout.addWidget(self.btnFlash)
        self.btnHWP = QRadioButton('HWP')
        self.btnHWP.toggled.connect(lambda: self.toggledRadioBtn(self.btnHWP))
        radioLayout.addWidget(self.btnHWP)
        self.btnIE = QRadioButton('Internet Explorer')
        self.btnIE.setChecked(True)
        self.btnIE.toggled.connect(lambda: self.toggledRadioBtn(self.btnIE))
        radioLayout.addWidget(self.btnIE)
        self.btnOffice = QRadioButton('MS-Office')
        self.btnOffice.toggled.connect(lambda: self.toggledRadioBtn(self.btnOffice))
        radioLayout.addWidget(self.btnOffice)
        self.btnPDF = QRadioButton('PDF')
        self.btnPDF.toggled.connect(lambda: self.toggledRadioBtn(self.btnPDF))
        radioLayout.addWidget(self.btnPDF)
        self.layout.addWidget(groupBox)

        # Set up text box for Search
        self.search = QLineEdit(self)
        self.search.move(10, 100)
        self.search.setFixedWidth(groupBox.width())
        self.search.setPlaceholderText("Filtering...")
        self.search.editingFinished.connect(self.enterPressed)
        self.search.textChanged.connect(self.textChanged)
        self.layout.addWidget(self.search)

        # self.t = Thread(target=self.loading)
        # self.t.start()
        # Set up table
        self.table = PrototypeTable(3, self.env)
        self.table.setParent(self)
        # self.table.hide()
        self.table.initUI()
        self.table.move(0, 110 + self.search.height())
        self.table.resize(self.search.width() + 20, self.h + 100)

        self.layout.addWidget(self.table)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.showMaximized()

    def loading(self):
        from time import sleep
        self.label = QLabel(self)
        loadingGif = QMovie('img/loading1.gif')
        self.label.setMovie(loadingGif)
        self.label.move(0, 110 + self.search.height())
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        loadingGif.start()
        # self.table.show()
        # self.layout.removeWidget(label)

    def toggledRadioBtn(self, b):
        msg = b.text()
        if self.btnFlash.isChecked():
            print(msg + " is checked")
        elif self.btnHWP.isChecked():
            print(msg + " is checked")
        elif self.btnIE.isChecked():
            print(msg + " is checked")
        elif self.btnOffice.isChecked():
            print(msg + " is checked")
        elif self.btnPDF.isChecked():
            print(msg + " is checked")
        self.statusBar().showMessage(msg + " is checked")

    def textChanged(self):
        print("Text Changed: " + self.search.text())

    def enterPressed(self):
        print("Entered: " + self.search.text())

if __name__ == "__main__":
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Failed")
        msg.setText("Not administrator")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(sys.exit)
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = Main()
    sys.exit(app.exec_())