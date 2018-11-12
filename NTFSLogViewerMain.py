from PyQt5.Qt import QApplication
from modules.UI.NTFSViewer import NTFSViewer
import qdarkstyle
import os, sys, ctypes
import win32com.shell.shell as shell

def uac_require():
    asadmin = 'asadmin'
    try:
        if sys.argv[-1] != asadmin:
            script = os.path.abspath(sys.argv[0])
            params = ''.join([script]+sys.argv[1:]+[asadmin])
            shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
            sys.exit()
        return True
    except Exception as e:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = NTFSViewer()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())

    '''
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = QApplication(sys.argv)
        w = NTFSViewer()
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        sys.exit(app.exec_())
    else:
        if uac_require():
            app = QApplication(sys.argv)
            w = NTFSViewer()
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            sys.exit(app.exec_())
        else:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Not administrator")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(sys.exit)
            msg.exec_()
    '''
