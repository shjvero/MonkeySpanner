from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *
import modules.constant as CONSTANT

class AboutWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.index = {
            '1. Introduction': ['1-1. Background', '1-2. Motivation', '1-3. About "MonkeySapnner"'],
            '2. What is Artifact Prototype?': ['2-1. Definition of Artifact Prototype', '2-2. Methodology'],
            '3. Prototype': [
                "3-1. {}".format(CONSTANT.ADOBE_READER_KEYWORD),
                "3-2. {}".format(CONSTANT.ADOBE_FLASH_PLAYER_KEYWORD),
                "3-3. {}".format(CONSTANT.EDGE_KEYWORD),
                "3-4. {}".format(CONSTANT.HWP_KEYWORD),
                "3-5. {}".format(CONSTANT.IE_KEYWORD),
                "3-6. {}".format(CONSTANT.OFFICE_KEYWORD),
                "3-7. {}".format(CONSTANT.LPE_KEYWORD),
            ],
        }
        self.presentPage = 0
        self.contentsText = {
            '1': '"MonkeySpanner" was made by a project manager, \n'
                 'Eunjin, Kwon, in the team, "Eunjin with MonkeySpanner".\n'
                 'Our team had performed research about security.\n'
                 'Our topic is "Precise Analysis of attacker\'s behavior\n'
                 'through Offensive Research". '
                 'But, our project scope is only to exploit vulnerabilities of software in Windows.\n\n'
                 '# Next page explain contents as below.\n'
                 '    (1) What our direction was\n'
                 '    (2) What purpose we approached as\n'
                 '    (3) Which expected effect many people can get \n'
                 '        by using this tool, and contacting with our research.\n',
            '1-1': 'A software fundamentally behaves by being executed commands of assembly unit from CPU.\n'
                   'In Digital Forensic, `Artifact` means data created \n'
                   'automatically by system or software.\n'
                   'Creating data automatically is to execute the commands \n'
                   'when do some behavior or satisfy some conditions. \n'
                   'Like Event Log, Prefetch, Registry, ... and vice versa.\n'
                   '(above artifacts from Operating System, artifacts created from each software can exists.)\n\n'
                   'So, Let Think about `Artifact Created When an Error Occurs`\n\n'
                   'This is because a exception code of are executed \n'
                   'when error inside sw or system occurs.\n'
                   '(some exception code can’t create artifacts)\n\n'
                   'In fact, all software can’t create such artifacts, but\n'
                   'if it is popular, it\'ll handle exception, and deal with it for user to find cause of error.\n'
                   'This is why popular softwares are able to create some artifacts when an error occurs.',
            '1-2': 'We needed to research popular software (like MS-Office, IE, Chrome, … etc) in Windows.\n\n'
                   'Also, we want to check on the following curiosity.\n'
                   '    (1) When exploit code executed, which artifact is left?\n'
                   '    (2) Is this treated as the artifact created when an error\n'
                   '        occurs ?\n'
                   '    (3) Such artifacts are different when not same\n'
                   '        vulnerability ?\n\n'
                   'In case (3), If such artifacts are similar,\n'
                   'Are these common for every exploit in the software only?\n\n'
                   'So, we determined to find out `common artifacts set` for popular software when error occurs in Windows.\n\n'
                   'Our research is meaningful historically, but we worried about practicality (is this useful?)\n\n'
                   '"What about Incident Response ?"\n\n'
                   'Fundamentally, it’s important to prevent from propagating malicious program after incident occurs.'
                   'So, we thought that our finding, common artifacts set will be artifacts occurred during malicious program spread.\n\n'
                   '# Direction: To define common artifacts set for target software.\n\n'
                   '# Goal: Our research reports seems to be used as logical grounds for precisely analyzing and classifying attacker’s behavior in Incident Response or Analysis',
            '1-3': 'The tool MonkeySapnner aims to be used to precisely classify and analyze attacker\'s behavior '
                   'in the process of responding to and analyzing the incident.\n'
                   'Today, the many forensic tools that add convenience are unfortunately '
                   'not in the process of extracting the associations of artifacts.\n'
                   '(There is, of course, such a tool.)\n\n'
                   'However, analysts are inconvenienced because this process requires a lot of time to invest in analysis.\n'
                   'Our tools will help you relieve this discomfort.\n\n'
                   'With the Monkey Spanner, you will be able to see artifacts grouped by software, '
                   'and you will be able to quickly identify actual inflows and respond quickly to infringement.',
            '2': 'We called the artifacts grouped by specified software "Artifact Prototype".\n(It is just simple reason)',
            '2-1': 'When you actually run malicious code, you may or may not have a variety of artifacts. \n'
                   'We do not always think that our defined artifact prototype is complete because we always consider that there is not.'
                   'It just started from the idea that it could be grouped and used as an indicator of an intrusion. \n\n'
                   'When there are various artifacts left in normal execution, they may remain redundant. '
                   'In this case, it\'s hard to see it as a significant artifact. '
                   'What we want to do is to help us identify the infringement, or to handle the error. \n\n'
                   'To summarize, we have defined the artifact prototype as a set of meaningful artifacts '
                   'that can be used to identify infringement of an infected malware by attacking certain software.',
            '2-2': 'Based on artifacts created time, if classfy exploit code,\n\n'
                   '0.1 process execute\n'
                   '        1.1 just got crash\n'
                   '        2.1 run to shellcode\n'
                   '\t    2.2 dll injection / file create\n'
                   '\t    2.3 file delete / downloader\n\n'
                   'We thought it was the most significant artifact in terms of artifacts that could distinguish each step.'
                   'In fact, what I wanted most was to find artifacts due to errors, but in the Windows environment, '
                   'not all software left these artifacts.\n\n'
                   'Usually the first stage was a prefetch, a jump list, a web artifact, '
                   'and the second stage was an event log, a temporary file, or a deleted file. '
                   'To confirm this fact, we analyzed vulnerabilities exploited in exploit-kits with high attack success rates. '
                   'The artifacts for each CVE number were grouped and excluded if not significant. '
                   'As the process repeats, more and more artifact prototypes of certain software have been completed.',

            '3': "3 TEST",
            '3-1': "3-1"*20,
            '3-2': "3-2"*20,
            '3-3': "3-3"*20,
            '3-4': "3-4"*20,
            '3-5': "3-5"*20,
            '3-6': "3-6"*20,
            '3-7': "3-7"*20,
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About")
        self.setFixedSize(self.width(), self.height()-150)
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # Table of Contents
        self.indexTree = QTreeWidget(self)
        self.indexTree.setFixedWidth(265)
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
        self.contents = QTextEdit('', self)
        self.contents.setText(self.contentsText['1'])
        self.contents.setContentsMargins(10, 5, 5, 10)
        self.contents.setReadOnly(True)

        self.splitter.addWidget(self.indexTree)
        self.splitter.addWidget(self.contents)
        self.show()

    def indexItemClicked(self, item, p_int):
        idx = item.text(0).split('.')[0]
        self.contents.setText(self.contentsText[idx])

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = AboutWidget()
    sys.exit(app.exec_())