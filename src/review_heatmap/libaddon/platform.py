# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys
import os
from aqt import mw
from anki import version
from anki.utils import isMac, isWin

__all__ = ["PYTHON3", "ANKI21", "SYS_ENCODING", "MODULE_ADDON",
           "MODULE_LIBADDON", "DIRECTORY_ADDONS", "JSPY_BRIDGE",
           "PATH_ADDON", "PATH_USERFILES", "PLATFORM"]

PYTHON3 = sys.version_info[0] == 3
ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

name_components = __name__.split(".")

MODULE_ADDON = name_components[0]
MODULE_LIBADDON = name_components[1]

if ANKI21:
    DIRECTORY_ADDONS = mw.addonManager.addonsFolder()
    JSPY_BRIDGE = "pycmd"
else:
    DIRECTORY_ADDONS = mw.pm.addonFolder()
    if isWin:
        DIRECTORY_ADDONS = DIRECTORY_ADDONS.encode(SYS_ENCODING)
    JSPY_BRIDGE = "py.link"

PATH_ADDON = os.path.join(DIRECTORY_ADDONS, MODULE_ADDON)
PATH_USERFILES = os.path.join(PATH_ADDON, "user_files")

if isMac:
    PLATFORM = "mac"
elif isWin:
    PLATFORM = "win"
else:
    PLATFORM = "lin"
