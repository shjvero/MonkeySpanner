from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog

class NTFSLogFileDialog(QDialog, QObject):
    complete = pyqtSignal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        QObject.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Import File System Log File")
        self.setFixedSize(self.sizeHint())
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.gridlayout = QGridLayout(self)
        self.layout.addLayout(self.gridlayout)
        self.setLayout(self.layout)

        # Set up Label
        self.mftLabel = QLabel("$MFT: ", self)
        self.usnjrnlLabel = QLabel("$UsnJrnl: ", self)
        self.logfileLabel = QLabel("$LogFile: ", self)

        # Set up TextBox
        self.mftPathTextBox = QLineEdit(self)
        self.mftPathTextBox.setReadOnly(True)
        self.mftPathTextBox.setFixedWidth(400)
        self.usnjrnlPathTextBox = QLineEdit(self)
        self.usnjrnlPathTextBox.setReadOnly(True)
        self.usnjrnlPathTextBox.setFixedWidth(400)
        self.logfilePathTextBox = QLineEdit(self)
        self.logfilePathTextBox.setReadOnly(True)
        self.logfilePathTextBox.setFixedWidth(400)

        # Set up Button
        self.importMFTBtn = QPushButton("...", self)
        self.importMFTBtn.clicked.connect(self.btnClicekd_byTest)
        self.importMFTBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.importUsnJrnlBtn = QPushButton("...", self)
        self.importUsnJrnlBtn .clicked.connect(self.btnClicekd_byTest)
        self.importUsnJrnlBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.importLogFileBtn = QPushButton("...", self)
        self.importLogFileBtn .clicked.connect(self.btnClicekd_byTest)
        self.importLogFileBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.submitBtn = QPushButton("Submit", self)
        self.submitBtn.setFixedSize(100, 40)
        self.submitBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # logging
        self.loggingLabel = QLabel("Loading...", self)
        self.loggingLabel.setFixedHeight(20)
        self.loggingLabel.setAlignment(Qt.AlignBottom)
        self.loggingLabel.hide()

        # Set up Progress Bar
        self.loadingBar = QProgressBar(self)
        self.loadingBar.setFixedHeight(10)
        self.loadingBar.setTextVisible(False)
        self.loadingBar.hide()

        from modules.UI.LoadingScreen import LoadingBarThread
        self.barThread = LoadingBarThread(self)
        self.barThread.change_value.connect(self.loadingBar.setValue)

        self.gridlayout.addWidget(self.mftLabel, 0, 0)
        self.gridlayout.addWidget(self.mftPathTextBox, 0, 1)
        self.gridlayout.addWidget(self.importMFTBtn, 0, 2)
        self.gridlayout.addWidget(self.usnjrnlLabel, 1, 0)
        self.gridlayout.addWidget(self.usnjrnlPathTextBox, 1, 1)
        self.gridlayout.addWidget(self.importUsnJrnlBtn, 1, 2)
        self.gridlayout.addWidget(self.logfileLabel, 2, 0)
        self.gridlayout.addWidget(self.logfilePathTextBox, 2, 1)
        self.gridlayout.addWidget(self.importLogFileBtn, 2, 2)
        self.layout.addWidget(self.submitBtn, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.loggingLabel, alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.layout.addWidget(self.loadingBar)

        self.setWindowModality(Qt.WindowModal)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def btnClicekd_byTest(self):
        sender = self.sender()
        fileName = QFileDialog.getOpenFileName(self)
        if sender is self.importMFTBtn:
            self.mftPathTextBox.setText(fileName[0])
        elif sender is self.importUsnJrnlBtn:
            self.usnjrnlPathTextBox.setText(fileName[0])
        elif sender is self.importLogFileBtn:
            self.logfilePathTextBox.setText(fileName[0])

    def ready(self):
        self.loggingLabel.show()
        self.loadingBar.show()
        self.barThread.start()

    def resume(self):
        if self.barThread.cnt < 50:
            self.barThread.cnt = 100
            return
        self.barThread.toggle_status()
