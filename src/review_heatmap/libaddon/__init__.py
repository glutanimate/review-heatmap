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
Libaddon: A helper library for Anki add-on development

Provides access to a number of commonly used modules shared across
many of my add-ons.

Please note that this package is not fit for general use yet, as it is
still is too specific to my own add-ons and implementations.

This module is the package entry-point.
"""

from ._version import __version__  # noqa: F401


def maybeVendorTyping():
    try:
        import typing  # noqa: F401
        import types  # noqa: F401
    except ImportError:
        registerLegacyVendorDir()


def registerLegacyVendorDir():
    """Some modules like "typing" cannot be properly vendorized, so fall back
    to hacky sys.path modifications if necessary
    NOTE: make sure not to use vendored legacy dependencies before running this
    """
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_vendor_legacy"))


def checkFor2114ImportError(name: str) -> bool:
    try:
        # litmus test for Anki import bug
        from .platform import anki_version  # noqa: F401

        return True
    except ImportError:
        # Disable add-on and inform user of the bug
        from aqt.utils import showWarning
        from aqt import mw
        from anki import version as anki_version

        if mw is None:
            return False

        mw.addonManager.toggleEnabled(__name__, enable=False)

        bug = "https://anki.tenderapp.com/discussions/ankidesktop/34836"
        downloads = "https://apps.ankiweb.net#download"
        vers = "2.1.15"
        title = "Warning: {name} disabled".format(name=name)
        msg = (
            "<b>WARNING</b>: {name} had to be disabled because the "
            "version of Anki that is currently installed on your system "
            "({anki_version}) is incompatible with the add-on.<br><br> "
            "Earlier releases of Anki like this one "
            "suffer from a <a href='{bug}'>bug</a> that breaks "
            "{name} and many other add-ons on your system. "
            "In order to fix this you will have to update Anki "
            "to version <a href='{downloads}'>{vers} or higher</a>.<br><br>"
            "After updating Anki, please re-enable "
            "{name} by heading to Tools → Add-ons, selecting the "
            "add-on, and clicking <i>Toggle Enabled</i>.".format(
                name=name,
                anki_version=anki_version,
                bug=bug,
                vers=vers,
                downloads=downloads,
            )
        )

        showWarning(msg, title=title, textFormat="rich")

        return False
