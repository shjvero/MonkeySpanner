def showMsg(msg, type):
    import sys
    from PyQt5.QtWidgets import QMessageBox
    msg = QMessageBox()
    # QMessageBox.Information   1
    # QMessageBox.Warning       2
    # QMessageBox.Critical      3
    msg.setIcon(type)
    msg.setWindowTitle("[Report]")
    msg.setText(msg)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.buttonClicked.connect(sys.exit)
    msg.exec_()