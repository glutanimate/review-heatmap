# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from .widgets.qt import *
from .interface import CommonWidgetInterface

__all__ = ["BasicDialog"]

class BasicDialog(QDialog):
    def __init__(self, form=None, parent=None, **kwargs):
        super(BasicDialog, self).__init__(parent=parent, **kwargs)
        self.parent = parent
        # Set up UI from pre-generated UI form:
        self.interface = CommonWidgetInterface(self)
        if form:
            self.form = form.Ui_Dialog()
            self.form.setupUi(self)

    # DIALOG OPEN/CLOSE

    def onClose(self):
        """Executed whenever dialog closed"""
        pass

    def onAccept(self):
        """Executed only if dialog confirmed"""
        pass

    def onReject(self):
        """Executed only if dialog dismissed"""
        pass

    def accept(self):
        """Overwrites default accept() to control close actions"""
        self.onClose()
        self.onAccept()
        super(BasicDialog, self).accept()

    def reject(self):
        """Overwrites default reject() to control close actions"""
        self.onClose()
        self.onReject()
        super(BasicDialog, self).reject()
