# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Contributions dialog

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import QApplication

from ..libaddon.gui.dialog_contrib import ContribDialog
from ..libaddon.platform import PLATFORM

from .forms import contrib as qtform_contrib

__all__ = ["RevHmContrib", "invokeContributionsDialog"]

class RevHmContrib(ContribDialog):

    """
    Add-on-specific contrib dialog implementation
    """

    def __init__(self, parent):
        super(RevHmContrib, self).__init__(qtform_contrib, parent=parent)

    def _setupUI(self):
        super(RevHmContrib, self)._setupUI()

        # manually adjust title label font sizes on Windows
        # gap between default windows font sizes and sizes that work well
        # on Linux and macOS is simply too big
        # TODO: find a better solution
        if PLATFORM == "win":
            default_size = QApplication.font().pointSize()
            for label in [self.form.fmtLabContrib]:
                font = label.font()
                font.setPointSize(int(default_size * 1.4))
                label.setFont(font)


def invokeContributionsDialog(parent):
    dialog = RevHmContrib(parent)
    dialog.exec_()
