from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *

class NTFSViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.w = self.width()
        self.h = self.height()
        self.usnjrnlTableHeaderItems = ['Timestamp',
                                        'USN',
                                        'File Name',
                                        'Full Path',
                                        'Reason',
                                        'File Attributes',
                                        'Source Info']
        self.logfileTableHeaderItems = ['LSN',
                                        'Type',
                                        'Redo Operation',
                                        'Undo Operation',
                                        'File Name',
                                        'Full Path',
                                        'Created Time',
                                        'Modified Time',
                                        'MFT Modified Time',
                                        'Accessed Time',
                                        'Cluster Index',
                                        'Target VCN']
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File System Log")
        self.setMinimumSize(self.w, self.h)

        # Layout
        self.windowLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.optionsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.windowLayout.addLayout(self.optionsLayout)

        # Set up Filtering
        self.groupBox = QGroupBox(self)
        chkLayout = QHBoxLayout()
        self.groupBox.setLayout(chkLayout)
        self.allChkBox = QCheckBox('ALL', self)
        self.createChkBox = QCheckBox('File Create', self)
        self.modifiyChkBox = QCheckBox('File Modifiy', self)
        self.deleteChkBox = QCheckBox('File Delete', self)
        chkLayout.addWidget(self.allChkBox)
        chkLayout.addWidget(self.createChkBox)
        chkLayout.addWidget(self.modifiyChkBox)
        chkLayout.addWidget(self.deleteChkBox)

        # Set up Button
        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.setFixedSize(120, self.groupBox.height())
        self.exportBtn.setStyleSheet("background-color: darkslategray;")
        self.exportBtn.clicked.connect(self.export)
        self.exportBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.carveBtn = QPushButton("Carving", self)
        self.carveBtn.setFixedSize(120, self.groupBox.height())
        self.carveBtn.setStyleSheet("background-color: darkslategray;")
        self.carveBtn.clicked.connect(self.carve)
        self.carveBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # Set up Text Box for Search
        self.search = QLineEdit(self)
        self.search.setFixedHeight(30)
        self.search.showMaximized()
        self.search.setPlaceholderText("Search")
        self.search.editingFinished.connect(self.enterPressed)

        # Set up UsnJrnl Table
        self.usnjrnlTable = QTableWidget()
        usnjrnlTableHeader = self.usnjrnlTable.verticalHeader()
        usnjrnlTableHeader.setDefaultSectionSize(28)
        usnjrnlTableHeader.setMaximumSectionSize(28)
        self.usnjrnlTable.setColumnCount(7)
        self.usnjrnlTable.setHorizontalHeaderLabels(self.usnjrnlTableHeaderItems)
        self.usnjrnlTable.horizontalHeader().setStretchLastSection(True)
        self.usnjrnlTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.usnjrnlTable.verticalHeader().setVisible(False)

        # Set up LogFile Table
        self.logfileTable = QTableWidget()
        logfileTableHeader = self.logfileTable.verticalHeader()
        logfileTableHeader.setDefaultSectionSize(28)
        logfileTableHeader.setMaximumSectionSize(28)
        self.logfileTable.setColumnCount(7)
        self.logfileTable.setHorizontalHeaderLabels(self.logfileTableHeaderItems)
        self.logfileTable.horizontalHeader().setStretchLastSection(True)
        self.logfileTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.logfileTable.verticalHeader().setVisible(False)

        # Set up Tab Widget
        self.ntfsTabs = QTabWidget()
        self.ntfsTabs.addTab(self.usnjrnlTable, "$UsnJrnl")
        self.ntfsTabs.addTab(self.logfileTable, "$LogFile")

        self.optionsLayout.addWidget(self.groupBox)
        self.optionsLayout.addWidget(self.exportBtn)
        self.optionsLayout.addWidget(self.carveBtn)
        self.windowLayout.addWidget(self.search)
        self.windowLayout.addWidget(self.ntfsTabs)
        self.setLayout(self.windowLayout)
        # self.show()

    def loadData(self, usnjrnlArr, logFileArr):
        print(usnjrnlArr)
        print(logFileArr)

    def enterPressed(self):
        print(self.search.text())
        return

    def export(self):
        print(self.exportBtn.text())
        dialog = NTFSLogFileDialog(self)


    def carve(self):
        print(self.carveBtn.text())

class NTFSLogFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Import File System Log File")
        self.setFixedSize(self.sizeHint())
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.gridlayout = QGridLayout(self)
        self.layout.addLayout(self.gridlayout)
        self.setLayout(self.layout)

        self.mftLabel = QLabel("$MFT: ", self)
        self.usnjrnlLabel = QLabel("$UsnJrnl: ", self)
        self.logfileLabel = QLabel("$LogFile: ", self)

        self.mftPathTextBox = QLineEdit(self)
        self.mftPathTextBox.setReadOnly(True)
        self.mftPathTextBox.setFixedWidth(400)
        self.usnjrnlPathTextBox = QLineEdit(self)
        self.usnjrnlPathTextBox.setReadOnly(True)
        self.usnjrnlPathTextBox.setFixedWidth(400)
        self.logfilePathTextBox = QLineEdit(self)
        self.logfilePathTextBox.setReadOnly(True)
        self.logfilePathTextBox.setFixedWidth(400)

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
        self.completeBtn.clicked.connect(self.submit)

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
        self.setWindowModality(Qt.WindowModal)
        self.show()

    def MFTBtnClicked(self):
        self.btnClicked(1)

    def UsnJrnlBtnClicked(self):
        self.btnClicked(2)

    def LogFileBtnClicked(self):
        self.btnClicked(3)

    def btnClicked(self, type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*)", options=options)
        if type == 1:
            self.mftPathTextBox.setText(fileName)
        elif type == 2:
            self.usnjrnlPathTextBox.setText(fileName)
        elif type == 3:
            self.logfilePathTextBox.setText(fileName)

    def submit(self):
        print(self.mftPathTextBox.text())
        print(self.usnjrnlPathTextBox.text())
        print(self.logfilePathTextBox.text())
        # ntfsViewer = NTFSViewer(self.parent())
        # ntfsViewer.loadData(["TEST1", "TEST2", "TEST3"], ["ARR1", "ARR2", "ARR3"])
        # ntfsViewer.show()
        self.accept()

# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     w = NTFSViewer()
#     sys.exit(app.exec_())