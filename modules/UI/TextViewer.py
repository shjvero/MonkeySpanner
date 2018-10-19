import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class TextViewer(QDialog):
    _buttons = 0

    def __init__(self, parent=None):
        super(TextViewer, self).__init__(parent)
        self.content = parent.viewerContent
        self.setWindowTitle(parent.viewerTitle)
        self.resize(800, 500)
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

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
                # 에러나는 이유는,, \n가 있어서 -- 어찌할건가?
