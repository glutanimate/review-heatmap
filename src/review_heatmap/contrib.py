# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Contribution dialog

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from aqt.qt import *
from aqt.utils import openLink

from .consts import (ANKI21, LINK_PATREON, LINK_COFFEE, ADDON_NAME, MAIL_AUTHOR)

if ANKI21:
    from .forms5 import contrib
else:
    from .forms4 import contrib

mail_string = "mailto:{}".format(MAIL_AUTHOR)
format_dict = {"addon": ADDON_NAME}

class ContribDialog(QDialog):
    """Main Options dialog"""

    def __init__(self, parent):
        super(ContribDialog, self).__init__(parent=parent)
        # Set up UI from pre-generated UI form:
        self.form = contrib.Ui_Dialog()
        self.form.setupUi(self)
        # Perform any subsequent setup steps:
        self.setupLabels()
        self.setupEvents()

    def setupLabels(self):
        """
        Insert add-on name into dialog
        """
        for label in ("labContrib", "labHeader", "labFooter"):
            widget = getattr(self.form, label, None)
            if not widget:
                continue
            widget.setText(widget.text().format(**format_dict))

    def setupEvents(self):
        """
        Connect button click events
        """
        self.form.btnCoffee.clicked.connect(lambda: openLink(LINK_COFFEE))
        self.form.btnPatreon.clicked.connect(lambda: openLink(LINK_PATREON))
        self.form.btnMail.clicked.connect(lambda: openLink(mail_string))


def invokeContribDialog(parent):
    dialog = ContribDialog(parent)
    dialog.exec_()
