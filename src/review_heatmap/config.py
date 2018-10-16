# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles the add-on configuration

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
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
