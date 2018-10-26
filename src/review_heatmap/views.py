# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2018  Aristotelis P. <https//glutanimate.com/>
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from anki.hooks import wrap

from aqt.qt import *

from aqt import mw
from aqt.overview import Overview
from aqt.deckbrowser import DeckBrowser
from aqt.stats import DeckStats
from anki.stats import CollectionStats
from anki.hooks import addHook, remHook

from .libaddon.platform import ANKI21

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

    if not ANKI21:
        self.web.stdHtml(self._body % dict(
            deck=deck['name'],
            shareLink=shareLink,
            desc=self._desc(deck),
            table=self._table(),
            stats=hmap.generate(view="overview")
        ), self.mw.sharedCSS + self._css)
    else:
        self.web.stdHtml(self._body % dict(
            deck=deck['name'],
            shareLink=shareLink,
            desc=self._desc(deck),
            table=self._table(),
            stats=hmap.generate(view="overview")
        ),
            css=["overview.css"],
            js=["jquery.js", "overview.js"])


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
    addHook('reset', self.refresh)


def deckStatsInit20(self, mw):
    """Custom stats window that uses AnkiWebView instead of QWebView"""
    # self is aqt.stats.DeckWindow
    import aqt
    from aqt.webview import AnkiWebView
    from aqt.utils import restoreGeom, maybeHideClose, addCloseShortcut
    #########################################################
    QDialog.__init__(self, mw, Qt.Window)
    self.mw = mw
    self.name = "deckStats"
    self.period = 0
    self.form = aqt.forms.stats.Ui_Dialog()
    self.oldPos = None
    self.wholeCollection = False
    self.setMinimumWidth(700)
    f = self.form
    f.setupUi(self)
    #########################################################
    # remove old webview created in form:
    # (TODO: find a less hacky solution)
    f.verticalLayout.removeWidget(f.web)
    f.web.deleteLater()
    f.web = AnkiWebView()  # need to use AnkiWebView for linkhandler to work
    f.web.setLinkHandler(self._linkHandler)
    self.form.verticalLayout.insertWidget(0, f.web)
    addHook('reset', self.refresh)
    #########################################################
    restoreGeom(self, self.name)
    b = f.buttonBox.addButton(_("Save Image"), QDialogButtonBox.ActionRole)
    b.clicked.connect(self.browser)
    b.setAutoDefault(False)
    c = self.connect
    s = SIGNAL("clicked()")
    c(f.groups, s, lambda: self.changeScope("deck"))
    f.groups.setShortcut("g")
    c(f.all, s, lambda: self.changeScope("collection"))
    c(f.month, s, lambda: self.changePeriod(0))
    c(f.year, s, lambda: self.changePeriod(1))
    c(f.life, s, lambda: self.changePeriod(2))
    c(f.web, SIGNAL("loadFinished(bool)"), self.loadFin)
    maybeHideClose(self.form.buttonBox)
    addCloseShortcut(self)
    self.refresh()
    self.show()  # show instead of exec in order for browser to open properly

def deckStatsReject(self):
    # clean up after ourselves:
    remHook('reset', self.refresh)

def initializeViews():
    CollectionStats.dueGraph = wrap(
        CollectionStats.dueGraph, collectionStatsDueGraph, "around")
    Overview._body = ov_body
    Overview._renderPage = overviewRenderPage
    DeckBrowser._renderStats = wrap(
        DeckBrowser._renderStats, deckbrowserRenderStats, "around")
    if ANKI21:
        DeckStats.__init__ = wrap(DeckStats.__init__, deckStatsInit21, "after")
    else:
        DeckStats.__init__ = deckStatsInit20
    DeckStats.reject = wrap(DeckStats.reject, deckStatsReject)
    # Initially set up hotkey:
    addHook("profileLoaded", initializeHotkey)
    # Update hotkey on config save:
    addHook("config_saved_heatmap", initializeHotkey)
