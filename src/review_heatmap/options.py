# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Options dialog and associated code

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from functools import reduce

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, openLink

from .about import get_about_string
from ._version import __version__
from .consts import (ANKI21, LINK_PATREON, LINK_COFFEE, ADDON_NAME,
                     LINK_RATE, LINK_TWITTER, LINK_YOUTUBE, LINK_HELP)
from .config import heatmap_colors, heatmap_modes, activity_stats

if ANKI21:
    from .forms5 import settings
else:
    from .forms4 import settings


# Widget data getter functions

def getColCreationTime():
    try:
        return mw.col.crt
    except AttributeError:
        return None

# Widget <-> config assignments

comboboxes = {
    "selHmColor": {"confPath": ("config", "colors"), "presets": heatmap_colors},
    "selHmCalMode": {"confPath": ("config", "mode"), "presets": heatmap_modes},
    "selActivity": {"confPath": ("config", "stat"), "presets": activity_stats}
}

checkboxes = {
    "cbHmMain": {"confPath": ("prefs", "display", 0)},
    "cbHmDeck": {"confPath": ("prefs", "display", 1)},
    "cbHmStats": {"confPath": ("prefs", "display", 2)},
    "cbStreakAll": {"confPath": ("prefs", "statsvis")}
}

spinboxes = {
    "spinLimHist": {"confPath": ("config", "limhist")},
    "spinLimFcst": {"confPath": ("config", "limfcst")}
}

keygrabbers = {
    "btnKeyToggle": {"confPath": ("prefs", "hotkeys", "toggle")}
}

dateedits = {
    "dateLimData": {"confPath": ("config", "limdate"),
                    "minDate": getColCreationTime}
}

# Utility functions for operating with nested collections

def getNestedValue(obj, keys):
    """
    Get value out of nested collection by supplying tuple of 
    nested keys/indices
    """
    cur = obj
    for nr, key in enumerate(keys):
        cur = cur[key]
    return cur

def setNestedValue(obj, keys, value):
    """
    Set value in nested collection by supplying tuple of
    nested keys / indices, and value to set
    """
    depth = len(keys) - 1
    cur = obj
    for nr, key in enumerate(keys):
        if nr == depth:
            cur[key] = value
            return
        cur = cur[key]

# Options dialog and associated classes

class OptionsDialog(QDialog):
    """Main options dialog"""

    def __init__(self, parent, conf):
        super(OptionsDialog, self).__init__(parent=parent)
        self.conf = conf
        # Set up UI from pre-generated UI form:
        self.form = settings.Ui_Dialog()
        self.form.setupUi(self)
        # Perform any subsequent setup steps:
        self.setupLabels()
        self.setupEvents()
        self.setupValues()

    def updateHotkey(self, btn, hotkey):
        """Update hotkey label and attribute"""
        btn.setText(hotkey)

    def grabKeyFor(self, btn):
        """Invoke key grabber"""
        win = GrabKey(self, lambda key: self.updateHotkey(btn, key))
        win.exec_()

    def setupValues(self):
        """Set up widget data based on provided config dict"""
        conf = self.conf

        for object_name, object_data in comboboxes.items():
            combobox = getattr(self.form, object_name)
            presets = object_data["presets"]
            combobox.addItems(list(val["label"] for val in presets.values()))
            current = getNestedValue(conf, object_data["confPath"])
            current_index = list(presets.keys()).index(current)
            combobox.setCurrentIndex(current_index)

        for object_name, object_data in checkboxes.items():
            checkbox = getattr(self.form, object_name)
            current = getNestedValue(conf, object_data["confPath"])
            checkbox.setChecked(current)

        for object_name, object_data in spinboxes.items():
            spinbox = getattr(self.form, object_name)
            current = getNestedValue(conf, object_data["confPath"])
            spinbox.setValue(current)

        for object_name, object_data in dateedits.items():
            dateedit = getattr(self.form, object_name)

            mindate = object_data["minDate"]
            if callable(mindate):  # can only get mw.col.crt at runtime
                mindate = mindate()
            minDateTime = QDateTime()
            minDateTime.setTime_t(mindate)

            current = getNestedValue(conf, object_data["confPath"])
            if current:
                curDateTime = QDateTime()
                curDateTime.setTime_t(current)
            else:
                curDateTime = minDateTime

            dateedit.setMinimumDateTime(minDateTime)
            dateedit.setDateTime(curDateTime)

        for object_name, object_data in keygrabbers.items():
            keygrabber = getattr(self.form, object_name)
            hotkey = getNestedValue(conf, object_data["confPath"])
            self.updateHotkey(keygrabber, hotkey)
            keygrabber.clicked.connect(lambda: self.grabKeyFor(keygrabber))

    def getValues(self):
        conf = self.conf
        for object_name, object_data in comboboxes.items():
            combobox = getattr(self.form, object_name)
            presets = object_data["presets"]
            current_index = combobox.currentIndex()
            current = list(presets.items())[current_index][0]
            setNestedValue(conf, object_data["confPath"], current)

        for object_name, object_data in checkboxes.items():
            checkbox = getattr(self.form, object_name)
            current = checkbox.isChecked()
            setNestedValue(conf, object_data["confPath"], current)

        for object_name, object_data in spinboxes.items():
            spinbox = getattr(self.form, object_name)
            current = spinbox.value()
            setNestedValue(conf, object_data["confPath"], current)

        for object_name, object_data in dateedits.items():
            dateedit = getattr(self.form, object_name)
            curDateTime = dateedit.dateTime()
            current = curDateTime.toSecsSinceEpoch()
            setNestedValue(conf, object_data["confPath"], current)

        for object_name, object_data in keygrabbers.items():
            keygrabber = getattr(self.form, object_name)
            current = keygrabber.text()
            setNestedValue(conf, object_data["confPath"], current)

    def setupLabels(self):
        info_string = "{} v{}".format(ADDON_NAME, __version__)
        about_string = get_about_string()
        self.form.labInfo.setText(info_string)
        self.form.labAbout.setText(about_string)

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Enter or evt.key() == Qt.Key_Return:
            evt.accept()
            return
        super(OptionsDialog, self).keyPressEvent(evt)

    def setupEvents(self):
        self.form.btnCoffee.clicked.connect(lambda: openLink(LINK_COFFEE))
        self.form.btnPatreon.clicked.connect(lambda: openLink(LINK_PATREON))
        self.form.btnRate.clicked.connect(lambda: openLink(LINK_RATE))
        self.form.btnTwitter.clicked.connect(lambda: openLink(LINK_TWITTER))
        self.form.btnYoutube.clicked.connect(lambda: openLink(LINK_YOUTUBE))
        self.form.btnHelp.clicked.connect(lambda: openLink(LINK_HELP))

    def restore(self):
        """Restore colors and fields back to defaults"""
        self.setup_values(default_conf, default_prefs)

    def accept(self):
        """Apply changes on OK button press"""
        self.getValues()
        mw.col.setMod()
        mw.reset()
        super(OptionsDialog, self).accept()

    def reject(self):
        """Dismiss changes on Close button press"""
        super(OptionsDialog, self).reject()


