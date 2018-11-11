from modules.UI.JumpListViewer import JumpListViewer
from modules.UI.NTFSViewer import *

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)
        # 메뉴 생성
        fileMenu = self.addMenu("File")  # 메뉴그룹 생성

        NTFSMenu = QAction("Import NTFS Log", self)
        NTFSMenu.triggered.connect(self.showNTFSLogFileDialog)
        fileMenu.addAction(NTFSMenu)

        jumplistMenu = QAction("Import JumpList", self)
        jumplistMenu.triggered.connect(self.showJumpListViewer)
        fileMenu.addAction(jumplistMenu)

        registryMenu = QAction("Import Registry", self)
        registryMenu.triggered.connect(self.importRegistry)
        fileMenu.addAction(registryMenu)

        exit_menu = QAction("Exit", self)  # 메뉴 객체 생성
        exit_menu.setShortcut("Ctrl+Q")  # 단축키 생성
        exit_menu.setStatusTip("종료")
        exit_menu.triggered.connect(qApp.quit)
        fileMenu.addAction(exit_menu)

        viewMenu = self.addMenu("View")
        helpMenu = self.addMenu("Help")


        reloadAction1 = QAction("Reload", self)
        reloadAction1.setShortcut("F5")
        timelineAction2 = QAction("Reload with Timeline", self)
        timelineAction2.setShortcut("F6")
        fullScreenAction3 = QAction("Full Screen", self, checkable=True)
        fullScreenAction3.setShortcut("F11")
        fullScreenAction3.setChecked(False)
        viewAction4 = QAction("View Option 4", self, checkable=True)
        viewAction4.setChecked(False)
        viewMenu.addAction(reloadAction1)
        viewMenu.addAction(timelineAction2)
        viewMenu.addAction(fullScreenAction3)
        viewMenu.addAction(viewAction4)

        envAction = QAction("Environment", self)
        envAction.triggered.connect(self.showUserEnvironment)
        shortcutAction = QAction("Shortcut", self)
        shortcutAction.triggered.connect(self.showShortcutInfo)
        helpMenu.addAction(envAction)
        helpMenu.addAction(shortcutAction)

    def showNTFSLogFileDialog(self):
        from modules.UI.NTFSLogFileDialog import NTFSLogFileDialog
        self.ntfsDialog = NTFSLogFileDialog(self)
        self.ntfsDialog.completeBtn.clicked.connect(self.showNTFSViewer)

    def showNTFSViewer(self):
        self.ntfsDialog.loadingBar.show()
        self.ntfsDialog.barThread.start()
        _path = [
            self.ntfsDialog.mftPathTextBox.text(),
            self.ntfsDialog.usnjrnlPathTextBox.text(),
            self.ntfsDialog.logfilePathTextBox.text()
        ]
        self.ntfsViewer = NTFSViewer()
        rst, msg = self.ntfsViewer.check(_path)
        if rst:
            self.ntfsViewer.load()
            self.ntfsDialog.resume()
            self.ntfsViewer.show()
        else:
            QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)
            self.ntfsDialog.accept()

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
        content = getJumplistItems(hashList.copy())
        if not content:
            msg = "[Not Exists.]\n"
            for h in hashList:
                msg += " - ".join(h)
                msg += "\n"
            QMessageBox.question(self, "Help", msg, QMessageBox.Ok)
            return
        self.jumplistViewer = JumpListViewer(content)
        self.jumplistViewer.show()

    def importRegistry(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)
        # print("Import Registry")

    def showUserEnvironment(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)
        # print("showUserEnvironment")

    def showShortcutInfo(self):
        QMessageBox.question(self, "Help", "Preparing...", QMessageBox.Ok)
        # print("showShortcutInfo")