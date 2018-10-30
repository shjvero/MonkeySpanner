import os, sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, Qt, QRect

a = []
class Exam(QMainWindow):
    FROM, SUBJECT, DATE = range(3)
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Example'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(self.width(), self.height())

        self.btn = QPushButton("Push", self)
        self.btn.move(10, 400)
        self.btn.resize(200, 30)
        self.btn.clicked.connect(self.btnClicked)

        self.movie = QMovie("img/loading2.gif")
        self.label = QLabel(self)
        self.label.move(20, 20)
        self.label.setMovie(self.movie)
        self.label.setFixedSize(self.width(), self.height())
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.hide()
        self.show()
        from threading import Thread
        msg = "Thread"
        self.t = [
            Thread(target=self.func1, args=("Thread A",)),
            Thread(target=self.func2, args=("Thread B",)),
            # Thread(target=self.func3, args=("Thread C",)),
            # Thread(target=self.func4, args=("Thread D",)),
            # Thread(target=self.func5, args=("Thread E",)),
        ]
        for i in range(len(self.t)):
            self.t[i].start()
        # import time
        # time.sleep(5)
        # for i in range(len(self.t)):
        #     self.t[i].join()
        # for i in range(len(self.t)):
        #     print(a[i])

    def btnClicked(self, b):
        self.label.show()

    def func1(self, msg):
        print("Func1", msg)
        from threading import Thread
        t = Thread(target=self.func3, args=("Thread A - C",))
        t.start()
        self.label.hide()
        a.append(1)

    def func2(self, msg):
        self.movie.start()
        print("Func2", msg)
        a.append(2)

    def func3(self, msg):
        print("Func3", msg)
        a.append(3)

    def func4(self, msg):
        print("Func4", msg)
        a.append(4)

    def func5(self, msg):
        print("Func5", msg)
        a.append(5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_()) # 이벤트 처리 루프를 위해 exec가 아닌 exec_를 실행(메인루프)