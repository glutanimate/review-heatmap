# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
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
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Utility functions for interacting with Anki
"""

import os

from aqt import mw

from ..platform import ANKI20, PATH_ADDONS
from ..consts import ADDON


def debugInfo():
    """Return verbose info on add-ons and Anki installation"""
    info = ["{name} version {version}".format(name=ADDON.NAME,
                                              version=ADDON.VERSION)]
    if ANKI20:
        from aqt.qt import QT_VERSION_STR, PYQT_VERSION_STR
        from aqt import appVersion
        from anki.utils import platDesc
        info.append("Anki {version} (Qt {qt} PyQt {pyqt})".format(
            version=appVersion, qt=QT_VERSION_STR, pyqt=PYQT_VERSION_STR))
        info.append(platDesc())
        files = [f for f in os.listdir(PATH_ADDONS)
                 if f.endswith(".py")]
        info.append("Add-ons:\n\n" + repr(files))
    else:
        from aqt.utils import supportText
        info.append(supportText())

        addmgr = mw.addonManager
        info.append("Add-ons:\n\n" + "\n".join(
            addmgr.annotatedName(d) for d in addmgr.allAddons()))

    return "\n\n".join(info)
