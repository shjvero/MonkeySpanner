from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, \
    QGroupBox, QCheckBox, QHBoxLayout, QSpacerItem

class NTFSLogFileDialog(QDialog, QObject):
    complete = pyqtSignal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        QObject.__init__(self)
        self.selectedPartition = -1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Import File System Log File")
        # self.setFixedSize(570, 300)
        self.setFixedSize(self.sizeHint())
        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.spacerItem1 = QSpacerItem(10, 5)
        self.layout.addItem(self.spacerItem1)
        self.setLayout(self.layout)

        # First Group
        self.diskRawChkBox = QCheckBox("In this case, it's possible to carve some files.", self)
        self.diskRawChkBox.stateChanged.connect(lambda: self.selectedType(self.diskRawChkBox))
        self.diskRawGroupBox = QGroupBox(self)
        self.diskRawGroupBox.setStyleSheet("margin-top: 0;")
        self.diskRawGroupBox.setDisabled(True)
        diskRawGroupBoxLayout = QHBoxLayout(self.diskRawGroupBox)
        self.diskRawGroupBox.setLayout(diskRawGroupBoxLayout)

        self.diskRawLabel = QLabel("Disk Raw: ", self)
        self.diskRawTextBox = QLineEdit()
        self.diskRawTextBox.setReadOnly(True)
        self.diskRawTextBox.setFixedWidth(400)

        self.browseDiskRawBtn = QPushButton("...", self)
        self.browseDiskRawBtn.setFixedWidth(50)
        self.browseDiskRawBtn.clicked.connect(self.btnClicekd)
        self.browseDiskRawBtn.setCursor(QCursor(Qt.PointingHandCursor))

        diskRawGroupBoxLayout.addWidget(self.diskRawLabel)
        diskRawGroupBoxLayout.addWidget(self.diskRawTextBox)
        diskRawGroupBoxLayout.addWidget(self.browseDiskRawBtn)

        self.layout.addWidget(self.diskRawChkBox)
        self.layout.addWidget(self.diskRawGroupBox)

        # Second Group
        self.ntfsLogFileChkBox = QCheckBox("In this case, NTFS Log analysis only supported.", self)
        self.ntfsLogFileChkBox.stateChanged.connect(lambda: self.selectedType(self.ntfsLogFileChkBox))

        self.ntfsLogGroupBox = QGroupBox(self)
        self.ntfsLogGroupBox.setStyleSheet("margin-top: 0;")
        self.ntfsLogGroupBox.setDisabled(True)
        ntfsLogGroupBoxLayout = QGridLayout(self)
        self.ntfsLogGroupBox.setLayout(ntfsLogGroupBoxLayout)

        self.mftLabel = QLabel("$MFT: ", self)
        self.mftPathTextBox = QLineEdit(self)
        self.mftPathTextBox.setReadOnly(True)
        self.mftPathTextBox.setFixedWidth(400)
        self.browseMFTBtn = QPushButton("...", self)
        self.browseMFTBtn.setFixedWidth(50)
        self.browseMFTBtn.clicked.connect(self.btnClicekd)
        self.browseMFTBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.usnjrnlLabel = QLabel("$UsnJrnl: ", self)
        self.usnjrnlPathTextBox = QLineEdit(self)
        self.usnjrnlPathTextBox.setReadOnly(True)
        self.usnjrnlPathTextBox.setFixedWidth(400)
        self.browseUsnJrnlBtn = QPushButton("...", self)
        self.browseUsnJrnlBtn.setFixedWidth(50)
        self.browseUsnJrnlBtn .clicked.connect(self.btnClicekd)
        self.browseUsnJrnlBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.logfileLabel = QLabel("$LogFile: ", self)
        self.logfilePathTextBox = QLineEdit(self)
        self.logfilePathTextBox.setReadOnly(True)
        self.logfilePathTextBox.setFixedWidth(400)
        self.browseLogFileBtn = QPushButton("...", self)
        self.browseLogFileBtn.setFixedWidth(50)
        self.browseLogFileBtn .clicked.connect(self.btnClicekd)
        self.browseLogFileBtn.setCursor(QCursor(Qt.PointingHandCursor))

        ntfsLogGroupBoxLayout.addWidget(self.mftLabel, 0, 0)
        ntfsLogGroupBoxLayout.addWidget(self.mftPathTextBox, 0, 1)
        ntfsLogGroupBoxLayout.addWidget(self.browseMFTBtn, 0, 2)
        ntfsLogGroupBoxLayout.addWidget(self.usnjrnlLabel, 1, 0)
        ntfsLogGroupBoxLayout.addWidget(self.usnjrnlPathTextBox, 1, 1)
        ntfsLogGroupBoxLayout.addWidget(self.browseUsnJrnlBtn, 1, 2)
        ntfsLogGroupBoxLayout.addWidget(self.logfileLabel, 2, 0)
        ntfsLogGroupBoxLayout.addWidget(self.logfilePathTextBox, 2, 1)
        ntfsLogGroupBoxLayout.addWidget(self.browseLogFileBtn, 2, 2)

        self.submitBtn = QPushButton("Submit", self)
        self.submitBtn.setFixedSize(100, 40)
        self.submitBtn.setCursor(QCursor(Qt.PointingHandCursor))

        self.loggingLabel = QLabel("Loading...", self)
        self.loggingLabel.setFixedHeight(20)
        self.loggingLabel.setAlignment(Qt.AlignCenter)
        self.loggingLabel.hide()

        self.loadingBar = QProgressBar(self)
        self.loadingBar.setFixedHeight(10)
        self.loadingBar.setTextVisible(False)
        self.loadingBar.hide()

        from modules.UI.LoadingScreen import LoadingBarThread
        self.barThread = LoadingBarThread(self)
        self.barThread.change_value.connect(self.loadingBar.setValue)

        self.spacerItem2 = QSpacerItem(10, 15)
        self.spacerItem3 = QSpacerItem(10, 20)
        self.layout.addItem(self.spacerItem2)
        self.layout.addWidget(self.ntfsLogFileChkBox)
        self.layout.addWidget(self.ntfsLogGroupBox)
        self.layout.addItem(self.spacerItem3)
        self.layout.addWidget(self.submitBtn, alignment=Qt.AlignHCenter)

        self.setWindowModality(Qt.WindowModal)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def selectedType(self, b):
        if b is self.diskRawChkBox:
            if b.isChecked():
                self.ntfsLogFileChkBox.setChecked(False)
                self.ntfsLogGroupBox.setDisabled(True)
                self.diskRawGroupBox.setDisabled(False)
            else:
                self.diskRawGroupBox.setDisabled(True)
        else:
            if b.isChecked():
                self.diskRawChkBox.setChecked(False)
                self.diskRawGroupBox.setDisabled(True)
                self.ntfsLogGroupBox.setDisabled(False)
            else:
                self.ntfsLogGroupBox.setDisabled(True)

    def btnClicekd(self):
        sender = self.sender()
        fileName = QFileDialog.getOpenFileName(self)
        if sender is self.browseDiskRawBtn:
            self.diskRawTextBox.setText(fileName[0])
        elif sender is self.browseMFTBtn:
            self.mftPathTextBox.setText(fileName[0])
        elif sender is self.browseUsnJrnlBtn:
            self.usnjrnlPathTextBox.setText(fileName[0])
        elif sender is self.browseLogFileBtn:
            self.logfilePathTextBox.setText(fileName[0])

    def ready(self):
        self.submitBtn.hide()
        self.layout.removeWidget(self.submitBtn)
        self.layout.addWidget(self.loggingLabel, alignment=Qt.AlignBottom | Qt.AlignHCenter)
        self.layout.addWidget(self.loadingBar)
        self.loggingLabel.show()
        self.loadingBar.show()
        self.barThread.start()

    def resume(self):
        if self.barThread.cnt < 50:
            self.barThread.cnt = 100
            return
        self.barThread.toggle_status()

    def changeInterface(self, contents):
        from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

        self.layout.removeWidget(self.diskRawChkBox)
        self.diskRawChkBox.hide()
        self.layout.removeWidget(self.diskRawGroupBox)
        self.diskRawGroupBox.hide()
        self.layout.removeItem(self.spacerItem2)
        self.layout.removeWidget(self.ntfsLogFileChkBox)
        self.ntfsLogFileChkBox.hide()
        self.layout.removeWidget(self.ntfsLogGroupBox)
        self.ntfsLogGroupBox.hide()
        self.layout.removeItem(self.spacerItem3)
        self.layout.removeWidget(self.submitBtn)

        self.diskNameLabel = QLabel("Image Name:\t" + contents[0][0], self)
        self.diskSizeLabel = QLabel("Image Size:\t{} Bytes".format(contents[0][1]), self)
        self.diskSizeLabel.setFixedHeight(20)
        self.diskSizeLabel.setAlignment(Qt.AlignVCenter)
        self.diskPartLabel = QLabel("Partition:", self)
        self.diskPartLabel.setFixedHeight(20)
        self.diskPartLabel.setAlignment(Qt.AlignBottom)

        self.partitionTree = QTreeWidget(self)
        self.partitionTree.setHeaderLabels(
            ["Order", "File System", "Active", "Starting Offset", "Total Sector", "Size"])
        self.partitionTree.itemChanged.connect(self.itemChanged)
        self.partitionTree.resizeColumnToContents(2)
        self.partitionTree.resizeColumnToContents(3)
        self.partitionTree.resizeColumnToContents(4)
        self.partitionTree.headerItem().setTextAlignment(0, Qt.AlignCenter)
        self.partitionTree.headerItem().setTextAlignment(1, Qt.AlignCenter)

        self.partitionItems = []
        for row in range(1, 5):
            self.partitionTree.headerItem().setTextAlignment(row + 1, Qt.AlignCenter)
            item = QTreeWidgetItem(self.partitionTree)
            item.setText(0, str(row))
            item.setTextAlignment(0, Qt.AlignLeft)
            if not contents[row]:
                item.setText(1, "None")
                item.setCheckState(0, Qt.Unchecked)
                item.setDisabled(True)
                continue
            for col in range(5):
                item.setText(col + 1, contents[row][col])
                item.setTextAlignment(col + 1, Qt.AlignCenter)
            item.setTextAlignment(1, Qt.AlignLeft)
            item.setCheckState(0, Qt.Unchecked)
            self.partitionItems.append(item)

        self.layout.addWidget(self.diskNameLabel)
        self.layout.addWidget(self.diskSizeLabel)
        self.layout.addWidget(self.diskPartLabel)
        self.layout.addWidget(self.partitionTree)
        self.layout.addItem(QSpacerItem(10, 10))
        self.layout.addWidget(self.submitBtn, alignment=Qt.AlignCenter)


    def itemChanged(self, changedItem, p_int):
        if changedItem.checkState(0) == Qt.Checked:
            self.selectedPartition = int(changedItem.text(0))
            for item in self.partitionItems:
                if item is not changedItem:
                    item.setCheckState(0, Qt.Unchecked)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    import qdarkstyle
    app = QApplication(sys.argv)
    w = NTFSLogFileDialog()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())