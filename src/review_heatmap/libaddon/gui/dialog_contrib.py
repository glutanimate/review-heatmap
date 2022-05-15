# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
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
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Contributions diaog

Uses the following addon-level constants, if defined:

ADDON.NAME, ADDON.AUTHOR_MAIL, ADDON.LINKS
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.utils import openLink

from ..consts import ADDON

from .basic.dialog_basic import BasicDialog
from .labelformatter import formatLabels

from .dialog_htmlview import HTMLViewer
from .about import getAboutString


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
            QPushButton: btnPatreon, btnCredits

        Keyword Arguments:
            parent {QWidget} -- Parent Qt widget (default: {None})
        """

        super(ContribDialog, self).__init__(form_module=form_module,
                                            parent=parent)

    def _setupUI(self):
        formatLabels(self, self._linkHandler)

    def _setupEvents(self):
        """
        Connect button presses to actions
        """
        self.form.btnPatreon.clicked.connect(
            lambda: openLink(ADDON.LINKS["patreon"]))
        self.form.btnCredits.clicked.connect(
            self._showCredits)

    def _showCredits(self):
        viewer = HTMLViewer(getAboutString(title=True),
                            title=ADDON.NAME, parent=self)
        viewer.exec()

    def _linkHandler(self, url):
        """Support for binding custom actions to text links"""
        if not url.startswith("action://"):
            return openLink(url)
        protocol, cmd = url.split("://")
        if cmd == "installed-addons":
            openLink("https://ankiweb.net/shared/byauthor/1771074083")
