# -*- coding: utf-8 -*-

"""
Reusable add-on agnostic contributions dialog module

Depends on presence of the following parent-level modules:
    
    consts

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.utils import openLink

from ..consts import MAIL_AUTHOR, LINKS

from .basic.dialog_basic import BasicDialog
from .labelformatter import formatLabels

from .dialog_htmlview import HTMLViewer
from .about import get_about_string
from ..consts import ADDON_NAME


class ContribDialog(BasicDialog):
    """
    Add-on agnostic dialog that presents user with a number
    of options to support the development of the add-on.
    """

    def __init__(self, form_module, parent=None):
        """
        Initialize contrib dialog with provided form

        Arguments:
            form_module {PyQt form module} -- PyQt dialog form outlining the UI

        Provided Qt form should contain the following widgets:
            QPushButton: btnMail, btnCoffee, btnPatreon, btnCredits

        Keyword Arguments:
            parent {QWidget} -- Parent Qt widget (default: {None})
        """

        super(ContribDialog, self).__init__(form_module=form_module,
                                            parent=parent)

    def _setupUI(self):
        formatLabels(self)

    def _setupEvents(self):
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
        self.form.btnCredits.clicked.connect(
            self.showCredits)

    def showCredits(self):
        viewer = HTMLViewer(get_about_string(title=True),
                            title=ADDON_NAME, parent=self)
        viewer.exec_()
