# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .qt import QMessageBox

def showInfo(message, parent=None, mode="info", title="Anki"):
    if mode == "info":
        icon = QMessageBox.Information
    elif mode == "warning":
        icon = QMessageBox.Warning
    elif mode == "critical":
        icon = QMessageBox.Critical

    return QMessageBox(icon, title, message, parent=parent)
