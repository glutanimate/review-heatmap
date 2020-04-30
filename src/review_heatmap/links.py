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
Webview link handlers and associated components
"""

import re

import aqt
from anki.hooks import wrap
from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.overview import Overview
from aqt.qt import QWidget
from aqt.stats import DeckStats

from .config import config, heatmap_colors, heatmap_modes
from .gui.contrib import invokeContributionsDialog
from .gui.extra import invokeSnanki
from .gui.options import invokeOptionsDialog

# Link handler
######################################################################


def heatmapLinkHandler(self, url, _old=None):
    """Launches Browser when clicking on a graph subdomain"""
    if ":" in url:
        (cmd, arg) = url.split(":", 1)
    else:
        cmd, arg = url, ""
    if not cmd or cmd not in (
        "revhm_browse",
        "revhm_opts",
        "revhm_contrib",
        "revhm_modeswitch",
        "revhm_themeswitch",
        "revhm_snanki",
    ):
        return None if not _old else _old(self, url)

    if isinstance(self, QWidget):
        parent = self
    else:
        parent = mw

    if cmd == "revhm_opts":
        invokeOptionsDialog(parent)
    elif cmd == "revhm_contrib":
        invokeContributionsDialog(parent)
    elif cmd == "revhm_browse":
        invokeBrowser(arg)
    elif cmd == "revhm_modeswitch":
        cycleHmModes()
    elif cmd == "revhm_themeswitch":
        cycleHmThemes()
    elif cmd == "revhm_snanki":
        invokeSnanki(parent=parent)


def cycleHmThemes():
    themes = list(heatmap_colors.keys())
    cur_idx = themes.index(config["synced"]["colors"])
    new_idx = (cur_idx + 1) % len(themes)
    config["synced"]["colors"] = themes[new_idx]
    config.save()


def cycleHmModes():
    modes = list(heatmap_modes.keys())
    cur_idx = modes.index(config["synced"]["mode"])
    new_idx = (cur_idx + 1) % len(modes)
    config["synced"]["mode"] = modes[new_idx]
    config.save()


def invokeBrowser(search):
    browser = aqt.dialogs.open("Browser", mw)
    browser.form.searchEdit.lineEdit().setText(search)
    browser.onSearchActivated()


# Finder extensions
######################################################################

# LEGACY

# Used when clicking on heatmap date
def findRevlogEntries(self, val):
    """Find cards by revlog timestamp range"""
    args = val[0]
    cutoff1, cutoff2 = [int(i) for i in args.split(":")]
    return "c.id in (select cid from revlog where id between %d and %d)" % (
        cutoff1,
        cutoff2,
    )


def addFinders(self, col):
    """Add custom finder to search dictionary"""
    self.search["rid"] = self.findRevlogEntries


# NEW


def _find_cards_reviewed_between(start_date: int, end_date: int):
    # select from cards instead of just selecting uniques from revlog
    # in order to exclude deleted cards
    return mw.col.db.list(  # type: ignore
        "SELECT id FROM cards where id in "
        "(SELECT cid FROM revlog where id between ? and ?)",
        start_date,
        end_date,
    )


_re_rid = re.compile(r"^rid:([0-9]+):([0-9]+)$")


def find_rid(search: str):
    match = _re_rid.match(search)

    if not match:
        return False

    start_date = int(match[1])
    end_date = int(match[2])

    return _find_cards_reviewed_between(start_date, end_date)


def on_browser_will_search(search_context):
    search = search_context.search
    if search.startswith("rid"):
        found_ids = find_rid(search)
    else:
        return

    if found_ids is False:
        return

    search_context.card_ids = found_ids


# Hooks
######################################################################


def initializeLinks():
    Overview._linkHandler = wrap(Overview._linkHandler, heatmapLinkHandler, "around")
    DeckBrowser._linkHandler = wrap(
        DeckBrowser._linkHandler, heatmapLinkHandler, "around"
    )
    DeckStats._linkHandler = heatmapLinkHandler

    try:
        from aqt.gui_hooks import browser_will_search

        browser_will_search.append(on_browser_will_search)
    except (ImportError, ModuleNotFoundError):
        from anki.find import Finder

        Finder.findRevlogEntries = findRevlogEntries
        Finder.__init__ = wrap(Finder.__init__, addFinders, "after")
