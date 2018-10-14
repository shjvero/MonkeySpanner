import sys
from PyQt5.Qt import *
import modules.IE.Prototype as InternetExplorerPrototype

class PrototypeTable(QTableWidget):
    def __init__(self, sw, env):
        super().__init__()
        self.sw = sw
        self.env = env
        self.prototype = []
        self.colors = {
            "Prefetch": QColor(255, 0, 0),
            "EventLog": QColor(0, 255, 0),
            "History": QColor(0, 0, 255),
            "Cache": QColor(125, 125, 125)
        }
        # 사이즈, 기타 기능 준비
        self.load(sw)
        '''
            1. load() : 프로로타입 로드
            2. initUI() : 테이블 UI 로드
            3. copy() : 셀 우클릭 시 복사
            4. changeColumnHeader() : 항목 클릭 시 컬럼헤더 변화 (*)
            5. showDetail() : 항목 더블클릭 시 뷰어 켜기 (*)
            6. search() : 검색, 스크롤 바 이동까지 포함
        '''

    def load(self, sw=None, timeline=None):
        print("ready")
        if sw == 1:
            print("Adobe Flash Player")
        elif sw == 2:
            print("HWP")
        elif sw == 3:
            self.prototype, self.row = InternetExplorerPrototype.getPrototype(self.env)
            self.customHeaders = InternetExplorerPrototype.getColumnHeader()
        elif sw == 4:
            print("Office")
        elif sw == 5:
            print("PDF")
        else:
            print("기존 SW: {}".format(self.sw))
        # sw에 따라서 프로토타입 가져오기 -- 배열 or 객체
        # self.initUI(prototype)
        if timeline:
            print("타임라인 설정 O")
        else:
            print("타임라인 설정 X")

    def initUI(self):
        print("initUI")
        self.setColumnCount(6)
        self.setRowCount(self.row)
        # self.prototype 에 저장된 데이터들 모두 테이블에 로드
        self.setHorizontalHeaderLabels(["", "", "", "", "", ""])
        row = 0
        # print(self.prototype)
        for header, list in self.prototype.items():
            for prototypeItem in list:
                self.setVerticalHeaderItem(row, QTableWidgetItem(header))
                print(prototypeItem)
                self.setItem(row, 0, QTableWidgetItem(prototypeItem[0]))
                self.setItem(row, 1, QTableWidgetItem(prototypeItem[1]))
                self.setItem(row, 2, QTableWidgetItem(prototypeItem[2]))
                self.setItem(row, 3, QTableWidgetItem(prototypeItem[3]))
                self.setItem(row, 4, QTableWidgetItem(prototypeItem[4]))
                self.setItem(row, 5, QTableWidgetItem(""))
                # self.item(row, 0).setBackground(self.colors[header])
                # self.item(row, 1).setBackground(self.colors[header])
                # self.item(row, 2).setBackground(self.colors[header])
                # self.item(row, 3).setBackground(self.colors[header])
                # self.item(row, 4).setBackground(self.colors[header])
                # self.item(row, 5).setBackground(self.colors[header])
                row += 1

        self.clicked.connect(self.changeColumnHeader)  # 원클릭
        self.doubleClicked.connect(self.showDetail)  # 더블 클릭
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


    def search(self, keyword):
        print("search: " + keyword)

    @pyqtSlot()
    def changeColumnHeader(self):
        print("changeColumnHeader\n")
        # header = ''
        # for currentQTableWidgetItem in self.selectedItems():
        #     header = self.item(currentQTableWidgetItem.row, 0).text()
        #     print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
        # self.table.setHorizontalHeaderLabels(self.customHeaders[header])

    @pyqtSlot()
    def showDetail(self):
        print("showDetail")