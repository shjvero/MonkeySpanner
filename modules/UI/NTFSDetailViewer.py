from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QApplication, QTableWidgetItem, QFormLayout


class NTFSDetailViewer(QWidget):
    def __init__(self, contents):
        super(NTFSDetailViewer, self).__init__()
        self.initUI(contents)

    def initUI(self, contents):
        self.setWindowTitle("NTFS Detail Viewer")
        self.setMinimumWidth(self.width())
        # self.setMinimumSize(self.width(), self.height())

        self.layout = QFormLayout(self)

        self.label1 = QLabel("MFT Entry Detail", self)
        self.label1.setFixedWidth(270)
        self.label2 = QLabel("USN Record Detail", self)
        self.label3 = QLabel("LogFile Transaction Number: {}".format(contents[2][0]), self)
        self.label3.setFixedHeight(40)
        self.label3.setAlignment(Qt.AlignBottom)

        self.table1 = QTableWidget(self)
        self.table1.setFixedSize(250, 125)
        self.table1.verticalHeader().setVisible(False)
        self.table1.verticalHeader().setStretchLastSection(True)
        self.table1.horizontalHeader().setVisible(False)
        self.table1.horizontalHeader().setStretchLastSection(True)
        self.table1.setRowCount(4)
        self.table1.setColumnCount(2)
        self.table1.setItem(0, 0, QTableWidgetItem("MFT Entry Number"))
        self.table1.setItem(1, 0, QTableWidgetItem("Sequence Value"))
        self.table1.setItem(2, 0, QTableWidgetItem("Currently In Use"))
        self.table1.setItem(3, 0, QTableWidgetItem("File Name")) # Attributes 항목 따로,
        self.table1.resizeColumnsToContents()

        self.table2 = QTableWidget(self)
        self.table2.setFixedHeight(125)
        self.table2.verticalHeader().setVisible(False)
        self.table2.verticalHeader().setStretchLastSection(True)
        self.table2.horizontalHeader().setVisible(False)
        self.table2.horizontalHeader().setStretchLastSection(True)
        self.table2.setRowCount(4)
        self.table2.setColumnCount(2)
        self.table2.setItem(0, 0, QTableWidgetItem("USN"))
        self.table2.setItem(1, 0, QTableWidgetItem("File Name"))
        self.table2.setItem(2, 0, QTableWidgetItem("Timestamp"))
        self.table2.setItem(3, 0, QTableWidgetItem("Reason"))
        self.table2.resizeColumnsToContents()

        self.table3 = QTableWidget(self)
        self.table3.verticalHeader().setVisible(False)
        self.table2.verticalHeader().setStretchLastSection(True)
        self.table2.horizontalHeader().setStretchLastSection(True)
        self.table3.setRowCount(1)
        self.table3.setColumnCount(3)
        self.table3.setHorizontalHeaderLabels(["LSN", "Redo Operation", "Undo Operation"])
        # self.table3.resizeColumnsToContents()
        self.table3.setColumnWidth(0, 120)
        self.table3.setColumnWidth(1, 250)
        self.table3.setColumnWidth(2, 250)

        self.layout.addRow(self.label1,self.label2)
        self.layout.addRow(self.table1,self.table2)
        self.layout.addRow(self.label3)
        self.layout.addRow(self.table3)

        self.show()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = NTFSDetailViewer(["ASDA", "ASFAD", [35, 0]])
    sys.exit(app.exec_())