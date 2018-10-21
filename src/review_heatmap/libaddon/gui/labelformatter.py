# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import *

from ..consts import ADDON_NAME, ADDON_VERSION
from ..platform import ANKI21

format_dict = {
    "ADDON_NAME": ADDON_NAME,
    "ADDON_VERSION": ADDON_VERSION,
}

if ANKI21:
    fmt_find_params = ((QLabel, QPushButton), QRegExp("^fmt.*"),
                       Qt.FindChildrenRecursively)
else:
    # Qt4: recursive by default. No third param.
    fmt_find_params = ((QLabel, QPushButton), QRegExp("^fmt.*"))

def formatLabels(dialog):
    for widget in dialog.findChildren(*fmt_find_params):
        widget.setText(widget.text().format(**format_dict))
