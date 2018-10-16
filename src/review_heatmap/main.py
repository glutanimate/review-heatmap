# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Main Module, hooks add-on methods into Anki.

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import *
from aqt import mw

from .gui.options import invokeOptionsDialog

from .links import initializeLinks
from .views import initializeViews

def toggle_heatmap():
    """Toggle heatmap display on demand"""
    prefs = mw.pm.profile['heatmap']
    if mw.state == "deckBrowser":
        prefs['display'][0] = not prefs['display'][0]
        mw.deckBrowser.refresh()
    elif mw.state == "overview":
        prefs['display'][1] = not prefs['display'][1]
        mw.overview.refresh()

### Hooks and wraps ###

# Set up menus and hooks
options_action = QAction("Review &Heatmap Options...", mw)
options_action.triggered.connect(invokeOptionsDialog)
mw.form.menuTools.addAction(options_action)

toggle_action = QAction(mw, triggered=toggle_heatmap)
toggle_action.setShortcut(QKeySequence(_("Ctrl+R")))
mw.addAction(toggle_action)


initializeViews()
initializeLinks()
