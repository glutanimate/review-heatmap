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
Integration with Anki views
"""

from anki.hooks import addHook, remHook, wrap
from anki.stats import CollectionStats
from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.overview import Overview
from aqt.qt import *
from aqt.stats import DeckStats

from .config import config
from .heatmap import HeatmapCreator

# Common
######################################################################


def toggleHeatmap():
    """Toggle heatmap display on demand"""
    state = mw.state.lower()
    hm_active = config["profile"]["display"].get(state, None)
    if hm_active is None:
        # unrecognized mw state
        return False
    config["profile"]["display"][state] = not hm_active
    mw.reset()


def initializeHotkey():
    """
    Create toggle action if it does not exist, yet, and assign it the
    hotkey defined in the user config
    """
    toggle_action = getattr(mw, "_hmToggleAction", None)

    if toggle_action is None:
        toggle_action = QAction(mw, triggered=toggleHeatmap)
        mw.addAction(toggle_action)
        mw._hmToggleAction = toggle_action

    hotkey = config["profile"]["hotkeys"]["toggle"]
    toggle_action.setShortcut(QKeySequence(hotkey))


######################################################################
# LEGACY
######################################################################


# Deck Browser (Main view)
######################################################################


def deckbrowserRenderStats(self, _old):
    """Add heatmap to _renderStats() return"""
    # self is deckbrowser
    ret = _old(self)
    hmap = HeatmapCreator(config, whole=True)
    html = ret + hmap.generate(view="deckbrowser")
    return html


# Overview (Deck view)
######################################################################

ov_body = """
<center>
<h3>%(deck)s</h3>
%(shareLink)s
%(desc)s
%(table)s
%(stats)s
</center>
<script>$(function () { $("#study").focus(); });</script>
"""


def overviewRenderPage(self):
    """Replace original _renderPage()
    We use this instead of _table() in order to stay compatible
    with other add-ons
    (add-ons like more overview stats overwrite _table())
    TODO: consider using onProfileLoaded instead
    """
    # self is overview
    deck = self.mw.col.decks.current()
    self.sid = deck.get("sharedFrom")
    if self.sid:
        self.sidVer = deck.get("ver", None)
        shareLink = '<a class=smallLink href="review">Reviews and Updates</a>'
    else:
        shareLink = ""

    hmap = HeatmapCreator(config, whole=False)

    self.web.stdHtml(
        self._body
        % dict(
            deck=deck["name"],
            shareLink=shareLink,
            desc=self._desc(deck),
            table=self._table(),
            stats=hmap.generate(view="overview"),
        ),
        css=["overview.css"],
        js=["jquery.js", "overview.js"],
    )


# CollectionStats (Stats window)
######################################################################


def collectionStatsDueGraph(self, _old):
    """Wraps dueGraph and adds our heatmap to the stats screen"""
    # self is anki.stats.CollectionStats
    ret = _old(self)
    if self.type == 0:
        limhist, limfcst = 31, 31
    elif self.type == 1:
        limhist, limfcst = 365, 365
    elif self.type == 2:
        limhist, limfcst = None, None
    hmap = HeatmapCreator(config, whole=self.wholeCollection)
    report = hmap.generate(view="stats", limhist=limhist, limfcst=limfcst)
    return report + ret


def deckStatsInit21(self, mw):
    self.form.web.onBridgeCmd = self._linkHandler
    # refresh heatmap on options change:
    addHook("reset", self.refresh)


def deckStatsReject(self):
    # clean up after ourselves:
    remHook("reset", self.refresh)


######################################################################
# NEW HOOKS
######################################################################


def on_deckbrowser_will_render_content(deck_browser, content):
    heatmap = HeatmapCreator(config, whole=True)
    content.stats += heatmap.generate(view="deckbrowser")


def on_overview_will_render_content(overview, content):
    heatmap = HeatmapCreator(config, whole=False)
    content.table += heatmap.generate(view="overview")


def initializeViews():
    try:
        from aqt.gui_hooks import (
            deck_browser_will_render_content,
            overview_will_render_content,
        )

        deck_browser_will_render_content.append(on_deckbrowser_will_render_content)
        overview_will_render_content.append(on_overview_will_render_content)
    except (ImportError, ModuleNotFoundError):
        Overview._body = ov_body
        Overview._renderPage = overviewRenderPage
        DeckBrowser._renderStats = wrap(
            DeckBrowser._renderStats, deckbrowserRenderStats, "around"
        )

    # TODO: Submit Anki PR to add hook to CollectionStats.report
    CollectionStats.dueGraph = wrap(
        CollectionStats.dueGraph, collectionStatsDueGraph, "around"
    )
    DeckStats.__init__ = wrap(DeckStats.__init__, deckStatsInit21, "after")
    DeckStats.reject = wrap(DeckStats.reject, deckStatsReject)

    # Initially set up hotkey:
    # TODO: Migrate to config.json storage, so that profile hook is not required
    try:
        from aqt.gui_hooks import profile_did_open

        profile_did_open.append(initializeHotkey)
    except (ImportError, ModuleNotFoundError):
        addHook("profileLoaded", initializeHotkey)

    # Update hotkey on config save:
    addHook("config_saved_heatmap", initializeHotkey)
