#-*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: Glutanimate 2016-2017
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

### Add-on configuration ###

from aqt.qt import *
from aqt import mw

heatmap_colors = {
    "olive":    ("#dae289", "#bbd179", "#9cc069", "#8ab45d", "#78a851",
                "#669d45", "#648b3f", "#637939", "#4f6e30", "#3b6427"),
    "lime":     ("#d6e685", "#bddb7a", "#a4d06f", "#8cc665", "#74ba58",
                "#5cae4c", "#44a340", "#378f36", "#2a7b2c", "#1e6823"),
    "ice":      ("#a8d5f6", "#95c8f3", "#82bbf0", "#70afee", "#5da2eb",
                "#4a95e8", "#3889e6", "#257ce3", "#126fe0", "#0063de"),
    "magenta":  ("#fde0dd", "#fcc5c0", "#fa9fb5", "#f768a1", "#ea4e9c",
                "#dd3497", "#ae017e", "#7a0177", "#610070",  "#49006a"),
    "flame":    ("#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc6d33",
                "#fc4e2a", "#e31a1c", "#d00d21", "#bd0026", "#800026")
}

heatmap_modes = {
    "year": {"domain": 'year', "subDomain": 'day', "range": 1},
    "months": {"domain": 'month', "subDomain": 'day', "range": 12}
}

# use synced conf for settings that are device-agnostic
default_conf = {
    "colors": "lime",
    "mode": "year",
    "limhist": 365,
    "limfcst": 90,
    "version": 0.3
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
        if not 'heatmap' in conf:
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
        QDialog.__init__(self, parent=mw)
        self.setup_ui()
        self.setup_values(mw.col.conf["heatmap"], mw.pm.profile['heatmap'])

    def setup_values(self, config, prefs):
        """Set up widget data based on provided config dict"""
        colsel = heatmap_colors.keys()
        idx = colsel.index(config["colors"])
        self.col_sel.setCurrentIndex(idx)
        modesel = heatmap_modes.keys()
        idx = modesel.index(config["mode"])
        self.mode_sel.setCurrentIndex(idx)
        self.hist_sel.setValue(config["limhist"])
        self.fcst_sel.setValue(config["limfcst"])
        self.db_cb.setChecked(prefs["display"][0])
        self.ov_cb.setChecked(prefs["display"][1])
        self.st_cb.setChecked(prefs["display"][2])
        self.streak_cb.setChecked(prefs["statsvis"])

    def setup_ui(self):
        """Set up widgets and layouts"""
        col_l = QLabel("Color Scheme")
        mode_l = QLabel("Calendar Mode")
        hist_l = QLabel("History Limit")
        fcst_l = QLabel("Forecast Limit")
        show_l = QLabel("Display heatmap on the following screens:")
        rule1 = self.create_horizontal_rule()
        rule2 = self.create_horizontal_rule()
        rule3 = self.create_horizontal_rule()

        self.col_sel = QComboBox()
        self.col_sel.addItems(heatmap_colors.keys())
        self.mode_sel = QComboBox()
        self.mode_sel.addItems(heatmap_modes.keys())
        self.hist_sel = QSpinBox()
        self.fcst_sel = QSpinBox()
        self.db_cb = QCheckBox("Main screen")
        self.ov_cb = QCheckBox("Deck screen")
        self.st_cb = QCheckBox("Stats screen")
        self.streak_cb = QCheckBox("Show streak stats even if heatmap disabled")
        sel_tt = "Only applies to main screen and deck overview"
        for sel in (self.hist_sel, self.fcst_sel):
            sel.setToolTip(sel_tt)
            sel.setRange(0, 1000000)
            sel.setSuffix(" days")
            sel.setSpecialValueText("No limit")

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(col_l, 1, 0, 1, 1)
        grid.addWidget(self.col_sel, 1, 1, 1, 2)
        grid.addWidget(mode_l, 2, 0, 1, 1)
        grid.addWidget(self.mode_sel, 2, 1, 1, 2)
        grid.addWidget(rule1, 3, 0, 1, 3)
        grid.addWidget(hist_l, 4, 0, 1, 1)
        grid.addWidget(self.hist_sel, 4, 1, 1, 2)
        grid.addWidget(fcst_l, 5, 0, 1, 1)
        grid.addWidget(self.fcst_sel, 5, 1, 1, 2)
        grid.addWidget(rule2, 6, 0, 1, 3)
        grid.addWidget(show_l, 7, 0, 1, 3)
        grid.addWidget(self.db_cb)
        grid.addWidget(self.ov_cb)
        grid.addWidget(self.st_cb)
        grid.addWidget(rule3, 9, 0, 1, 3)
        grid.addWidget(self.streak_cb, 10, 0, 1, 3)


        # Main button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok
                        | QDialogButtonBox.Cancel)
        defaults_btn = button_box.addButton("Defaults",
           QDialogButtonBox.ResetRole)
        defaults_btn.clicked.connect(self.restore)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.on_reject)

        # Main layout
        l_main = QVBoxLayout()
        l_main.addLayout(grid)
        l_main.addWidget(button_box)
        self.setLayout(l_main)
        self.setMinimumWidth(360)
        self.setWindowTitle('Review Heatmap Options')

    def create_horizontal_rule(self):
        """Returns a QFrame that is a sunken, horizontal rule."""
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame

    def restore(self):
        """Restore colors and fields back to defaults"""
        self.setup_values(default_conf, default_prefs)

    def on_accept(self):
        """Apply changes on OK button press"""
        config = mw.col.conf['heatmap']
        prefs = mw.pm.profile['heatmap']
        config['colors'] = self.col_sel.currentText()
        config['mode'] = self.mode_sel.currentText()
        config['limhist'] = self.hist_sel.value()
        config['limfcst'] = self.fcst_sel.value()
        prefs['display'] = [i.isChecked() for i in (self.db_cb, self.ov_cb, self.st_cb)]
        prefs['statsvis'] = self.streak_cb.isChecked()
        mw.col.setMod()
        mw.reset()
        self.close()

    def on_reject(self):
        """Dismiss changes on Close button press"""
        self.close()

def on_heatmap_settings(mw):
    """Call settings dialog"""
    dialog = HeatmapOpts(mw)
    dialog.exec_()