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

heatmap_colors_fcst = {
    "light": (
        "#525252", "#616161", "#707070", "#7F7F7F", "#8E8E8E",
        "#9D9D9D", "#ACACAC", "#BBBBBB", "#CACACA", "#D9D9D9"
    ),
    "dark": (
        "#5d5f5f", "#585a5a", "#535555", "#4e5050", "#494b4b",
        "#444646", "#3f4141", "#3a3c3c", "#353737", "#313232"
    )
}

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
