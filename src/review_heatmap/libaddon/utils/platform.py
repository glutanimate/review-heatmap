# -*- coding: utf-8 -*-

"""
Add-on agnostic constants

Also tries to import parent-level consts file to supply
add-on-specific constants to modules of this package.

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import sys
import os
from anki import version
from anki.utils import isMac, isWin

ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()
if ANKI21:
    ADDON_PATH = os.path.dirname(__file__)
else:
    ADDON_PATH = os.path.dirname(__file__).decode(SYS_ENCODING)

if isMac:
    PLATFORM = "mac"
elif isWin:
    PLATFORM = "win"
else:
    PLATFORM = "lin"
