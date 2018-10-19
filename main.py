import os, sys

from PyQt5.QtGui import QColor, QPixmap, QMovie
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, Qt


class Exam(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(QVBoxLayout(self.centralwidget))

        self.mdiArea = QMdiArea(self.centralwidget)
        self.centralwidget.layout().addWidget(self.mdiArea)

        subWindow = QMdiSubWindow(self)

        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        btn = QPushButton("close", widget)
        widget.layout().addWidget(btn)

        btn.clicked.connect(subWindow.close)

        subWindow.setWidget(widget)
        subWindow.setObjectName("New_Window")
        subWindow.setWindowTitle("New SubWindow")
        self.mdiArea.addSubWindow(subWindow)
        # self.initUI()

    def initUI(self):
        btn = QPushButton('Push me!', self)
        btn.resize(btn.sizeHint()) # 글씨 기준으로 크기 조절
        btn.setToolTip('this is <strong>tooltip</strong>')
        btn.move(20, 30) # 버튼 움직이기.

        # 눌렀을 때, 시그널을 보내면, 받고 꺼지도록,
        # connect 인자에는 함수명만 들어감
        # ...connect(self.on_click)
        btn.clicked.connect(QCoreApplication.instance().quit)

        #self.setGeometry(300, 300, 400, 500) # 창크기 조절
        self.resize(500, 500) # 바탕화면 정중앙 배치.
        self.setWindowTitle("TEST Title")
        self.table = QTableWidget(self)
        self.table.resize(400, 300)
        self.table.setColumnCount(4)
        self.table.setRowCount(5)
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                import random
                item = QTableWidgetItem()
                item.setData(Qt.EditRole, "{}{}".format(random.randint(1, 100),random.randint(1, 100)))
                self.table.setItem(r, c, item)

        self.table.setHorizontalHeaderLabels(["A", "B", "C", "D"])
        self.table.hide()
        label = QLabel(self)
        loadingGif = QMovie("img/loading1.gif")
        label.setMovie(loadingGif)
        label.move(10, 10)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(Qt.AlignCenter)
        loadingGif.start()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_()) # 이벤트 처리 루프를 위해 exec가 아닌 exec_를 실행(메인루프)