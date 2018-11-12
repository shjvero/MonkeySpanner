from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QApplication, QTableWidgetItem, QFormLayout, \
    QAbstractItemView


class NTFSDetailViewer(QWidget):
    def __init__(self, contents):
        super(NTFSDetailViewer, self).__init__()
        self.initUI(contents)

    def initUI(self, contents):
        self.setWindowTitle("NTFS Detail Viewer")
        self.setMinimumWidth(750)

        self.layout = QFormLayout(self)

        self.label1 = QLabel("- MFT Entry Detail", self)
        self.label1.setFixedWidth(320)
        self.label2 = QLabel("- USN Record Detail", self)
        self.label3 = QLabel("- File Name Attribute in MFT", self)
        self.label3.setFixedHeight(20)
        self.label3.setAlignment(Qt.AlignBottom)
        self.label4 = QLabel(self)
        self.label4.setFixedHeight(20)
        self.label4.setAlignment(Qt.AlignBottom)

        self.table1 = QTableWidget(self)
        self.table1.setFixedSize(300, 130)
        self.table1.verticalHeader().setVisible(False)
        self.table1.verticalHeader().setDefaultSectionSize(25)
        self.table1.verticalHeader().setMaximumSectionSize(25)
        self.table1.horizontalHeader().setVisible(False)
        self.table1.setRowCount(5)
        self.table1.setColumnCount(2)
        self.table1.setItem(0, 0, QTableWidgetItem("MFT Entry Number  "))
        self.table1.setItem(1, 0, QTableWidgetItem("Sequence Value"))
        self.table1.setItem(2, 0, QTableWidgetItem("Base Entry"))
        self.table1.setItem(3, 0, QTableWidgetItem("Currently In Use"))
        self.table1.setItem(4, 0, QTableWidgetItem("MFT LSN"))
        for i in range(len(contents[0])-1):
            self.table1.setItem(i, 1, QTableWidgetItem(contents[0][i]))
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table1.resizeColumnsToContents()
        for c in range(self.table1.columnCount()):
            self.table1.setColumnWidth(c, 180)
        self.table1.verticalHeader().setStretchLastSection(True)
        self.table1.horizontalHeader().setStretchLastSection(True)

        self.table2 = QTableWidget(self)
        self.table2.setMinimumWidth(280)
        self.table2.setFixedHeight(130)
        self.table2.verticalHeader().setVisible(False)
        self.table2.verticalHeader().setDefaultSectionSize(25)
        self.table2.verticalHeader().setMaximumSectionSize(25)
        self.table2.horizontalHeader().setVisible(False)
        self.table2.setRowCount(5)
        self.table2.setColumnCount(2)
        self.table2.setItem(0, 0, QTableWidgetItem("USN"))
        self.table2.setItem(1, 0, QTableWidgetItem("File Name"))
        self.table2.setItem(2, 0, QTableWidgetItem("Timestamp"))
        self.table2.setItem(3, 0, QTableWidgetItem("Reason"))
        self.table2.setItem(4, 0, QTableWidgetItem("File Attributes   "))
        for i in range(len(contents[1])):
            self.table2.setItem(i, 1, QTableWidgetItem(contents[1][i]))
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table2.resizeColumnsToContents()
        self.table2.verticalHeader().setStretchLastSection(True)
        self.table2.horizontalHeader().setStretchLastSection(True)

        if contents[0][-1]:
            attributes = contents[0][-1]
            self.table3 = QTableWidget(self)
            self.table3.setFixedHeight(115)
            self.table3.verticalHeader().setVisible(False)
            self.table3.verticalHeader().setDefaultSectionSize(28)
            self.table3.verticalHeader().setMaximumSectionSize(28)
            self.table3.setRowCount(len(contents[0][-1]))
            self.table3.setColumnCount(5)
            self.table3.setHorizontalHeaderLabels([
                "File Name",
                "File Created Time",
                "File Modified Time",
                "MFT Modified Time",
                "File Accessed Time"
            ])
            for row in range(len(attributes)):
                self.table3.setItem(row, 0, QTableWidgetItem(attributes[row][0]))
                self.table3.setItem(row, 1, QTableWidgetItem(attributes[row][1]))
                self.table3.setItem(row, 2, QTableWidgetItem(attributes[row][2]))
                self.table3.setItem(row, 3, QTableWidgetItem(attributes[row][3]))
                self.table3.setItem(row, 4, QTableWidgetItem(attributes[row][4]))
                for c in range(5):
                    self.table3.item(row, c).setTextAlignment(Qt.AlignCenter)
            self.table3.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.table3.resizeColumnsToContents()
            self.table3.verticalHeader().setStretchLastSection(True)
            self.table3.horizontalHeader().setStretchLastSection(True)
        else:
            self.table3 = QLabel("None")
            self.table3.setFixedHeight(40)
            self.table3.setFixedWidth(self.width())
            self.table3.setAlignment(Qt.AlignCenter)

        if len(contents) == 3:
            self.label4.setText("- LogFile Transaction Number: {}".format(contents[-1][0]))
            self.table4 = QTableWidget(self)
            self.table4.verticalHeader().setVisible(False)
            self.table4.verticalHeader().setDefaultSectionSize(25)
            self.table4.verticalHeader().setMaximumSectionSize(25)
            self.table4.setRowCount(len(contents[2][1]))
            self.table4.setColumnCount(3)
            self.table4.setHorizontalHeaderLabels(["LSN", "Redo Operation", "Undo Operation"])
            self.table4.setColumnWidth(0, 120)
            self.table4.setColumnWidth(1, 300)
            self.table4.setColumnWidth(2, 300)
            row = 0
            for lsn, redo_op, undo_op in contents[2][1]:
                self.table4.setItem(row, 0, QTableWidgetItem(str(lsn)))
                self.table4.setItem(row, 1, QTableWidgetItem(redo_op))
                self.table4.setItem(row, 2, QTableWidgetItem(undo_op))
                self.table4.item(row, 0).setTextAlignment(Qt.AlignCenter)
                row += 1
            self.table4.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.label4.setText("- LogFile Transaction Number:")
            self.table4 = QLabel("None")
            self.table4.setFixedHeight(60)
            self.table4.setFixedWidth(self.width())
            self.table4.setAlignment(Qt.AlignCenter)
            self.table4.horizontalHeader().setStretchLastSection(True)

        self.layout.addRow(self.label1, self.label2)
        self.layout.addRow(self.table1, self.table2)
        self.layout.addRow(self.label3)
        self.layout.addRow(self.table3)
        self.layout.addRow(self.label4)
        self.layout.addRow(self.table4)

        self.show()
