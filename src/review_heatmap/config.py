# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles the add-on configuration

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from collections import OrderedDict

from aqt.qt import *
from aqt import mw

from .about import get_about_string
from ._version import __version__
from .consts import anki21

if anki21:
    from .forms5 import settings
else:
    from .forms4 import settings

heatmap_colors = OrderedDict((
    ("olive", ("#dae289", "#bbd179", "#9cc069", "#8ab45d", "#78a851",
               "#669d45", "#648b3f", "#637939", "#4f6e30", "#3b6427")),
    ("lime", ("#d6e685", "#bddb7a", "#a4d06f", "#8cc665", "#74ba58",
              "#5cae4c", "#44a340", "#378f36", "#2a7b2c", "#1e6823")),
    ("ice", ("#a8d5f6", "#95c8f3", "#82bbf0", "#70afee", "#5da2eb",
             "#4a95e8", "#3889e6", "#257ce3", "#126fe0", "#0063de")),
    ("magenta", ("#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#ea4e9c",
                 "#dd3497", "#ae017e", "#7a0177", "#610070", "#49006a")),
    ("flame", ("#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc6d33",
               "#fc4e2a", "#e31a1c", "#d00d21", "#bd0026", "#800026"))
))

heatmap_modes = OrderedDict((
    ("year", {"domain": 'year', "subDomain": 'day', "range": 1}),
    ("months", {"domain": 'month', "subDomain": 'day', "range": 12})
))

activities = OrderedDict((
    ("a", {"label": "All reviews"}),
    ("n", {"label": "New card sightings"}),
    ("r", {"label": "Review card sightings"}),
    ("c", {"label": "Cards created"})
))

# use synced conf for settings that are device-agnostic
default_conf = {
    "colors": "lime",
    "mode": "year",
    "activity": "a",
    "limdate": None,
    "limhist": 365,
    "limfcst": 90,
    "limcdel": False,
    "limdecks": (),
    "version": 0.7
}

# use local prefs for settings that might be device-specific
default_prefs = {
    "display": [True, True, True],
    "statsvis": True,
    "version": 0.3
}


def load_config(ret=None):
    """Load and/or create add-on preferences"""
    configs = [
        (mw.col.conf, default_conf),
        (mw.pm.profile, default_prefs)
    ]
    for conf, default in configs:
        if 'heatmap' not in conf:
            # create initial configuration
            conf['heatmap'] = default
            mw.col.setMod()

        elif conf['heatmap']['version'] < default['version']:
            print("Updating synced config DB from earlier add-on release")
            for key in list(default.keys()):
                if key not in conf['heatmap']:
                    conf['heatmap'][key] = default[key]
            conf['heatmap']['version'] = default['version']
            # insert other update actions here:
            mw.col.setMod()

    if ret == "conf":
        return mw.col.conf['heatmap']
    if ret == "prefs":
        return mw.pm.profile['heatmap']
    return mw.col.conf['heatmap'], mw.pm.profile['heatmap']


class HeatmapOpts(QDialog):
    """Main Options dialog"""

    def __init__(self, mw):
        super(HeatmapOpts, self).__init__(parent=mw)
        # Set up UI from pre-generated UI form:
        self.form = settings.Ui_Dialog()
        self.form.setupUi(self)
        # Perform any subsequent setup steps:
        self.setupLabels()
        self.setupEvents()
        self.setupValues(mw.col.conf["heatmap"], mw.pm.profile['heatmap'])
        # restoreGeom(self, "revhmopts")

    def setupValues(self, config, prefs):
        """Set up widget data based on provided config dict"""
        for conf_key, dct, wname in (("colors", heatmap_colors, "selHmColor"),
                                     ("mode", heatmap_modes, "selHmCalMode"),
                                     ("activity", activities, "selActivity")):
            keys = list(dct.keys())
            cur_idx = keys.index(config[conf_key])
            combobox = getattr(self.form, wname)
            # Use long labels for default activity selection
            if conf_key == "activity":
                combobox.addItems(list(dct[key]["label"] for key in keys))
            else:
                combobox.addItems(keys)
            combobox.setCurrentIndex(cur_idx)

        for wname, state in zip(("cbHmMain", "cbHmDeck", "cbHmStats"),
                                prefs["display"]):
            checkbox = getattr(self.form, wname)
            checkbox.setChecked(state)

        self.form.cbStreakAll.setChecked(prefs["statsvis"])

        unix_start = config["limdate"] or mw.col.crt
        if unix_start:
            date = QDateTime()
            date.setTime_t(unix_start)
            self.form.dateLimData.setDateTime(date)

        self.form.spinLimHist.setValue(config["limhist"])
        self.form.spinLimFcst.setValue(config["limfcst"])

    def setupLabels(self):
        info_string = "Review Heatmap\nv{}".format(__version__)
        about_string = get_about_string()
        self.form.labInfo.setText(info_string)
        self.form.labAbout.setText(about_string)

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Enter or evt.key() == Qt.Key_Return:
            evt.accept()
            return
        QDialog(self).keyPressEvent(evt)

    def setupEvents(self):
        pass

    def restore(self):
        """Restore colors and fields back to defaults"""
        self.setup_values(default_conf, default_prefs)

    def accept(self):
        """Apply changes on OK button press"""
        # config = mw.col.conf['heatmap']
        # prefs = mw.pm.profile['heatmap']
        # config['colors'] = self.col_sel.currentText()
        # config['mode'] = self.mode_sel.currentText()
        # config['limhist'] = self.hist_sel.value()
        # config['limfcst'] = self.fcst_sel.value()
        # prefs['display'] = [i.isChecked()
        #                     for i in (self.db_cb, self.ov_cb, self.st_cb)]
        # prefs['statsvis'] = self.streak_cb.isChecked()
        # mw.col.setMod()
        # mw.reset()
        self.close()

    # def reject(self):
    #     """Dismiss changes on Close button press"""
    #     self.closeEvent()


def on_heatmap_settings(mw):
    """Call settings dialog"""
    dialog = HeatmapOpts(mw)
    dialog.exec_()
