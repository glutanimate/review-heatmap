# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import sys
import os
from aqt import mw
from anki import version
from anki.utils import isMac, isWin

def addonsFolder():
    path = mw.pm.addonFolder()
    if isWin:
        path = path.encode(sys.getfilesystemencoding())
    return path

PYTHON3 = sys.version_info[0] == 3
ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

ADDON_MODULE = __name__.split(".")[0]
if ANKI21:
    ADDON_DIR = mw.addonManager.addonsFolder()
    JSPY_BRIDGE = "pycmd"
else:
    ADDON_DIR = addonsFolder()
    JSPY_BRIDGE = "py.link"
ADDON_PATH = os.path.join(ADDON_DIR, ADDON_MODULE)

if isMac:
    PLATFORM = "mac"
elif isWin:
    PLATFORM = "win"
else:
    PLATFORM = "lin"
