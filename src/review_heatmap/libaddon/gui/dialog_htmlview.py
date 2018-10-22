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

from aqt.qt import QVBoxLayout, QTextBrowser

from .basic.dialog_basic import BasicDialog


class HTMLViewer(BasicDialog):

    def __init__(self, html, title=None, parent=None):
        super(HTMLViewer, self).__init__(parent=parent)
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
