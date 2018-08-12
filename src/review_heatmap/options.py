# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Options dialog and associated code

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from .config import (heatmap_colors, heatmap_modes, activity_stats,
                     default_config, default_prefs)

from .libaddon.widgets.options import OptionsDialog

from .consts import ANKI21

if ANKI21:
    from .forms5 import options as qtform_options  # noqa: F401
else:
    from .forms4 import options as qtform_options  # noqa: F401


# Widget <-> config mappings

widgets_options = (
    {
        "name": "selHmColor",
        "type": "combobox",
        "current": {
            "confPath": ("config", "colors"),
        },
        "items": {
            "getter": "getHeatmapColors"
        }
    },
    {
        "name": "selHmCalMode",
        "type": "combobox",
        "current": {
            "confPath": ("config", "mode")
        },
        "items": {
            "getter": "getHeatmapModes"
        }
    },
    {
        "name": "selActivity",
        "type": "combobox",
        "current": {
            "confPath": ("config", "stat")
        },
        "items": {
            "getter": "getActivityStats"
        }
    },
    {
        "name": "cbHmMain",
        "type": "checkbox",
        "current": {
            "confPath": ("prefs", "display", 0)
        }
    },
    {
        "name": "cbHmDeck",
        "type": "checkbox",
        "current": {
            "confPath": ("prefs", "display", 1)
        }
    },
    {
        "name": "cbHmStats",
        "type": "checkbox",
        "current": {
            "confPath": ("prefs", "display", 2)
        }
    },
    {
        "name": "cbStreakAll",
        "type": "checkbox",
        "current": {
            "confPath": ("prefs", "statsvis")
        }
    },
    {
        "name": "spinLimHist",
        "type": "spinbox",
        "current": {
            "confPath": ("config", "limhist")
        }
    },
    {
        "name": "spinLimFcst",
        "type": "spinbox",
        "current": {
            "confPath": ("config", "limfcst")
        }
    },
    {
        "name": "btnKeyToggle",
        "type": "keygrabber",
        "current": {
            "confPath": ("prefs", "hotkeys", "toggle")
        }
    },
    {
        "name": "dateLimData",
        "type": "dateedit",
        "current": {
            "confPath": ("config", "limdate")
        },
        "minimum": {
            "getter": "getColCreationTime"
        }
    },
    {
        "name": "listDecks",
        "type": "list",
        "current": {
            "confPath": ("config", "limdecks"),
            "getter": "getIgnoredDecks",
            "setter": "setIgnoredDecks"
        }
    },
)


class RevHmOptions(OptionsDialog):

    """
    Add-on-specific options dialog implementation
    """

    def __init__(self, conf, defaults, mw):
        self.mw = mw
        super(RevHmOptions, self).__init__(qtform_options, widgets_options,
                                           conf, defaults, parent=mw)

    def getColCreationTime(self):
        return self.mw.col.crt

    def getComboItems(self, dct):
        return list((val["label"], key) for key, val in dct.items())

    def getHeatmapColors(self):
        return self.getComboItems(heatmap_colors)

    def getHeatmapModes(self):
        return self.getComboItems(heatmap_modes)

    def getActivityStats(self):
        return self.getComboItems(activity_stats)

    # def getIgnoredDecks(self, cur):
    #     return ()

    # def setIgnoredDecks(self, cur):
    #     return ()


def invokeOptionsDialog(mw):
    """Call settings dialog"""
    conf = {"config": mw.col.conf['heatmap'],
            "prefs": mw.pm.profile['heatmap']}
    defaults = {"config": default_config,
                "prefs": default_prefs}
    dialog = RevHmOptions(conf, defaults, mw)
    ret = dialog.exec_()
    if not ret:
        return
    new_conf = dialog.getConfig(conf)
    del(dialog)
    mw.col.conf['heatmap'] = new_conf["config"]
    mw.pm.profile['heatmap'] = new_conf["prefs"]
    mw.col.setMod()
    mw.reset()
