# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .widgets.qt import *
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
