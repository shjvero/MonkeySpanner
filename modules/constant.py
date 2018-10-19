import os

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
WER = 'C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive\\'
EVENTLOG = SYSTEMROOT + '\\System32\\Winevt\\logs\\'
JUMPLIST = [
    APPDATA + '\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\',      # AutomaticDestinations
    APPDATA + '\\Microsoft\\Windows\\Recent\\CustomDestinations\\'          # CustomDestinations
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