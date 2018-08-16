
from .widgets.qt import *
from .interface import CommonWidgetInterface

class BasicDialog(QDialog, CommonWidgetInterface):
    def __init__(self, form=None, parent=None, **kwargs):
        super(BasicDialog, self).__init__(parent=parent, **kwargs)
        self.parent = parent
        # Set up UI from pre-generated UI form:
        if form:
            self.form = form.Ui_Dialog()
            self.form.setupUi(self)

    # HELPER

    def nameToWidget(self, name):
        return getattr(self, name, None) or getattr(self.form, name, None)

    # DIALOG OPEN/CLOSE

    def onClose(self):
        pass

    def onAccept(self):
        pass

    def onReject(self):
        pass

    def accept(self):
        """Apply changes on OK button press"""
        self.onClose()
        self.onAccept()
        super(BasicDialog, self).accept()

    def reject(self):
        """Dismiss changes on Close button press"""
        self.onClose()
        self.onReject()
        super(BasicDialog, self).reject()
