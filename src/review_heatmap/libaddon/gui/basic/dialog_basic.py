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
Basic QDialog, extended with some quality-of-life improvements
"""

from aqt.qt import *
from .interface import CommonWidgetInterface

__all__ = ["BasicDialog"]


class BasicDialog(QDialog):

    def __init__(self, form_module=None, parent=None, **kwargs):
        super(BasicDialog, self).__init__(parent=parent, **kwargs)
        self.parent = parent
        self.interface = CommonWidgetInterface(self)
        # Set up UI from pre-generated UI form:
        if form_module:
            self.form = form_module.Ui_Dialog()
            self.form.setupUi(self)
        self._setupUI()
        self._setupEvents()
        self._setupShortcuts()

    # WIDGET SET-UP

    def _setupUI(self):
        """
        Set up any type of subsequent UI modifications
        (e.g. adding custom widgets on top of form)
        """
        pass

    def _setupEvents(self):
        """Set up any type of event bindings"""
        pass

    def _setupShortcuts(self):
        """Set up any type of keyboard shortcuts"""
        pass

    # DIALOG OPEN/CLOSE

    def _onClose(self):
        """Executed whenever dialog closed"""
        pass

    def _onAccept(self):
        """Executed only if dialog confirmed"""
        pass

    def _onReject(self):
        """Executed only if dialog dismissed"""
        pass

    def accept(self):
        """Overwrites default accept() to control close actions"""
        self._onClose()
        self._onAccept()
        super(BasicDialog, self).accept()

    def reject(self):
        """Overwrites default reject() to control close actions"""
        self._onClose()
        self._onReject()
        super(BasicDialog, self).reject()
