from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog


class NTFSLogFileDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
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
        self.importMFTBtn.clicked.connect(self.MFTBtnClicked)
        self.importMFTBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.importUsnJrnlBtn = QPushButton("...", self)
        self.importUsnJrnlBtn.clicked.connect(self.UsnJrnlBtnClicked)
        self.importUsnJrnlBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.importLogFileBtn = QPushButton("...", self)
        self.importLogFileBtn.clicked.connect(self.LogFileBtnClicked)
        self.importLogFileBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.completeBtn = QPushButton("Submit", self)
        # self.setFixedSize(200, 40)
        self.completeBtn.setCursor(QCursor(Qt.PointingHandCursor))

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
        self.layout.addWidget(self.completeBtn, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.loadingBar)

        self.setWindowModality(Qt.WindowModal)
        self.show()

    def MFTBtnClicked(self):
        self.btnClicked(1)

    def UsnJrnlBtnClicked(self):
        self.btnClicked(2)

    def LogFileBtnClicked(self):
        self.btnClicked(3)

    def btnClicked(self, type):
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        options = QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getOpenFileName(self)
        # fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                           "All Files (*)", options=options)
        if type == 1:
            self.mftPathTextBox.setText(fileName[0])
        elif type == 2:
            self.usnjrnlPathTextBox.setText(fileName[0])
        elif type == 3:
            self.logfilePathTextBox.setText(fileName[0])

    def resume(self):
        if self.barThread.cnt < 50:
            self.barThread.cnt = 100
            return
        self.barThread.toggle_status()

    def clear(self):
        self.accept()
