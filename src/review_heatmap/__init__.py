# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https//glutanimate.com/>
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
Initializes add-on components.
"""

from ._version import __version__  # noqa: F401


def checkFor2114ImportError():
    from .consts import ADDON

    try:
        # litmus test for Anki import bug
        from .libaddon.platform import anki_version  # noqa: F401

        return True
    except ImportError as e:
        print(e)
        # Disable add-on and inform user of the bug
        from aqt.utils import showWarning
        from aqt import mw
        from anki import version as anki_version

        mw.addonManager.toggleEnabled(__name__, enable=False)

        bug = "https://anki.tenderapp.com/discussions/ankidesktop/34836"
        downloads = "https://apps.ankiweb.net#download"
        beta = "https://apps.ankiweb.net/downloads/beta/"
        vers = "2.1.15"
        title = "Warning: {name} disabled".format(name=ADDON.NAME)
        msg = (
            "<b>WARNING</b>: {name} had to be disabled because the "
            "version of Anki that is currently installed on your system "
            "({anki_version}) is incompatible with the add-on.<br><br> "
            "Earlier releases of Anki like this one "
            "suffer from a <a href='{bug}'>bug</a> that breaks "
            "{name} and many other add-ons on your system. "
            "In order to fix this you will have to update Anki "
            "to version {vers} or higher.<br><br>"
            "As of writing this message, Anki {vers} is still in "
            "beta testing, but that might have "
            "changed in the meantime. Please check with the "
            "<a href='{downloads}'>releases page</a> to see if {vers} "
            "or a later release is available, otherwise download and "
            "install the 2.1.15 beta <a href='{beta}'>here</a>.<br><br>"
            "After updating Anki, please re-enable "
            "{name} by heading to Tools → Add-ons, selecting the "
            "add-on, and clicking <i>Toggle Enabled</i>.".format(
                name=ADDON.NAME,
                anki_version=anki_version,
                bug=bug,
                vers=vers,
                downloads=downloads,
                beta=beta,
            )
        )

        showWarning(msg, title=title, textFormat="rich")

        return False


def initializeAddon():
    """Initializes add-on after performing a few checks
    
    Allows more fine-grained control over add-on execution, which can
    be helpful when implementing workarounds for Anki bugs (e.g. the module
    import bug present in all Anki 2.1 versions up to 2.1.14)
    """

    if not checkFor2114ImportError():
        return False

    from .consts import ADDON
    from .libaddon.consts import setAddonProperties

    setAddonProperties(ADDON)

    from .libaddon.debug import maybeStartDebugging

    maybeStartDebugging()

    from .gui import initializeQtResources
    from .gui.options import initializeOptions
    from .views import initializeViews
    from .links import initializeLinks

    initializeQtResources()
    initializeOptions()
    initializeViews()
    initializeLinks()


initializeAddon()
