# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from .qt import QDialog, QPushButton, QVBoxLayout, QLabel, Qt
from .utils import showInfo

class QKeyGrabButton(QPushButton):
    def __init__(self, text, parent=None):
        super(QKeyGrabButton, self).__init__(text, parent=parent)
        self.clicked.connect(self.grabKey)

    def grabKey(self):
        """Invoke key grabber"""
        grabber = QKeyGrab(self.parent())
        ret = grabber._exec()
        # if not ret...
        print(ret)
        key_string = grabber.key_string
        if not key_string:  # or not ret
            return
        self.setText(key_string)


class QKeyGrab(QDialog):
    """
    Simple key combination grabber for hotkey assignments

    Largely based on ImageResizer by searene
    (https://github.com/searene/Anki-Addons)
    """

    def __init__(self, parent, callback):
        """
        Initialize dialog

        Arguments:
            parent {QWidget} -- Parent Qt widget
            callback {function} -- Callable to run once dialog exits.
                                   Needs to be able to take a hotkey
                                   string as an argument.
        """

        QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.callback = callback
        # self.active is used to trace whether there's any key held now:
        self.active = 0
        self.meta = self.ctrl = self.alt = self.shift = False
        self.extra = self.key_string = None
        self.setupUI()

    def setupUI(self):
        """Basic UI setup"""
        mainLayout = QVBoxLayout()
        label = QLabel("Please press they key combination\n"
                       "you would like to assign")
        mainLayout.addWidget(label)
        self.setLayout(mainLayout)
        self.setWindowTitle("Grab key combination")

    def keyPressEvent(self, evt):
        """
        Intercept key presses and save current key plus
        active modifiers.

        Arguments:
            evt {QKeyEvent} -- Intercepted key press event
        """
        self.active += 1
        
        key = evt.key()
        if key > 0 and key < 127:
            self.extra = chr(key)
        elif key == Qt.Key_Control:
            self.ctrl = True
        elif key == Qt.Key_Alt:
            self.alt = True
        elif key == Qt.Key_Shift:
            self.shift = True
        elif key == Qt.Key_Meta:
            self.meta = True

    def keyReleaseEvent(self, evt):
        """
        Intercept key release event, checking and then saving key combo
        and exiting dialog.

        Arguments:
            evt {QKeyEvent} -- Intercepted key release event
        """
        self.active -= 1

        if self.active != 0:
            # at least 1 key still held
            return

        # TODO: platform-specific messages
        if not (self.shift or self.ctrl or self.alt or self.meta):
            showInfo("Please use at least one keyboard modifier\n"
                     "(Win, Ctrl, Alt, Shift)")
            return
        if (self.shift and not (self.ctrl or self.alt or self.meta)):
            showInfo("Shift needs to be combined with at least one\n"
                     "other modifier (Win, Ctrl, Alt)")
            return
        if not self.extra:
            showInfo("Please press at least one key that is \n"
                     "not a modifier (not Win, Ctrl, Alt, or Shift)")
            return

        combo = []
        if self.meta:
            combo.append("Meta")
        if self.ctrl:
            combo.append("Ctrl")
        if self.shift:
            combo.append("Shift")
        if self.alt:
            combo.append("Alt")
        combo.append(self.extra)

        self.key_string = "+".join(combo)
        # TODO: Show key string according to platform-specific key designations:
        # keySeq = QKeySequence(key_string)
        # key_string = keySeq.toString(format=QKeySequence.NativeText)

        self.accept()
