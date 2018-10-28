import os

# Software Number
ADOBE_READER = 1
ADOBE_FLASH_PLAYER = 2
CHROME = 3
EDGE = 4
HWP = 5
IE = 6
OFFICE = 7
LPE = 8

# Environment Variable
LOCALAPPDATA = os.environ["LOCALAPPDATA"]   # C:\\Users\\[username]\\AppData\\Local
APPDATA = os.environ["APPDATA"]             # C:\\Users\\[username]\\AppData\\Roaming
SYSTEMDRIVE = os.environ["SYSTEMDRIVE"]     # C:\\Users\\[username]\\AppData\\Roaming
SYSTEMROOT = os.environ["SYSTEMROOT"]       # C:\\Windows


# Common Path
REGISTRY = {
    'SAM': SYSTEMROOT + "\\System32\\config\\SAM",
    'SYSTEM': SYSTEMROOT + "\\System32\\config\\SYSTEM",
    'SECURITY': SYSTEMROOT + "\\System32\\config\\SECURITY",
    'SOFTWARE': SYSTEMROOT + "\\System32\\config\\SOFTWARE",
}
PREFETCH = SYSTEMROOT + '\\Prefetch\\'
WER = {
    'Windows7': LOCALAPPDATA + "\\Microsoft\\Windows\\WER\\ReportArchive\\",
    'Windows10': 'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive\\'
}
EVENTLOG = SYSTEMROOT + '\\System32\\Winevt\\logs\\'
JUMPLIST = [
    APPDATA + '\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\',      # AutomaticDestinations
    APPDATA + '\\Microsoft\\Windows\\Recent\\CustomDestinations\\'          # CustomDestinations
]
JUMPLIST_HASH = [
    '9839aec31243a928',     # [00] Excel 2010 x86
    '6e855c85de07bc6a',     # [01] Excel 2010 x64
    'f0275e8685d95486',     # [02] Excel 2013 x86
    'b8ab77100df80ab2',     # [03] Excel 2013, 2016 x64
    '9c7cc110ff56d1bd',     # [04] PowerPoint 2010 x86
    '5f6e7bc0fb699772',     # [05] PowerPoint 2010 x64
    'd00655d2aa12ff6d',     # [06] PowerPoint 2013, 2016 x64
    'a7bd71699cd38d1c',     # [07] Word 2010 x86
    '44a3621b32122d64',     # [08] Word 2010 x64
    'a4a5324453625195',     # [09] Word 2013 x86
    'fb3b0dbfee58fac8',     # [10] Word 365 x86
    'a18df73203b0340e',     # [11] Word 2016
    '28c8b86deab549a1',     # [12] Internet Explorer 8 / 9 / 10 (32-bit)
    '5da8f997fd5f9428',     # [13] Internet Explorer x64
    'e2a593822e01aed3',     # [14] Adobe Flash CS5 (32-bit)
    '23646679aaccfae0',     # [15] Adobe Reader 9
    '23646679aaccfae0',     # [16] Adobe Reader 9 x64
    'f0468ce1ae57883d',     # [17] Adobe Reader 7.1.0
    'c2d349a0e756411b',	    # [18] Adobe Reader 8.1.2
    '23646679aaccfae0',	    # [19] Adobe Acrobat 9.4.0
    'ee462c3b81abb6f6',     # [20] Adobe Reader X 10.1.0
    'de48a32edcbe79e4',     # [21] Acrobat Reader 15.x
    '5d696d521de238c3',     # [22] Chrome 9.0.597.84 / 12.0.742.100 / 13.0.785.215 / 26
    '9d1f905ce5044aee',     # [23] Edge Browser
]
RECENT = APPDATA + '\\Microsoft\\Windows\\Recent\\'

# Software Path
FLASH_ARTIFACT_PATH = {         # Adobe Flash Player
}
HWP_ARTIFACT_PATH = {           # HWP
    'Recent': APPDATA + '\\HNC\\Office\\Recent',
}
IE_ARTIFACT_PATH = {            # IE
    'Windows7': {
        'History': LOCALAPPDATA + '\\Microsoft\\Windows\\WebCache\\',   # Target: WebCacheV*.dat
        'Cache': {
            'IE10': LOCALAPPDATA + '\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\',
            'IE11': LOCALAPPDATA + '\\Microsoft\\Windows\\INetCookies\\'
        },
        'Download': {},
        'Cookie': {
            'IE10': APPDATA + '\\Microsoft\\Windows\\Cookies\\',
            'IE11': LOCALAPPDATA + '\\Microsoft\\Windows\\INetCache\IE\\',
        },
        'SessionRestore': LOCALAPPDATA + '\\Microsoft\\Internet Explorer\\Recovery\\'
    },
    'Windows10': {
        'History': LOCALAPPDATA + '\\Microsoft\\Windows\\WebCache\\',   # Target: WebCacheV*.dat
        'Cache': {
            'IE10': LOCALAPPDATA + '\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\',
            'IE11': LOCALAPPDATA + '\\Microsoft\\Windows\\INetCookies\\'
        },
        'Download': {

        },
        'Cookie': {
            'IE10': APPDATA + '\\Microsoft\\Windows\\Cookies\\',
            'IE11': LOCALAPPDATA + '\\Microsoft\\Windows\\INetCache\\IE\\',
        },
        'SessionRestore': LOCALAPPDATA + '\\Microsoft\\Internet Explorer\\Recovery\\',
    }
}
OFFICE_ARTIFACT_PATH = {        # MS-Office
    'Recent': APPDATA + '\\Microsoft\\Office\\Recent\\',
    'UnsavedFiles': LOCALAPPDATA + '\\Microsoft\\Office\\UnsavedFiles\\',
    '2010': {

    },
    '2013': {

    },
    '2016': {

    }
}
PDF_ARTIFACT_PATH = {           # PDF

}
