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

PYTHON3 = sys.version_info[0] == 3
ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

name_components = __name__.split(".")

ADDON_MODULE = name_components[0]
LIBADDON_NAME = name_components[1]

if ANKI21:
    ADDON_DIR = mw.addonManager.addonsFolder()
    JSPY_BRIDGE = "pycmd"
else:
    ADDON_DIR = mw.pm.addonFolder()
    if isWin:
        ADDON_DIR = ADDON_DIR.encode(SYS_ENCODING)
    JSPY_BRIDGE = "py.link"

ADDON_PATH = os.path.join(ADDON_DIR, ADDON_MODULE)

if isMac:
    PLATFORM = "mac"
elif isWin:
    PLATFORM = "win"
else:
    PLATFORM = "lin"
