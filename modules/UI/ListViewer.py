from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *

class ListViewer(QWidget):

    def __init__(self, viewerTitle, viewerContent):
        QWidget.__init__(self)
        self.initUI(viewerTitle, viewerContent)

    def initUI(self, viewerTitle, viewerContent):
        self.setWindowTitle(viewerTitle)
        self.layout = QVBoxLayout(self)

        self.content = viewerContent
        self.setWindowTitle(viewerTitle)
        self.resize(self.width(), self.height())

        self.list = QListView(self)
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.model = QStandardItemModel()
        for item in viewerContent:
            self.model.appendRow(QStandardItem(item))
        self.list.setModel(self.model)
        self.layout.addWidget(self.list)

        self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
