from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QLabel, QBoxLayout, QScrollArea, QVBoxLayout, \
    QApplication


class WebArtifactDetailViewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        test_contents = [
            "213",
            "History",
            "2018-01-03 11:21:23.324221",
            "2018-01-03 11:21:23.324221",
            "2018-01-03 11:21:23.324221",
            "2018-01-03 11:21:23.324221",
            "2018-01-03 11:21:23.324221",
            "32",
            "56",
            "<<<<<<<<<<<<<<<<<<<<<<<ASDFASSMAPE>>>>>>>>>>>>>>>>>>",
            "<<<<<<<,File Name>>>>>>>",
            "23543245",
            "<<<<<<<<<<<<<<<<<<<<<<<ASDFASSMAPE>>>>>>>>>>>>>>>>>>",
            '200 OK \n\
            Access-Control-Allow-Origin: * \n\
            Connection: Keep-Alive \n\
            Content-Encoding: gzip \n\
            Content-Type: text/html; charset=utf-8 \n\
            Date: Mon, 18 Jul 2016 16:06:00 GMT \n\
            Etag: "c561c68d0ba92bbeb8b0f612a9199f722e3a621a" \n\
            Keep-Alive: timeout=5, max=997 \n\
            Last-Modified: Mon, 18 Jul 2016 02:36:04 GMT \n\
            Server: Apache \n\
            Set-Cookie: mykey=myvalue; expires=Mon, 17-Jul-2017 16:06:00 GMT; Max-Age=31449600; Path=/; secure \n\
            Transfer-Encoding: chunked \n\
            Vary: Cookie, Accept-Encoding \n\
            X-Backend-Server: developer2.webapp.scl3.mozilla.com \n\
            X-Cache-Info: not cacheable; meta data too large \n\
            X-kuma-revision: 1085259 \n\
            x-frame-options: DENY'
        ]
        self.initUI("Web Artifact Detail", test_contents)

    def initUI(self, title, contents):
        self.category = [
            "ID",
            "Container Name",
            "Created Time",
            "Accessed Time",
            "Modified Time",
            "Expires Time",
            "Synced Time",
            "Sync Count",
            "Access Count",
            "URL",
            "File Name",
            "File Size",
            "Directory"
        ]
        # response header
        self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setFixedSize(self.width()-100, 300)
        self.table.setRowCount(len(self.category))
        self.table.setColumnCount(2)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for i in range(len(self.category)):
            self.table.setItem(i, 0, QTableWidgetItem(self.category[i]))
        for i in range(len(contents)-1):
            self.table.setItem(i, 1, QTableWidgetItem(contents[i]))
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.verticalHeader().setMaximumSectionSize(28)
        self.table.setColumnWidth(0, 120)

        self.headerLabel = QLabel("Response Header", self)
        self.headerLabel.setFixedHeight(30)
        self.headerLabel.setAlignment(Qt.AlignBottom)

        self.label = QLabel()
        content = contents[-1] if contents[-1] else "None"
        self.label.setText(content)
        self.label.setMargin(10)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.label)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.headerLabel)
        self.layout.addWidget(self.scrollArea)
        self.show()

    def contextMenuEvent(self, event):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            import os
            if os.system("echo {} | clip".format(self.content)) == 0:
                print(self.content)
                # 에러나는 이유는,, \n가 있어서 -- 어찌할건가?

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = WebArtifactDetailViewer()
    sys.exit(app.exec_())