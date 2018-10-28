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

        from threading import Thread
        msg = "Thread"
        self.t = [
            Thread(target=func1, args=("Thread A",)),
            Thread(target=func2, args=("Thread B",)),
            Thread(target=func3, args=("Thread C",)),
            Thread(target=func4, args=("Thread D",)),
            Thread(target=func5, args=("Thread E",)),
        ]
        for i in range(5):
            self.t[i].start()
        for i in range(5):
            self.t[i].join()
        for i in range(5):
            print(a[i])
        self.show()

def func1(msg):
    print("Func1", msg)
    a.append(1)

def func2(msg):
    print("Func2", msg)
    a.append(2)

def func3(msg):
    print("Func3", msg)
    a.append(3)

def func4(msg):
    print("Func4", msg)
    a.append(4)

def func5(msg):
    print("Func5", msg)
    a.append(5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_()) # 이벤트 처리 루프를 위해 exec가 아닌 exec_를 실행(메인루프)