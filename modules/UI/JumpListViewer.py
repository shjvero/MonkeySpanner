import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *

class JumpListViewer(QWidget):
    def __init__(self, hashList):
        super().__init__()
        self.hashList = hashList
        self.w = self.width()
        self.h = self.height()
        self.tableWidth = 600
        self.tableHeight = 220
        self.listViewWidth = 180
        self.listViewHeight = self.tableHeight * 2 - 30
        self.tableLeft = self.listViewWidth + 25
        self.windowWidth = self.tableWidth + self.tableLeft + 20
        self.windowHeight = self.listViewHeight + 40
        self.linkFileHeader = ["Modified Time", "Accessed Time", "Created Time", "LocalBasePath", "Size", "E.No.",
             "Drive Type", "VolumnName", "Serial No."]
        self.destListHeader = ["Last Recorded Access", "Data", "E.No.", "Access Count", "NetBIOSName", "New (Timestamp)",
             "New (MAC)", "Seq No.", "Birth (Timestamp)", "Birth (MAC)"]
        self.selected = -1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JumpList")
        self.setWindowIcon(QIcon("../../img/logo.png"))
        self.setMinimumSize(self.windowWidth, self.windowHeight)

        self.hashTitleLabel = QLabel("Hash: ", self)
        self.hashTitleLabel.move(10, 20)

        self.hashLabel = QLabel(self)
        self.hashLabel.move(10, 40)
        self.hashLabel.setFixedWidth(self.listViewWidth)
        self.hashLabel.setAlignment(Qt.AlignCenter)

        self.hashListView = QListView(self)
        self.model = QStandardItemModel()
        for h in self.hashList:
            self.model.appendRow(QStandardItem(h[0]))
        self.hashListView.setModel(QStandardItemModel())
        self.hashListView.move(10, 60)
        self.hashListView.resize(self.listViewWidth, self.listViewHeight)
        self.hashListView.clicked.connect(self.selectedHash)
        self.hashListView.setModel(self.model)

        self.exportBtn = QPushButton("Export as CSV", self)
        self.exportBtn.move(10, self.hashTitleLabel.height() + self.hashLabel.height() + self.listViewHeight + 10)
        self.exportBtn.setFixedSize(self.listViewWidth, 40)
        self.exportBtn.setStyleSheet("background-color: darkslategray;")
        self.exportBtn.clicked.connect(self.btnClicked)

        self.label1 = QLabel("Link Files:", self)
        self.label1.move(self.tableLeft+10, 20)
        self.LinkFilesTable = QTableWidget(self)
        self.LinkFilesTable.move(self.tableLeft, 40)
        self.LinkFilesTable.setMinimumSize(self.tableWidth, self.tableHeight)
        self.LinkFilesTable.verticalHeader().setDefaultSectionSize(28)
        self.LinkFilesTable.verticalHeader().setMaximumSectionSize(28)
        self.LinkFilesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LinkFilesTable.verticalHeader().setVisible(False)
        self.LinkFilesTable.setColumnCount(len(self.linkFileHeader))
        self.LinkFilesTable.setHorizontalHeaderLabels(self.linkFileHeader)

        self.label2 = QLabel("Dest List:", self)
        self.label2.move(self.tableLeft + 10, self.LinkFilesTable.height() + 60)
        self.DestListTable = QTableWidget(self)
        self.DestListTable.move(self.tableLeft, self.LinkFilesTable.height() + 80)
        self.DestListTable.setMinimumSize(self.tableWidth, self.tableHeight)
        self.DestListTable.verticalHeader().setDefaultSectionSize(28)
        self.DestListTable.verticalHeader().setMaximumSectionSize(28)
        self.DestListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.DestListTable.verticalHeader().setVisible(False)
        self.DestListTable.setColumnCount(len(self.destListHeader))
        self.DestListTable.setHorizontalHeaderLabels(self.destListHeader)

        self.show()

    def selectedHash(self, i):
        self.selected = self.model.itemFromIndex(i).row()
        self.hashLabel.setText(self.hashList[self.selected][1])
        self.loadData(self.hashList[self.selected][2])

    def loadData(self, logList):
        LinkFiles = logList["LinkFiles"]
        DestList = logList["DestList"]
        self.LinkFilesTable.clearContents()
        self.LinkFilesTable.setRowCount(len(LinkFiles))
        self.DestListTable.clearContents()
        self.DestListTable.setRowCount(len(DestList))
        r = 0
        for item in LinkFiles:
            for c in range(self.LinkFilesTable.columnCount()):
               self.LinkFilesTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1
        r = 0
        for item in DestList:
            for c in range(self.DestListTable.columnCount()):
               self.DestListTable.setItem(r, c, QTableWidgetItem(item[c]))
            r += 1
        self.LinkFilesTable.resizeColumnsToContents()

        self.DestListTable.resizeColumnsToContents()

    def btnClicked(self):
        print(self.selected)
        if self.selected == -1:
            print("Please select in above list.")
            # from PyQt5.QtWidgets import QMessageBox
            # msg = QMessageBox(self)
            # msg.setIcon(QMessageBox.Help)
            # msg.setWindowTitle("Help")
            # msg.setText("Please select in above list.")
            # msg.setStandardButtons(QMessageBox.Ok)
            # msg.exec_()
            return
        self.export()
        # print("Call Thread")
        # from threading import Thread
        # t = Thread(target=self.export, argv=())
        # t.start()

    def export(self):
        print("Call Export")
        import os, csv
        # Export Link File List
        fileName = self.hashLabel.text() + "-LinkFiles.csv"
        newpath = os.getcwd() + "\\" + fileName
        csvfile = open(newpath, 'w')
        lnk_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.linkFileHeader)
        lnk_writer.writeheader()
        print("WriteHeader")
        for rowData in self.hashList[self.selected][2]["LinkFiles"]:
            try:
                _dict = { self.linkFileHeader[n]:rowData[n] for n in range(len(rowData)) }
                print(_dict)
                lnk_writer.writerow(_dict)
            except Exception as e:
                print(e)
        print("Write Rows - LinkFiles")

        '''
        ["Modified Time", "Accessed Time", "Created Time", "LocalBasePath", "Size", "E.No.",
         "Drive Type", "VolumnName", "Serial No."]
        ["Last Recorded Access", "Data", "E.No.", "Access Count", "NetBIOSName",
                               "New (Timestamp)",
                               "New (MAC)", "Seq No.", "Birth (Timestamp)", "Birth (MAC)"]
        '''

        '''
            newdirectory = os.chdir(newpath)
            csvfile = open('LinkFiles.csv', 'ab')
            lnk_writer.writerow({'E.No.': item[0] + "(" + str(int(item[0], 16)) + ")",
                                 'Modified': lnk_header[0], 'Accessed': lnk_header[1],
                                 'Created': lnk_header[2], 'Drive Type': lnk_after_header[0],
                                 'Volume Name': lnk_after_header[1], 'Serial No.': lnk_after_header[2],
                                 'File Size': lnk_header[3], 'LocalBasePath': lnk_after_header[3]})
        '''

        # Export Dest List
        fileName = self.hashLabel.text() + "-DestList.csv"
        newpath = os.getcwd() + "\\" + fileName
        csvfile = open(newpath, 'w')
        destlist_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=self.destListHeader)
        destlist_writer.writeheader()
        print("Write Header - DestList")
        for rowData in self.hashList[self.selected][2]["DestList"]:
            try:
                _dict = {self.destListHeader[n]: rowData[n] for n in range(len(rowData))}
                print(_dict)
                lnk_writer.writerow(_dict)
            except Exception as e:
                print(e)
        print("Write Rows - DestList")

        '''
            csvfile = open('DestList.csv', 'w')
            fieldnames = ['E.No.', 'NetBIOS Name', 'Last Recorded Access', 'Access Count',
                          'New(Timestamp)', 'New (MAC)', 'Seq. No.', 'Birth(Timestamp)', 'Birth (MAC)', 'Data']
            destlist_writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=fieldnames)
            destlist_writer.writeheader()
        '''

        '''
            destlist_writer.writerow({'E.No.': destlist_entryidnumber[0], 'NetBIOS Name': destlist_netbiosname,
                                      'Last Recorded Access': destlist_access_time,
                                      'Access Count': destlist_entry_access_count[0],
                                      'New(Timestamp)': destlist_object_timestamp,
                                      'New (MAC)': new_mac, 'Seq. No.': destlist_object_sequence[0],
                                      'Birth(Timestamp)': birth_destlist_object_timestamp,
                                      'Birth (MAC)': birth_mac, 'Data': Data})
        '''
        print("Success ! - hsah: " + self.hashLabel.text())
        # from PyQt5.QtWidgets import QMessageBox
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Help)
        # msg.setWindowTitle("Help")
        # msg.setText("Success ! - hsah: " + self.hashLabel.text())
        # msg.setStandardButtons(QMessageBox.Ok)
        # msg.exec_()