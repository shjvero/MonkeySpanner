from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, qApp, QFileDialog
from modules.UI.JumpListViewer import JumpListViewer

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)
        # 메뉴 생성
        fileMenu = self.addMenu("File")  # 메뉴그룹 생성
        fileMenu.triggered[QAction].connect(self.openFileDialog)
        viewMenu = self.addMenu("View")
        # viewMenu.triggered[QAction].connect(self.openFileDialog)
        helpMenu = self.addMenu("Help")

        NTFSMenu = QMenu("Import FileSystem", self)  # 서브메뉴 생성
        importUsnjrnl = QAction("$usnjrnl", self)
        importMFT = QAction("$mft", self)
        importLogFile = QAction("$LogFile", self)

        NTFSMenu.addAction(importUsnjrnl)
        NTFSMenu.addAction(importMFT)
        NTFSMenu.addAction(importLogFile)
        fileMenu.addMenu(NTFSMenu)

        jumplistMenu = QAction("Import JumpList", self)
        jumplistMenu.triggered.connect(self.showJumpList)
        fileMenu.addAction(jumplistMenu)

        registryMenu = QAction("Import Registry", self)
        jumplistMenu.triggered.connect(self.importRegistry)
        fileMenu.addAction(registryMenu)

        exit_menu = QAction("Exit", self)  # 메뉴 객체 생성
        exit_menu.setShortcut("Ctrl+Q")  # 단축키 생성
        exit_menu.setStatusTip("종료")
        exit_menu.triggered.connect(qApp.quit)
        fileMenu.addAction(exit_menu)

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

    def openFileDialog(self, type):
        print(type.text() + " is triggered")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*)", options=options)
        fileType = type.text()
        if fileType == "$usnjrnl":
            print()
        elif fileType == "$MFT":
            print()
        elif fileType == "$LogFile":
            print()

    def showJumpList(self):
        from modules.Prototype import getJumplistItems
        import modules.constant as CONSTANT
        self.selected = self.parent().presentSelected
        print(self.selected)
        hashList = []
        if self.selected == CONSTANT.ADOBE_READER:
            print("Adobe Reader")
            hashList.append(CONSTANT.JUMPLIST_HASH[15])
            hashList.append(CONSTANT.JUMPLIST_HASH[16])
            hashList.append(CONSTANT.JUMPLIST_HASH[17])
            hashList.append(CONSTANT.JUMPLIST_HASH[18])
            hashList.append(CONSTANT.JUMPLIST_HASH[19])
            hashList.append(CONSTANT.JUMPLIST_HASH[20])
            hashList.append(CONSTANT.JUMPLIST_HASH[21])
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
            print("HWP in JumpListViewer [None]")
        elif self.selected == CONSTANT.IE:
            print("IE in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[12])
            hashList.append(CONSTANT.JUMPLIST_HASH[13])
        elif self.selected == CONSTANT.OFFICE:
            print("Office in JumpListViewer")
            hashList.append(CONSTANT.JUMPLIST_HASH[0])
            hashList.append(CONSTANT.JUMPLIST_HASH[1])
            hashList.append(CONSTANT.JUMPLIST_HASH[2])
            hashList.append(CONSTANT.JUMPLIST_HASH[3])
            hashList.append(CONSTANT.JUMPLIST_HASH[4])
            hashList.append(CONSTANT.JUMPLIST_HASH[5])
            hashList.append(CONSTANT.JUMPLIST_HASH[6])
            hashList.append(CONSTANT.JUMPLIST_HASH[7])
            hashList.append(CONSTANT.JUMPLIST_HASH[8])
            hashList.append(CONSTANT.JUMPLIST_HASH[9])
            hashList.append(CONSTANT.JUMPLIST_HASH[10])
            hashList.append(CONSTANT.JUMPLIST_HASH[11])
        elif self.selected == CONSTANT.LPE:
            print("LPE in JumpListViewer [None]")
        else:
            self.msgDialog("Please select software.")
        # 현재 상태: 점프리스트 1개만 받아서 반환, 배열인데 어떻게 처리할 것?
        content = getJumplistItems(hashList[1])
        if not content:
            self.msgDialog("JumpList Not exists. - hash: " + hashList[1])
        self.ui = JumpListViewer(content)
        self.ui.show()

    def msgDialog(self, m):
        import sys
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setText(m)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(sys.exit)
        msg.exec_()

    def importRegistry(self):
        print("Import Registry")

    def showUserEnvironment(self):
        print("showUserEnvironment")

    def showShortcutInfo(self):
        print("showShortcutInfo")