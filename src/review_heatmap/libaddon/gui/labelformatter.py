# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import *

from ..consts import ADDON_NAME, ADDON_VERSION

format_dict = {
    "ADDON_NAME": ADDON_NAME,
    "ADDON_VERSION": ADDON_VERSION,
}


def formatLabels(dialog):
    for widget in dialog.findChildren((QLabel, QPushButton), QRegExp("^fmt.*"),
                                      Qt.FindChildrenRecursively):
        
        widget.setText(widget.text().format(**format_dict))
