# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Contributions diaog

Uses the following addon-level constants, if defined:

ADDON_NAME, MAIL_AUTHOR, LINKS
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
