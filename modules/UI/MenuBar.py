from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, qApp, QFileDialog, QMainWindow, QMessageBox
from modules.UI.JumpListViewer import TableViewer

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
            TableViewer(fileName).showUsnjrnl()
        elif fileType == "$MFT":
            TableViewer(fileName).showMFT()
        elif fileType == "$LogFile":
            TableViewer(fileName).showLogFile()

    def showJumpList(self):
        from modules.Prototype import getJumplistItems
        # self.checkedBtnNumber = self.parent().btnNumber
        # print(self.checkedBtnNumber)
        # jumplistHash = ''
        # if self.checkedBtnNumber == 1:
        #     print("Adobe Checked")
        # elif self.checkedBtnNumber == 2:
        #     print("HWP Checked")
        # elif self.checkedBtnNumber == 3:
        #     print("IE Checked")
        #     jumplistHash = "28c8b86deab549a1"
        # elif self.checkedBtnNumber == 4:
        #     print("Office Checked")
        # elif self.checkedBtnNumber == 5:
        #     print("PDF Checked")

        jumplistHash = "28c8b86deab549a1"
        content = getJumplistItems(jumplistHash)
        if not content:
            # QMessageBox.Warning(self, "")
            print("Not exists.")
        self.ui = TableViewer()
        self.ui.showJumpList(content)

    def showUserEnvironment(self):
        print("showUserEnvironment")

    def showShortcutInfo(self):
        print("showShortcutInfo")