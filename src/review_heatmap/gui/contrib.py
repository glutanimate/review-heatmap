# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Contributions dialog

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from ..libaddon.gui.dialog_contrib import ContribDialog

from .forms import contrib as qtform_contrib

__all__ = ["RevHmContrib", "invokeContributionsDialog"]

class RevHmContrib(ContribDialog):

    """
    Add-on-specific contrib dialog implementation
    """

    def __init__(self, parent):
        super(RevHmContrib, self).__init__(qtform_contrib, parent=parent)


def invokeContributionsDialog(parent):
    dialog = RevHmContrib(parent)
    dialog.exec_()
