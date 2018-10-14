import sys
from PyQt5.Qt import *
import modules.IE.Prototype as InternetExplorerPrototype

class PrototypeTable(QTableWidget):
    def __init__(self, sw):
        super().__init__()
        self.sw = sw
        self.prototype = []
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
            self.prototype = InternetExplorerPrototype.getPrototype()
            self.columnHeaders = InternetExplorerPrototype.getColumnHeader()
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

    def initUI(self, prototype):
        print("initUI")
        self.setColumnCount(8)
        # self.prototype 에 저장된 데이터들 모두 테이블에 로드
        # 행마다 색 지정
        self.clicked.connect(self.changeColumnHeader)  # 원클릭
        self.doubleClicked.connect(self.showDetail)  # 더블 클릭
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.move(0, 110 + self.search.height())
        self.table.resize(self.search.width() + 20, self.h + 100)

    def search(self, keyword):
        print("search: " + keyword)

    @pyqtSlot()
    def changeColumnHeader(self):
        print("changeColumnHeader\n")
        self.table.setHorizontalHeaderLabels(self.columnHeaders[""])
        for currentQTableWidgetItem in self.table.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    @pyqtSlot()
    def showDetail(self):
        print("showDetail")