# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Options dialog and associated code

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import time
from collections import OrderedDict

from aqt.qt import *

from aqt.studydeck import StudyDeck

from .config import (heatmap_colors, heatmap_modes, activity_stats,
                     default_config, default_prefs)

from .libaddon.gui.options import OptionsDialog

from .consts import ANKI21

if ANKI21:
    from .forms5 import options as option_qtform  # noqa: F401
else:
    from .forms4 import options as option_qtform  # noqa: F401


# Widget <-> config mappings

# order is important as events might fire when setting widget
# properties
option_widgets = OrderedDict((
    ("selHmColor",
        {
            "value": {
                "confPath": ("config", "colors"),
            },
            "items": {
                "getter": "getHeatmapColors"
            }
        }
     ),
    ("selHmCalMode",
        {
            "value": {
                "confPath": ("config", "mode")
            },
            "items": {
                "getter": "getHeatmapModes"
            }
        }
     ),
    ("selActivity",
        {
            "value": {
                "confPath": ("config", "stat")
            },
            "items": {
                "getter": "getActivityStats"
            }
        }
     ),
    ("cbHmMain",
        {
            "value": {
                "confPath": ("prefs", "display", 0)
            }
        }
     ),
    ("cbHmDeck",
        {
            "value": {
                "confPath": ("prefs", "display", 1)
            }
        }
     ),
    ("cbHmStats",
        {
            "value": {
                "confPath": ("prefs", "display", 2)
            }
        }
     ),
    ("cbStreakAll",
        {
            "value": {
                "confPath": ("prefs", "statsvis")
            }
        }
     ),
    ("spinLimHist",
        {
            "value": {
                "confPath": ("config", "limhist")
            }
        }
     ),
    ("spinLimFcst",
        {
            "value": {
                "confPath": ("config", "limfcst")
            }
        }
     ),
    ("dateLimData",
        {
            "value": {
                "confPath": ("config", "limdate")
            },
            "min": {
                "getter": "getColCreationTime"
            },
            "max": {
                "getter": "getCurrentTime"
            }
        }
     ),
    ("cbLimDel",
        {
            "value": {
                "confPath": ("config", "limcdel")
            }
        }
     ),
    ("keyGrabToggle",
        {
            "value": {
                "confPath": ("prefs", "hotkeys", "toggle")
            }
        },
     ),
    ("listDecks",
        {
            "value": {
                "confPath": ("config", "limdecks"),
                "getter": "getIgnoredDecks",
                "setter": "setIgnoredDecks"
            }
        }
     ),
))


class RevHmOptions(OptionsDialog):

    """
    Add-on-specific options dialog implementation
    """

    def __init__(self, conf, defaults, mw):
        self.mw = mw
        super(RevHmOptions, self).__init__(option_qtform, option_widgets,
                                           conf, defaults, parent=mw)

    # Events:

    def setupEvents(self):
        super(RevHmOptions, self).setupEvents()
        self.form.btnDeckAdd.clicked.connect(self.onAddIgnoredDeck)
        self.form.btnDeckDel.clicked.connect(self.onDeleteIgnoredDeck)
    
    # Actions:

    def onAddIgnoredDeck(self):
        list_widget = self.form.listDecks
        ret = StudyDeck(self.mw, accept=_("Choose"),
                        title=_("Choose Deck"), help="",
                        parent=self, geomKey="selectDeck")
        deck_name = ret.name
        deck_id = self.mw.col.decks.id(deck_name)
        
        item_tuple = (deck_name, deck_id)

        if not self.setCurrent(list_widget, item_tuple):
            self.setValuesAndCurrent(list_widget, [item_tuple], item_tuple)

    def onDeleteIgnoredDeck(self):
        list_widget = self.form.listDecks
        selected = self.getSelected(list_widget)
        self.removeValues(list_widget, selected)

    # Config Getters/Setters:

    def getColCreationTime(self):
        return self.mw.col.crt
    
    def getCurrentTime(self):
        return round(time.time())

    def getComboItems(self, dct):
        return list((val["label"], key) for key, val in dct.items())

    def getHeatmapColors(self):
        return self.getComboItems(heatmap_colors)

    def getHeatmapModes(self):
        return self.getComboItems(heatmap_modes)

    def getActivityStats(self):
        return self.getComboItems(activity_stats)

    def getIgnoredDecks(self, dids):
        item_tuples = []
        for did in dids:
            name = self.mw.col.decks.nameOrNone(did)
            if not name:
                continue
            item_tuples.append((name, did))
        return item_tuples
            
    def setIgnoredDecks(self, list_items):
        return list(list_items.keys())


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
