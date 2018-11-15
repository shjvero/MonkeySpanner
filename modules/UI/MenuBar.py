from modules.UI.JumpListViewer import JumpListViewer
from PyQt5.QtWidgets import *

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        QMenuBar.__init__(self, parent)
        self.menu = ["File", "View", "Settings", "Help"]
        self.action = [
            ["Export as CSV", "Exit"],
            ["Import NTFS Log", "Import JumpList", "Import RecentFileCache.bcf", "Import Amcache.hve", "Import Registry"],
            ["Reload"],
            ["Environment", "About"]
        ]
        self.initUI()

    def initUI(self):
        fileMenu = self.addMenu(self.menu[0])
        viewMenu = self.addMenu(self.menu[1])
        settingMenu = self.addMenu(self.menu[2])
        helpMenu = self.addMenu(self.menu[3])

        # File
        exportMenu = QAction(self.action[0][0], self)
        exportMenu.setShortcut("Ctrl+S")
        exportMenu.setToolTip("Only list currently visible")
        exportMenu.triggered.connect(self.export)
        fileMenu.addAction(exportMenu)

        exitMenu = QAction(self.action[0][1], self)
        exitMenu.setShortcut("Ctrl+Q")
        exitMenu.triggered.connect(qApp.quit)
        fileMenu.addAction(exitMenu)

        # View
        NTFSMenu = QAction(self.action[1][0], self)
        NTFSMenu.triggered.connect(self.showNTFSViewer)
        viewMenu.addAction(NTFSMenu)

        jumplistMenu = QAction(self.action[1][1], self)
        jumplistMenu.triggered.connect(self.showJumpListViewer)
        viewMenu.addAction(jumplistMenu)

        recentfilebcfMenu = QAction(self.action[1][2], self)
        recentfilebcfMenu.triggered.connect(self.showRecentFileBCF)
        viewMenu.addAction(recentfilebcfMenu)

        amcacheMenu = QAction(self.action[1][3], self)
        amcacheMenu.triggered.connect(self.showAmcache)
        viewMenu.addAction(amcacheMenu)

        registryMenu = QAction(self.action[1][4], self)
        registryMenu.triggered.connect(self.importRegistry)
        viewMenu.addAction(registryMenu)

        # Settings
        reloadAction1 = QAction(self.action[2][0], self)
        reloadAction1.setShortcut("F5")
        registryMenu.triggered.connect(self.reload)
        settingMenu.addAction(reloadAction1)

        # timelineAction2 = QAction("Reload with Timeline", self)
        # timelineAction2.setShortcut("F6")
        # settingMenu.addAction(timelineAction2)

        # Help
        envAction = QAction(self.action[3][0], self)
        envAction.triggered.connect(self.showUserEnvironment)
        helpMenu.addAction(envAction)

        aboutAction = QAction(self.action[3][1], self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def showNTFSViewer(self):
        from modules.UI.NTFSViewer import NTFSViewer
        self.parent().ntfsViewer = NTFSViewer()

    def showJumpListViewer(self):
        from modules.Prototype import getJumplistItems
        import modules.constant as CONSTANT
        self.selected = self.parent().presentSelected
        hashList = []
        if self.selected == CONSTANT.ADOBE_READER:
            print("Adobe Reader")
            for i in range(16, 22):
                hashList.append(CONSTANT.JUMPLIST_HASH[i])
        elif self.selected == CONSTANT.ADOBE_FLASH_PLAYER:
            print("Adobe Flash Player in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[14])
        elif self.selected == CONSTANT.CHROME:
            print("Chrome in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[22])
        elif self.selected == CONSTANT.EDGE:
            print("Edge in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[23])
        elif self.selected == CONSTANT.HWP:
            print("HWP in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[15])
        elif self.selected == CONSTANT.IE:
            print("IE in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[12])
            hashList.append(CONSTANT.JUMPLIST_HASH[13])
        elif self.selected == CONSTANT.OFFICE:
            print("Office in JumpListViewer")
            for i in range(12):
                hashList.append(CONSTANT.JUMPLIST_HASH[i])
        elif self.selected == CONSTANT.LPE:
            print("LPE in JumpListViewer [None]")
        else:
            QMessageBox.question(self, "Help", "Please select software.", QMessageBox.Ok)
            return
        content = getJumplistItems(hashList)
        if not content:
            msg = "[Not Exists.]\n"
            for h in hashList:
                msg += " - ".join(h)
                msg += "\n"
            QMessageBox.information(self, "Help", msg, QMessageBox.Ok)
            return
        self.parent().jumplistViewer = JumpListViewer(content)

    def showRecentFileBCF(self):
        from modules.Prototype import getRecentFileCache
        from modules.UI.ListViewer import ListViewer
        fileName = QFileDialog.getOpenFileName(self)
        rst, contents = getRecentFileCache(fileName[0])
        if rst:
            self.parent().listViewer = ListViewer("RecentFileCache Viewer", contents)
        else:
            QMessageBox.information(self, "Help", contents, QMessageBox.Ok)

    def showAmcache(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)

    def export(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)

    def reload(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)

    def importRegistry(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)

    def showUserEnvironment(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)

    def showAbout(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)
