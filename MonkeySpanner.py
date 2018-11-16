import os
import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from MainWindow import Main
import win32com.shell.shell as shell

def uac_require():
    asadmin = 'asadmin'
    try:
        if sys.argv[-1] != asadmin:
            script = os.path.abspath(sys.argv[0])
            params = ''.join([script]+sys.argv[1:]+[asadmin])
            shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
            sys.exit()
        return True, None
    except Exception as e:
        return False, "{}".format(e)

if __name__ == "__main__":
    '''
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = Main()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print("Error in Main: {}".format(e))
    '''
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = QApplication(sys.argv)
        w = Main()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        sys.exit(app.exec_())
    else:
        rst, msg = uac_require()
        if rst:
            app = QApplication(sys.argv)
            w = Main()
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            sys.exit(app.exec_())
        else:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(msg)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()
