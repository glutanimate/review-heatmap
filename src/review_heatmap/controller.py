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
from .errors import CollectionError

if TYPE_CHECKING:
    from .libaddon.anki.configmanager import ConfigManager


class HeatmapController:
    def __init__(self, mw: AnkiQt, config: "ConfigManager"):
        self._mw = mw
        self._config: ConfigManager = config

        self._bridge: Optional[HeatmapBridge] = None
        self._reporter: Optional[ActivityReporter] = None
        self._renderer: Optional[HeatmapRenderer] = None

    def register(self):
        self._bridge.register()
        try:
            from aqt.gui_hooks import profile_did_open, profile_will_close

            # TODO: Use gui_hooks.collection_did_load instead? Doesn't have equivalent
            # for unloading collection, unfortunately (to account for unloading during
            # sync, etc.)
            profile_did_open.append(self.on_profile_did_open)
            profile_will_close.append(self.on_profile_will_close)
        except (ImportError, ModuleNotFoundError):
            from anki.hooks import addHook

            addHook("profileLoaded", self.on_profile_did_open)
            addHook("unloadProfile", self.on_profile_will_close)

    def on_profile_did_open(self):
        if not self._mw.col:
            raise CollectionError()
        
        self._bridge: Optional[HeatmapBridge] = HeatmapBridge(self._mw, self._config)
        self._reporter = ActivityReporter(self._mw.col, self._config)
        self._renderer: Optional[HeatmapRenderer] = HeatmapRenderer(
            self._mw, self._reporter, self._config
        )

    def on_profile_will_close(self):
        self._reporter.unload_collection()
        # TODO: more unloading needed?

    def render_for_view(
        self,
        view: HeatmapView,
        limhist: Optional[int] = None,
        limfcst: Optional[int] = None,
        current_deck_only: bool = False,
    ) -> str:
        if not self._renderer:
            # TODO: better handling
            raise Exception
        return self._renderer.render(view, limhist, limfcst, current_deck_only)


def initialize_controller(mw: "AnkiQt", config: "ConfigManager"):
    controller = HeatmapController(mw, config)
    mw._review_heatmap = controller
