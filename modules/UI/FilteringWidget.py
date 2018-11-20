from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import modules.constant as CONSTANT

class FilteringWidget(QTreeWidget, QObject):

    def __init__(self):
        QTreeWidget.__init__(self)
        QObject.__init__(self)
        self.options = {
            "Artifact": CONSTANT.ArtifactList,
            "Color": CONSTANT.ColorList.keys()
        }
        self.initUI()

    def initUI(self):
        self.parents = []
        self.items = {}
        for option in self.options.keys():
            parent = QTreeWidgetItem(self)
            parent.setText(0, option)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            parent.setExpanded(True)
            self.parents.append(parent)
            self.items[option] = []
            for value in self.options[option]:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, value)
                child.setCheckState(0, Qt.Checked)
                self.items[option].append(child)

        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(200)
        self.setMinimumHeight(320)
        self.setHeaderHidden(True)
        self.setWindowTitle("Filtering")

    def presentCheckedItems(self):
        checkedItems = {}
        for p in self.parents:
            parent = p.text(0)
            checkedItems[parent] = []
            for child in self.items[parent]:
                if child.checkState(0) == Qt.Checked:
                    checkedItems[parent].append(child.text(0))
        return checkedItems