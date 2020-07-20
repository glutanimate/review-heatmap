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

from abc import ABC
from typing import TYPE_CHECKING, Callable, Optional

from anki.hooks import addHook, remHook, wrap
from anki.stats import CollectionStats
from aqt.deckbrowser import DeckBrowser
from aqt.main import AnkiQt
from aqt.overview import Overview
from aqt.stats import DeckStats

from .controller import HeatmapController
from .renderer import HeatmapView

if TYPE_CHECKING:
    from aqt.deckbrowser import DeckBrowserContent
    from aqt.overview import OverviewContent


class HeatmapInjector(ABC):

    _view: HeatmapView

    def __init__(self, controller: HeatmapController):
        self._controller = controller

    def register(self):
        ...


# Deck Browser (Main view)
######################################################################


class DeckBrowserInjector(HeatmapInjector):

    _view = HeatmapView.deckbrowser

    def register(self):
        try:
            from aqt.gui_hooks import deck_browser_will_render_content

            deck_browser_will_render_content.append(
                self.on_deckbrowser_will_render_content
            )
        except (ImportError, ModuleNotFoundError):
            DeckBrowser._renderStats = wrap(
                DeckBrowser._renderStats,
                self.on_legacy_deckbrowser_render_stats,
                "around",
            )

    def on_deckbrowser_will_render_content(
        self, deck_browser: DeckBrowser, content: "DeckBrowserContent"
    ):
        heatmap_html = self._controller.render_for_view(self._view)
        content.stats += heatmap_html

    def on_legacy_deckbrowser_render_stats(
        self, deck_browser: DeckBrowser, _old
    ) -> str:
        """Add heatmap to _renderStats() return"""
        # self is deckbrowser
        original_html = _old(deck_browser)
        heatmap_html = self._controller.render_for_view(self._view)
        new_html = original_html + heatmap_html
        return new_html


# Overview (Deck view)
######################################################################


class OverviewInjector(HeatmapInjector):

    _view = HeatmapView.overview

    _overview_body: str = """
<center>
<h3>%(deck)s</h3>
%(shareLink)s
%(desc)s
%(table)s
%(stats)s
</center>
<script>$(function () { $("#study").focus(); });</script>
"""

    def register(self):
        try:
            from aqt.gui_hooks import overview_will_render_content

            overview_will_render_content.append(self.overview_will_render_content)
        except (ImportError, ModuleNotFoundError):
            Overview._body = self._overview_body
            Overview._renderPage = self.on_legacy_overview_render_page

    def overview_will_render_content(
        self, overview: Overview, content: "OverviewContent"
    ):
        heatmap_html = self._controller.render_for_view(
            self._view, current_deck_only=True
        )
        content.table += heatmap_html

    def on_legacy_overview_render_page(self, overview: Overview):
        """Replace original _renderPage()
        We use this instead of _table() in order to stay compatible
        with other add-ons
        (add-ons like more overview stats overwrite _table())
        TODO: consider using onProfileLoaded instead
        """
        # self is overview

        deck = overview.mw.col.decks.current()
        overview.sid = deck.get("sharedFrom")
        if overview.sid:
            overview.sidVer = deck.get("ver", None)
            shareLink = '<a class=smallLink href="review">Reviews and Updates</a>'
        else:
            shareLink = ""

        heatmap_html = self._controller.render_for_view(
            self._view, current_deck_only=True
        )

        overview.web.stdHtml(
            overview._body
            % dict(
                deck=deck["name"],
                shareLink=shareLink,
                desc=overview._desc(deck),
                table=overview._table(),
                stats=heatmap_html,
            ),
            css=["overview.css"],
            js=["jquery.js", "overview.js"],
        )


# Legacy stats window
######################################################################

# TODO: NewDeckStats

class DeckStatsInjector(HeatmapInjector):
    
    _view = HeatmapView.stats
    
    def register(self):
        CollectionStats.dueGraph = wrap(
            CollectionStats.dueGraph, self.on_collection_stats_due_graph, "around"
        )
        DeckStats.__init__ = wrap(DeckStats.__init__, self.on_deck_stats_init, "after")
        DeckStats.reject = wrap(DeckStats.reject, self.on_deck_stats_reject, "after")

    def on_deck_stats_init(self, deck_stats: DeckStats, mw: AnkiQt):
        deck_stats.form.web.onBridgeCmd = deck_stats._linkHandler
        # refresh heatmap on options change:
        addHook("reset", deck_stats.refresh)

    def on_deck_stats_reject(self, deck_stats):
        # clean up after ourselves:
        remHook("reset", deck_stats.refresh)

    def on_collection_stats_due_graph(
        self, collection_stats: CollectionStats, _old_due_graph: Callable
    ) -> str:
        """Wraps dueGraph and adds our heatmap to the stats screen"""
        # self is anki.stats.CollectionStats
        original_html = _old_due_graph(collection_stats)

        limhist: Optional[int] = None
        limfcst: Optional[int] = None

        if collection_stats.type == 0:
            limhist, limfcst = 31, 31
        elif collection_stats.type == 1:
            limhist, limfcst = 365, 365
        elif collection_stats.type == 2:
            limhist, limfcst = None, None

        heatmap_html = self._controller.render_for_view(
            self._view,
            limhist=limhist,
            limfcst=limfcst,
            current_deck_only=collection_stats.wholeCollection,
        )

        new_html = original_html + heatmap_html

        return new_html



def initialize_views(controller: HeatmapController):
    deck_browser_injector = DeckBrowserInjector(controller)
    deck_browser_injector.register()
    
    overview_injector = OverviewInjector(controller)
    overview_injector.register()
    
    deck_stats_injector = DeckStatsInjector(controller)
    deck_stats_injector.register()
