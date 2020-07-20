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
Overarching control of heatmap rendering and state
"""

from typing import TYPE_CHECKING, Optional

from aqt.main import AnkiQt

from .activity import ActivityReporter
from .renderer import HeatmapRenderer, HeatmapView
from .web_bridge import HeatmapBridge
from .errors import CollectionError, ReviewHeatmapError

if TYPE_CHECKING:
    from anki.collection import Collection
    from .libaddon.anki.configmanager import ConfigManager


class HeatmapController:
    def __init__(self, mw: AnkiQt, config: "ConfigManager"):
        self._mw = mw
        self._config: ConfigManager = config

        self._bridge: Optional[HeatmapBridge] = HeatmapBridge(self._mw, self._config)
        self._bridge.register()
        self._reporter: Optional[ActivityReporter] = None
        self._renderer: Optional[HeatmapRenderer] = None

    def register(self):
        try:
            from aqt.gui_hooks import collection_did_load, profile_will_close

            # FIXME: gui_hooks.collection_did_load instead doesn't have equivalent
            # for unloading collection unfortunately (to account for unloading during
            # sync, etc.)
            collection_did_load.append(self._on_collection_did_load)
            profile_will_close.append(self._on_profile_will_close)
        except (ImportError, ModuleNotFoundError):
            from anki.hooks import addHook

            addHook("colLoading", self._on_collection_did_load)
            addHook("unloadProfile", self._on_profile_will_close)

    def render_for_view(
        self,
        view: HeatmapView,
        limhist: Optional[int] = None,
        limfcst: Optional[int] = None,
        current_deck_only: bool = False,
    ) -> str:
        if not self._renderer:
            # colLoading is not reliable on legacy Anki, so attempt to
            # initialize on demand
            self._on_collection_did_load(self._mw.col)
            if not self._renderer:
                raise ReviewHeatmapError("Could not initalize heatmap renderer.")
        return self._renderer.render(view, limhist, limfcst, current_deck_only)

    def _on_collection_did_load(self, col: Optional["Collection"]):
        if not col:
            raise CollectionError("Collection not properly initialized.")

        self._reporter = ActivityReporter(col, self._config)
        self._renderer = HeatmapRenderer(self._mw, self._reporter, self._config)

    def _on_profile_will_close(self):
        self._reporter.unload_collection()
        # TODO: more unloading needed?


def initialize_controller(mw: "AnkiQt", config: "ConfigManager") -> HeatmapController:
    controller = HeatmapController(mw, config)
    controller.register()
    mw._review_heatmap = controller
    return controller
