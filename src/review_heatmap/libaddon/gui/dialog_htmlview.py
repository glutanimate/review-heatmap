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
Simple dialog for viewing HTML
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import *

from ..platform import PLATFORM

from .basic.dialog_basic import BasicDialog


class HTMLViewer(BasicDialog):

    def __init__(self, html, title=None, parent=None):
        super(HTMLViewer, self).__init__(parent=parent)
        if PLATFORM == "win":
            self.setMinimumWidth(400)
            self.setMinimumHeight(500)
        else:
            self.setMinimumWidth(500)
            self.setMinimumHeight(600)
        if title:
            self.setWindowTitle(title)
        self.setHtml(html)

    def _setupUI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(True)
        layout.addWidget(self._browser)
        
    def setHtml(self, html):
        self._browser.setHtml(html)
