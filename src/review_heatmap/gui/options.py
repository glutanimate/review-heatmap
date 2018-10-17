# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Options dialog and associated code

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import time

from aqt import mw

from aqt.qt import *
from aqt.studydeck import StudyDeck

from ..libaddon.gui.dialog_options import OptionsDialog
from ..libaddon.packaging import platformAwareImport

from ..config import config, heatmap_colors, heatmap_modes

qtform_options = platformAwareImport(".forms", "options", __name__)

__all__ = ["RevHmOptions", "invokeOptionsDialog"]

class RevHmOptions(OptionsDialog):

    """
    Add-on-specific options dialog implementation
    """

    _mapped_widgets = (
        ("form.selHmColor", (
            # order is important (e.g. to set-up items before current item)
            ("items", {
                "setter": "_setSelHmColorItems"
            }),
            ("value", {
                "dataPath": "synced/colors",
            }),
        )),
        ("form.selHmCalMode", (
            ("items", {
                "setter": "_setSelHmCalModeItems"
            }),
            ("value", {
                "dataPath": "synced/mode"
            }),
        )),
        ("form.cbHmMain", (
            ("value", {
                "dataPath": "profile/display/deckbrowser"
            }),
        )),
        ("form.cbHmDeck", (
            ("value", {
                "dataPath": "profile/display/overview"
            }),
        )),
        ("form.cbHmStats", (
            ("value", {
                "dataPath": "profile/display/stats"
            }),
        )),
        ("form.cbStreakAll", (
            ("value", {
                "dataPath": "profile/statsvis"
            }),
        )),
        ("form.spinLimHist", (
            ("value", {
                "dataPath": "synced/limhist"
            }),
        )),
        ("form.spinLimFcst", (
            ("value", {
                "dataPath": "synced/limfcst"
            }),
        )),
        ("form.dateLimData", (
            ("value", {
                "dataPath": "synced/limdate"
            }),
            ("min", {
                "setter": "_setDateLimDataMin"
            }),
            ("max", {
                "setter": "_setDateLimDataMax"
            }),
        )),
        ("form.cbLimDel", (
            ("value", {
                "dataPath": "synced/limcdel"
            }),
        )),
        ("form.keyGrabToggle", (
            ("value", {
                "dataPath": "profile/hotkeys/toggle"
            }),
        )),
        ("form.listDecks", (
            ("value", {
                "dataPath": "synced/limdecks",
                "setter": "_setListDecksValue",
            }),
        )),
    )

    def __init__(self, config, mw, parent=None, **kwargs):
        # Mediator methods defined in mapped_widgets might need access to
        # certain instance attributes. As super().__init__ calls these
        # mediator methods it is important that we set the attributes
        # beforehand:
        self.parent = parent or mw
        self.mw = mw
        super(RevHmOptions, self).__init__(self._mapped_widgets, config,
                                           form_module=qtform_options,
                                           parent=self.parent, **kwargs)
        # Instance methods that modify the initialized UI should either be
        # called from self._setupUI or from here

    # UI adjustments

    def _setupUI(self):
        super(RevHmOptions, self)._setupUI()

    # Events:

    def _setupEvents(self):
        super(RevHmOptions, self)._setupEvents()
        self.form.btnDeckAdd.clicked.connect(self._onAddIgnoredDeck)
        self.form.btnDeckDel.clicked.connect(self._onDeleteIgnoredDeck)

    # Actions:

    # Deck list buttons
    # TODO: Migrate to custom widget

    def _onAddIgnoredDeck(self):
        list_widget = self.form.listDecks
        ret = StudyDeck(self.mw, accept=_("Choose"),
                        title=_("Choose Deck"), help="",
                        parent=self, geomKey="selectDeck")
        deck_name = ret.name
        if not deck_name:
            return False
        deck_id = self.mw.col.decks.id(deck_name)

        item_tuple = (deck_name, deck_id)

        if not self.interface.setCurrentByData(list_widget, deck_id):
            self.interface.addValueAndMakeCurrent(list_widget, item_tuple)

    def _onDeleteIgnoredDeck(self):
        list_widget = self.form.listDecks
        self.interface.removeSelected(list_widget)

    # Helpers:

    def _getComboItems(self, dct):
        return list((val["label"], key) for key, val in dct.items())

    # Config setters:

    def _setDateLimDataMin(self, data_val):
        return self.mw.col.crt

    def _setDateLimDataMax(self, data_val):
        return int(round(time.time()))

    def _setSelHmColorItems(self, data_val):
        return self._getComboItems(heatmap_colors)

    def _setSelHmCalModeItems(self, data_val):
        return self._getComboItems(heatmap_modes)

    def _setListDecksValue(self, dids):
        item_tuples = []
        for did in dids:
            name = self.mw.col.decks.nameOrNone(did)
            if not name:
                continue
            item_tuples.append((name, did))
        return item_tuples


def invokeOptionsDialog(parent=None):
    """Call settings dialog"""
    dialog = RevHmOptions(config, mw, parent=parent)
    return dialog.exec_()

def initializeOptions():
    config.setConfigAction(invokeOptionsDialog)
    # Set up menu entry:
    options_action = QAction("Review &Heatmap Options...", mw)
    options_action.triggered.connect(lambda _: invokeOptionsDialog())
    mw.form.menuTools.addAction(options_action)
