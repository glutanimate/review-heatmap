# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles the add-on configuration

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from collections import OrderedDict

from aqt import mw

from .libaddon.utils.config import ConfigManager


heatmap_colors = OrderedDict((
    ("olive", {
        "label": "Olive",
        "colors": ("#dae289", "#bbd179", "#9cc069", "#8ab45d", "#78a851",
                   "#669d45", "#648b3f", "#637939", "#4f6e30", "#3b6427")
    }),
    ("lime", {
        "label": "Lime",
        "colors": ("#d6e685", "#bddb7a", "#a4d06f", "#8cc665", "#74ba58",
                   "#5cae4c", "#44a340", "#378f36", "#2a7b2c", "#1e6823")
    }),
    ("ice", {
        "label": "Ice",
        "colors": ("#a8d5f6", "#95c8f3", "#82bbf0", "#70afee", "#5da2eb",
                   "#4a95e8", "#3889e6", "#257ce3", "#126fe0", "#0063de")
    }),
    ("magenta", {
        "label": "Magenta",
        "colors": ("#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#ea4e9c",
                   "#dd3497", "#ae017e", "#7a0177", "#610070", "#49006a")
    }),
    ("flame", {
        "label": "Flame",
        "colors": ("#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc6d33",
                   "#fc4e2a", "#e31a1c", "#d00d21", "#bd0026", "#800026")
    })
))

heatmap_modes = OrderedDict((
    ("year", {
        "label": "Continuous year",
        "domain": 'year',
        "subDomain": 'day',
        "range": 1,
        "domLabForm": "%Y"
    }),
    ("months", {
        "label": "Split into months",
        "domain": 'month',
        "subDomain": 'day',
        "range": 12,
        "domLabForm": "%b '%y"
    })
))

activity_stats = OrderedDict((
    ("a", {"label": "All reviews"}),
    ("n", {"label": "New cards"}),
    ("r", {"label": "Review cards"}),
    ("c", {"label": "Cards added"})
))

config_defaults = {
    "synced": {
        "colors": "lime",
        "mode": "year",
        "stat": "a",
        "limdate": 0,
        "limhist": 0,
        "limfcst": 0,
        "limcdel": False,
        "limdecks": []
    },
    "profile": {
        "display": [True, True, True],
        "statsvis": True,
        "hotkeys": {"toggle": "Ctrl+R"},
        "decks": {}
    }
}

config = ConfigManager(mw, config_dict=config_defaults,
                       conf_key="heatmap", reset_req=True)
