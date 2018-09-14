# -*- coding: utf-8 -*-

"""
Reusable add-on agnostic contributions dialog module

Depends on presence of the following parent-level modules:
    
    consts

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from aqt.qt import *
from aqt.utils import openLink

from ..consts import (ADDON_NAME, LINKS, MAIL_AUTHOR)


class ContribDialog(QDialog):
    """
    Add-on agnostic dialog that presents user with a number
    of options to support the development of the add-on.
    """

    def __init__(self, form, parent=None):
        """
        Initialize contrib dialog with provided form

        Arguments:
            form {PyQt form module} -- PyQt dialog form outlining the UI

        Keyword Arguments:
            parent {QWidget} -- Parent Qt widget (default: {None})
        """

        super(ContribDialog, self).__init__(parent=parent)
        # Set up UI from pre-generated UI form:
        self.form = form.Ui_Dialog()
        self.form.setupUi(self)
        # Perform any subsequent setup steps:
        self.setupLabels()
        self.setupEvents()

    def setupLabels(self):
        """
        Format dialog labels with add-on specific information
        """
        format_dict = {"addon": ADDON_NAME}

        for widget in self.children():
            if isinstance(widget, QLabel):
                widget.setText(widget.text().format(**format_dict))

    def setupEvents(self):
        """
        Connect button presses to actions
        """
        mail_string = "mailto:{}".format(MAIL_AUTHOR)
        self.form.btnMail.clicked.connect(
            lambda: openLink(mail_string))
        self.form.btnCoffee.clicked.connect(
            lambda: openLink(LINKS["coffee"]))
        self.form.btnPatreon.clicked.connect(
            lambda: openLink(LINKS["patreon"]))
