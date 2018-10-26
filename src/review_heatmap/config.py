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
Handles add-on configuration
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from collections import OrderedDict

from aqt import mw

from .libaddon.anki.configmanager import ConfigManager

from .consts import ADDON_VERSION

__all__ = ["heatmap_colors", "heatmap_modes", "config_defaults", "config"]

# Order is important for a predictable selection dropdown (anki20)
# Preserving the (key, dict) tuple in case we need to provide additional
# info on each theme in the future.
heatmap_colors = OrderedDict((
    ("lime", {
        "label": "Lime"
    }),
    ("olive", {
        "label": "Olive"
    }),
    ("ice", {
        "label": "Ice"
    }),
    ("magenta", {
        "label": "Magenta"
    }),
    ("flame", {
        "label": "Flame"
    })
))

heatmap_modes = OrderedDict((
    ("year", {
        "label": "Yearly Overview",
        "domain": 'year',
        "subDomain": 'day',
        "range": 1,
        "domLabForm": "%Y"
    }),
    ("months", {
        "label": "Continuous Timeline",
        "domain": 'month',
        "subDomain": 'day',
        "range": 9,
        "domLabForm": "%b '%y"
    })
))

config_defaults = {
    "synced": {
        "colors": "lime",
        "mode": "year",
        "limdate": 0,
        "limhist": 0,
        "limfcst": 0,
        "limcdel": False,
        "limdecks": [],
        "version": ADDON_VERSION
    },
    "profile": {
        "display": {
            "deckbrowser": True,
            "overview": True,
            "stats": True
        },
        "statsvis": True,
        "hotkeys": {
            "toggle": "Ctrl+R"
        },
        "version": ADDON_VERSION
    }
}

config = ConfigManager(mw, config_dict=config_defaults,
                       conf_key="heatmap", reset_req=True)
