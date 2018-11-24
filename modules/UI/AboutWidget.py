from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *
import modules.constant as CONSTANT

class AboutWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.index = {
            'Introduction': ['Background', 'Motivation', 'About "MonkeySapnner"'],
            'What is Artifact Prototype?': ['Definition of Artifact Prototype', 'Methodology'],
            'Prototype': [CONSTANT.ADOBE_READER_KEYWORD,
                            CONSTANT.ADOBE_FLASH_PLAYER_KEYWORD,
                            CONSTANT.EDGE_KEYWORD,
                            CONSTANT.HWP_KEYWORD,
                            CONSTANT.IE_KEYWORD,
                            CONSTANT.OFFICE_KEYWORD,
                            CONSTANT.LPE_KEYWORD]
        }
        self.presentPage = 0
        self.contentsText = ["A", "B", "C"]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About")
        self.setFixedSize(self.width(), self.height())
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Table of Contents
        self.indexTree = QTreeWidget(self)
        self.indexTree.setFixedWidth(250)
        self.indexTree.setHeaderLabel("Table Of Contents")
        self.indexTree.itemClicked.connect(self.indexItemClicked)

        self.treeWidgetItems = []
        for p_text in self.index.keys():
            parent = QTreeWidgetItem(self.indexTree)
            parent.setText(0, p_text)
            parent.setExpanded(True)
            self.treeWidgetItems.append(parent)
            for c_text in self.index[p_text]:
                child = QTreeWidgetItem(parent)
                child.setText(0, c_text)
                self.treeWidgetItems.append(child)


        # Contents
        self.contents = QTextEdit("TEST contents", self)
        self.contents.setReadOnly(True)

        self.splitter.addWidget(self.indexTree)
        self.splitter.addWidget(self.contents)
        self.show()

    def indexItemClicked(self, item, p_int):
        print(item.text(0))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = AboutWidget()
    sys.exit(app.exec_())