# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Constants providing information on current system and Anki platform
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
