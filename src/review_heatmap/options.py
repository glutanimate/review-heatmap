# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Options dialog and associated code

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import time

from aqt.qt import *
from aqt import mw
from aqt.studydeck import StudyDeck

from .libaddon.gui.options import OptionsDialog
from .config import (config, heatmap_colors, heatmap_modes, activity_stats)
from .consts import ANKI21

if ANKI21:
    from .forms5 import options as option_qtform  # noqa: F401
else:
    from .forms4 import options as option_qtform  # noqa: F401


# Widget <-> config mappings

# order is important (e.g. set items before current value)
option_widgets = (
    ("form.selHmColor", (
        ("items", {
            "getter": "getHeatmapColors"
        }),
        ("value", {
            "confPath": ("synced", "colors"),
        }),
    )),
    ("form.selHmCalMode", (
        ("items", {
            "getter": "getHeatmapModes"
        }),
        ("value", {
            "confPath": ("synced", "mode")
        }),
    )),
    ("form.selActivity", (
        ("items", {
            "getter": "getActivityStats"
        }),
        ("value", {
            "confPath": ("synced", "stat")
        }),
    )),
    ("form.cbHmMain", (
        ("value", {
            "confPath": ("profile", "display", 0)
        }),
    )),
    ("form.cbHmDeck", (
        ("value", {
            "confPath": ("profile", "display", 1)
        }),
    )),
    ("form.cbHmStats", (
        ("value", {
            "confPath": ("profile", "display", 2)
        }),
    )),
    ("form.cbStreakAll", (
        ("value", {
            "confPath": ("profile", "statsvis")
        }),
    )),
    ("form.spinLimHist", (
        ("value", {
            "confPath": ("synced", "limhist")
        }),
    )),
    ("form.spinLimFcst", (
        ("value", {
            "confPath": ("synced", "limfcst")
        }),
    )),
    ("form.dateLimData", (
        ("value", {
            "confPath": ("synced", "limdate")
        }),
        ("min", {
            "getter": "getColCreationTime"
        }),
        ("max", {
            "getter": "getCurrentTime"
        }),
    )),
    ("form.cbLimDel", (
        ("value", {
            "confPath": ("synced", "limcdel")
        }),
    )),
    ("form.keyGrabToggle", (
        ("value", {
            "confPath": ("profile", "hotkeys", "toggle")
        }),
    )),
    ("form.listDecks", (
        ("value", {
            "confPath": ("synced", "limdecks"),
            "getter": "getIgnoredDecks",
        }),
    )),
)


class RevHmOptions(OptionsDialog):

    """
    Add-on-specific options dialog implementation
    """

    def __init__(self, config, mw):
        self.mw = mw
        super(RevHmOptions, self).__init__(option_qtform, option_widgets,
                                           config, parent=mw)
        self.adjustUI()

    # UI adjustments

    def adjustUI(self):
        self.form.activitiesBox.hide()

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

        if not self.interface.setCurrent(list_widget, item_tuple):
            self.interface.setValuesAndCurrent(
                list_widget, [item_tuple], item_tuple)

    def onDeleteIgnoredDeck(self):
        list_widget = self.form.listDecks
        selected = self.interface.getSelected(list_widget)
        self.interface.removeValues(list_widget, selected)

    # Config Getters/Setters:

    def getColCreationTime(self):
        return self.mw.col.crt

    def getCurrentTime(self):
        return int(round(time.time()))

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


def invokeOptionsDialog():
    """Call settings dialog"""
    dialog = RevHmOptions(config, mw)
    return dialog.exec_()

config.setConfigAction(invokeOptionsDialog)
