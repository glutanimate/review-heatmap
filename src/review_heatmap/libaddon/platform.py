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
Provides information on Anki version and platform
"""

import sys
import os

from aqt import mw

try:
    from anki.buildinfo import version as anki_version
except (ImportError, ModuleNotFoundError):
    from anki import version as anki_version  # type: ignore[attr-defined, no-redef]

try:
    from anki.utils import is_mac, is_win
except (ImportError, ModuleNotFoundError):
    from anki.utils import isMac as is_mac  # type: ignore[attr-defined, no-redef]
    from anki.utils import isWin as is_win  # type: ignore[attr-defined, no-redef]

from .utils import ensureExists

if is_mac:
    PLATFORM = "mac"
elif is_win:
    PLATFORM = "win"
else:
    PLATFORM = "lin"

SYS_ENCODING = sys.getfilesystemencoding()
PYTHON3 = sys.version_info[0] == 3
ANKI20 = anki_version.startswith("2.0.")

name_components = __name__.split(".")

MODULE_ADDON = name_components[0]
MODULE_LIBADDON = name_components[1]

PATH_ADDONS = mw.pm.addonFolder()

if ANKI20:
    JSPY_BRIDGE = "py.link"
else:
    JSPY_BRIDGE = "pycmd"

PATH_THIS_ADDON = os.path.join(PATH_ADDONS, MODULE_ADDON)


def schedVer():
    if ANKI20:
        return 1
    if not mw.col:  # collection not loaded
        return None
    return mw.col.schedVer()


def pathUserFiles():
    user_files = os.path.join(PATH_THIS_ADDON, "user_files")
    return ensureExists(user_files)


def pathMediaFiles():
    return mw.col.media.dir()


def is_anki_version_in_range(lower: str, upper=None):
    """Check whether anki version is in specified range

    By default the upper boundary is set to infinite

    Arguments:
        lower {str} -- minimum version (inclusive)

    Keyword Arguments:
        upper {str} -- maximum version (exclusive) (default: {None})

    Returns:
        bool -- Whether anki version is in specified range
    """
    return is_version_in_range(anki_version, lower, upper=upper)


def is_qt_version_in_range(lower, upper=None):
    """Check whether Qt version is in specified range

    By default the upper boundary is set to infinite

    Arguments:
        lower {str} -- minimum version (inclusive)

    Keyword Arguments:
        upper {str} -- maximum version (exclusive) (default: {None})

    Returns:
        bool -- Whether Qt version is in specified range
    """
    from aqt.qt import QT_VERSION_STR
    return is_version_in_range(QT_VERSION_STR, lower, upper=upper)


def is_version_in_range(current, lower, upper=None):
    """Generic version checker

    Checks whether specified version is in specified range

    Arguments:
        current {str} -- current version
        lower {str} -- minimum version (inclusive)

    Keyword Arguments:
        upper {str} -- maximum version (exclusive) (default: {None})

    Returns:
        bool -- Whether current version is in specified range
    """
    from ._vendor.packaging import version

    if upper is not None:
        ankiv_parsed = version.parse(current)
        return (ankiv_parsed >= version.parse(lower) and
                ankiv_parsed < version.parse(upper))

    return version.parse(current) >= version.parse(lower)
