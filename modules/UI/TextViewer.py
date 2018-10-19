import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

class TextViewer(QWidget):

    def __init__(self):
        super(TextViewer, self).__init__()

    def initUI(self, viewerTitle, viewerContent):
        self.content = viewerContent
        self.setWindowTitle(viewerTitle)
        self.setWindowIcon(QIcon("../../img/logo.png"))
        self.resize(600, 500)
        self.label = QLabel()
        self.label.setText(self.content)
        self.label.setMargin(10)
        # self.font()
        # 선택모드
        # 스크롤영역 마진 없애기
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.label)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.scrollArea)
        self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
                # 에러나는 이유는,, \n가 있어서 -- 어찌할건가?