class GrabKey(QDialog):
    """
    Simple key combination grabber for hotkey assignments

    Largely based on ImageResizer by searene
    (https://github.com/searene/Anki-Addons)
    """

    def __init__(self, parent, callback):
        QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.callback = callback
        # self.active is used to trace whether there's any key held now
        self.active = 0
        self.meta = self.ctrl = self.alt = self.shift = False
        self.extra = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        label = QLabel('Please press the new key combination')
        mainLayout.addWidget(label)

        self.setWindowTitle('Grab key combination')

    def keyPressEvent(self, evt):
        self.active += 1
        if evt.key() > 0 and evt.key() < 127:
            self.extra = chr(evt.key())
        elif evt.key() == Qt.Key_Control:
            self.ctrl = True
        elif evt.key() == Qt.Key_Alt:
            self.alt = True
        elif evt.key() == Qt.Key_Shift:
            self.shift = True
        elif evt.key() == Qt.Key_Meta:
            self.meta = True

    def keyReleaseEvent(self, evt):
        self.active -= 1

        if self.active != 0:
            return
        if not (self.shift or self.ctrl or self.alt or self.meta):
            showInfo("Please use at least one keyboard "
                     "modifier (Win, Ctrl, Alt, Shift)")
            return
        if (self.shift and not (self.ctrl or self.alt or self.meta)):
            showInfo("Shift needs to be combined with at "
                     "least one other modifier (Ctrl, Alt)")
            return
        if not self.extra:
            showInfo("Please press at least one key "
                     "that is not a keyboard modifier (not Win/Ctrl/Alt/Shift)")
            return

        combo = []
        if self.meta:
            combo.append("Meta")
        if self.ctrl:
            combo.append("Ctrl")
        if self.shift:
            combo.append("Shift")
        if self.alt:
            combo.append("Alt")
        combo.append(self.extra)

        key_string = "+".join(combo)
        # Show key string according to platform-specific key designations:
        # keySeq = QKeySequence(key_string)
        # key_string = keySeq.toString(format=QKeySequence.NativeText)

        self.callback(key_string)

        self.close()


def invokeOptionsDialog(mw):
    """Call settings dialog"""
    conf = {"config": mw.col.conf['heatmap'],
            "prefs": mw.pm.profile['heatmap']}
    dialog = OptionsDialog(mw, conf)
    dialog.exec_()
