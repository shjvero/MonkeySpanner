import logging

from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtWidgets import QWidget, QProgressBar, QLabel, QSizePolicy, QBoxLayout
from PyQt5.QtCore import Qt, QThread, QWaitCondition, QMutex, pyqtSignal, QObject

import qdarkstyle

class LoadingBarThread(QThread):
    change_value = pyqtSignal(int)
    complete = pyqtSignal()

    def __init__(self, parent):
        QThread.__init__(self)
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self._status = True
        self.parent = parent

    def __del__(self):
        self.wait()

    def run(self):
        self.cnt = 0
        while True:
            self.mutex.lock()

            if not self._status:
                self.cond.wait(self.mutex)

            if 50 == self.cnt:
                self.toggle_status()

            if 100 == self.cnt:
                self.cnt = 0
                self.complete.emit()

            self.cnt += 1
            self.change_value.emit(self.cnt)
            self.msleep(10)

            self.mutex.unlock()

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.cond.wakeAll()

    @property
    def status(self):
        return self._status

class LoadingWidget(QWidget, QObject):
    complete = pyqtSignal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        QObject.__init__(self)
        self.setStyleSheet("background-color: #31353a;")
        self.setAutoFillBackground(True)
        self.gifPath = "img/loading.gif"
        self.initUI()

    def initUI(self):
        layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.setLayout(layout)

        self.loadingMovie = QMovie(self.gifPath)
        self.loadingImg = QLabel(self)
        self.loadingImg.setMovie(self.loadingMovie)
        self.loadingImg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.loadingImg.setAlignment(Qt.AlignCenter)

        self.logLabel = QLabelLogger(self)
        self.logLabel.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(self.logLabel)
        logging.getLogger().setLevel(logging.INFO)

        self.loadingBar = QProgressBar(self)
        self.loadingBar.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.loadingBar.setFixedHeight(10)
        self.loadingBar.setTextVisible(False)

        self.barThread = LoadingBarThread(self)
        self.barThread.change_value.connect(self.loadingBar.setValue)
        self.barThread.complete.connect(self.clear)

        layout.addWidget(self.loadingImg)
        layout.addWidget(self.logLabel.widget)
        layout.addWidget(self.loadingBar)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def start(self):
        self.loadingMovie.start()
        self.barThread.start()
        self.show()

    def resume(self):
        if self.barThread.cnt <= 50:
            self.barThread.cnt = 100
            return
        self.barThread.toggle_status()
        if self.loadingMovie.state() != QMovie.Running:
            self.loadingMovie.start()

    def clear(self):
        self.loadingMovie.stop()
        self.complete.emit()

class QLabelLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QLabel("Collecting...", parent)
        self.widget.setAlignment(Qt.AlignCenter)
        self.widget.setFont(QFont("Times New Roman", 11))

    def emit(self, msg):
        msg = self.format(msg)
        self.widget.setText(msg)