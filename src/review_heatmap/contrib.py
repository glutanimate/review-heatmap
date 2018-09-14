# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Contributions dialog

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""
from __future__ import unicode_literals

from aqt import mw

from .libaddon.gui.contrib import ContribDialog
from .libaddon.utils.platform import ANKI21

if ANKI21:
    from .forms5 import contrib as qtform_contrib  # noqa: F401
else:
    from .forms4 import contrib as qtform_contrib  # noqa: F401


class RevHmContrib(ContribDialog):

    """
    Add-on-specific contrib dialog implementation
    """

    def __init__(self, parent):
        super(RevHmContrib, self).__init__(qtform_contrib, parent=parent)


def invokeContributionsDialog():
    dialog = RevHmContrib(mw)
    dialog.exec_()
