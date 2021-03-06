import os

TITLE = "MonkeySpanner"
ICON_PATH = "logo.ico"

# OS
WIN7 = 'Windows7'
WIN10 = 'Windows10'

# Software Number
ADOBE_READER = 1
ADOBE_FLASH_PLAYER = 2
EDGE = 3
HWP = 4
IE = 5
OFFICE = 6
LPE = 7

# Software Keyword
ADOBE_READER_KEYWORD = "Adobe Reader"
ADOBE_FLASH_PLAYER_KEYWORD = "Adobe Flash Player"
EDGE_KEYWORD = "Microsoft Edge"
HWP_KEYWORD = "Hancom Word Process"
IE_KEYWORD = "Internet Explorer"
OFFICE_KEYWORD = "MS-Office"
LPE_KEYWORD = "Kernel(Local-Privilege-Escalation)"

SOFTWARE_SELECTION = [
    "---- Select Software ----",
    ADOBE_READER_KEYWORD,
    ADOBE_FLASH_PLAYER_KEYWORD,
    EDGE_KEYWORD,
    HWP_KEYWORD,
    IE_KEYWORD,
    OFFICE_KEYWORD,
    LPE_KEYWORD,
]

# Artifact List
PREFETCH_KEYWORD = "Prefetch"
EVENTLOG_KEYWORD = "EventLog"
WER_KEYWORD = "ErrorReport"
HISTORY_KEYWORD = "History"
# DOWNLOAD_KEYWORD = "Download"
CACHE_KEYWORD = "WebCache"
REGISTRY_KEYWORD = "Registry"
LNKFILE_KEYWORD = "JumpList[L]"
DESTLIST_KEYWORD = "JumpList[D]"

ArtifactList = [
    PREFETCH_KEYWORD,
    EVENTLOG_KEYWORD,
    WER_KEYWORD,
    HISTORY_KEYWORD,
    CACHE_KEYWORD,
    REGISTRY_KEYWORD,
    LNKFILE_KEYWORD,
    DESTLIST_KEYWORD
]

ColorList = {
    "Gray": 0,
    "Red": 1,
    "Orange": 2,
    "Yellow": 3,
    "Green": 4,
    "Blue": 5,
    "Navy": 6,
    "Purple": 7
}

# Table Header
TableHeader = {
    PREFETCH_KEYWORD: ["Timeline", "File Name", "Executable Name", "Action", ""],                       # 4 columns
    WER_KEYWORD: ["Modified Time", "Path", "Module", "Exception Code", "Created Time"],                 # 5 columns
    REGISTRY_KEYWORD: ["Modified Time", "Execution Path", "Size", "Exec Flag", "Registry Key"],         # 5 columns
    LNKFILE_KEYWORD: ["Modified Time", "File Path", "Drive Type", "Size", "Created Time"],              # 5 columns
    DESTLIST_KEYWORD: ["Timestamp", "File Path", "File Name", "Access", "Last Recorded Time"],    # 5 columns
    EVENTLOG_KEYWORD: ["Logged Time", "Provider Name", "Event ID", "Level", "Data"],                    # 5 columns
    HISTORY_KEYWORD: ["Accessed Time", "URL", "Modified Time", "", ""],                                 # 3 columns
    CACHE_KEYWORD: ["Accessed Time", "URL", "File Name", "Size", "Created Time"],                       # 5 columns
    # "Download": ["Accessed Time", "URL", "File Name", "Size", "Download Path"],                       # 5 columns
}

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
    WIN7: LOCALAPPDATA + "\\Microsoft\\Windows\\WER\\ReportArchive\\",
    WIN10: 'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive\\'
}
EVENTLOG = SYSTEMROOT + '\\System32\\Winevt\\logs\\'
JUMPLIST = [
    APPDATA + '\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\',      # AutomaticDestinations
    APPDATA + '\\Microsoft\\Windows\\Recent\\CustomDestinations\\'          # CustomDestinations
]

JUMPLIST_HASH = [
    ['Excel 2010 (32-bit)', '9839aec31243a928'],            # [00]
    ['Excel 2010 (64-bit)', '6e855c85de07bc6a'],            # [01]
    ['Excel 2013 (32-bit)', 'f0275e8685d95486'],            # [02]
    ['Excel 2013, 2016 (64-bit)', 'b8ab77100df80ab2'],      # [03]
    ['PowerPoint 2010 (32-bit)', '9c7cc110ff56d1bd'],       # [04]
    ['PowerPoint 2010 (64-bit)', '5f6e7bc0fb699772'],       # [05]
    ['PowerPoint 2013, 2016 (64-bit)', 'd00655d2aa12ff6d'], # [06]
    ['Word 2010 (32-bit)', 'a7bd71699cd38d1c'],             # [07]
    ['Word 2010 (64-bit)', '44a3621b32122d64'],             # [08]
    ['Word 2013 (32-bit)', 'a4a5324453625195'],             # [09]
    ['Word 365 (32-bit)', 'fb3b0dbfee58fac8'],              # [10]
    ['Word 2016 (64-bit)', 'a18df73203b0340e'],             # [11]
    ['Internet Explorer 8/9/10 (32-bit)', '28c8b86deab549a1'],  # [12]
    ['Internet Explorer 11 (64-bit)', '5da8f997fd5f9428'],      # [13]
    ['Adobe Flash CS5 (32-bit)', 'e2a593822e01aed3'],       # [14]
    ['HWP 2010', '20f18d57e149e379'],                       # [15]
    ['HWP 2014', '35a932d3d281dbfd'],                       # [16]
    ['HWP 2018', 'bcc51871d3e0b707'],                       # [17]
    ['Adobe Acrobat 9.4.0', '23646679aaccfae0'],            # [18]
    ['Adobe Reader 9', '23646679aaccfae0'],                 # [19]
    ['Adobe Reader 7.1.0', 'f0468ce1ae57883d'],             # [20]
    ['Adobe Reader 8.1.2', 'c2d349a0e756411b'],             # [21]
    ['Adobe Reader X 10.1.0', 'ee462c3b81abb6f6'],          # [22]
    ['Acrobat Reader 15.x', 'de48a32edcbe79e4'],            # [23]
    ['Chrome 9.0.597.84 / 12.0.742.100 / 13.0.785.215 / 26', '5d696d521de238c3'],     # [24]
    ['Edge 42.17134.1.0', '9d1f905ce5044aee'],                           # [25]
    ['Edge 44.17763.1.0', '90ca02effa84052f'],                           # [26]
]

RECENT = APPDATA + '\\Microsoft\\Windows\\Recent\\'
APPCOMPAT = SYSTEMROOT + "\\AppCompat\\Programs\\"

# Software Path
FLASH_ARTIFACT_PATH = {         # Adobe Flash Player
}
HWP_ARTIFACT_PATH = {           # HWP
    'Recent': APPDATA + '\\HNC\\Office\\Recent',
}
IE_ARTIFACT_PATH = {            # IE
    WIN7: {
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
    WIN10: {
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

