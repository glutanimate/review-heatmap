# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from ....utils.platform import PLATFORM

from .qt import QDialog, QPushButton, QVBoxLayout, QLabel, Qt, QKeySequence


class QKeyGrabButton(QPushButton):
    def __init__(self, parent=None, key_string=""):
        super(QKeyGrabButton, self).__init__("", parent=parent)
        self.setKey(key_string)
        self.clicked.connect(self.grabKey)

    def setKey(self, key_string):
        self.key_string = key_string
        qkeyseq = QKeySequence(key_string, QKeySequence.PortableText)
        native_key_string = qkeyseq.toString(format=QKeySequence.NativeText)
        self.setText(native_key_string)
    
    def key(self):
        return self.key_string

    def grabKey(self):
        """Invoke key grabber"""
        grabber = QKeyGrab(self.parent())
        ret = grabber.exec_()
        if ret != 1:
            return
        key_string = grabber.key_string
        if not key_string:  # or not ret
            return
        self.setKey(key_string)


class QKeyGrab(QDialog):
    """
    Simple key combination grabber for hotkey assignments

    Based in part on ImageResizer by searene
    (https://github.com/searene/Anki-Addons)
    """

    platform_modkey_names = {
        "lin": {"meta": "Meta", "ctrl": "Ctrl",
                "alt": "Alt", "shift": "Shift"},
        "win": {"meta": "Win", "ctrl": "Ctrl", "alt":
                "Alt", "shift": "Shift"},
        "mac": {"meta": "Control", "ctrl": "Command",
                "alt": "Option", "shift": "Shift"}
    }

    modkey_names = platform_modkey_names[PLATFORM]

    def __init__(self, parent):
        """
        Initialize dialog

        Arguments:
            parent {QWidget} -- Parent Qt widget
        """
        QDialog.__init__(self, parent=parent)
        self.parent = parent
        # self.active is used to trace whether there's any key held now:
        self.active = 0
        self.resetDialog()
        self.setupUI()

    def setupUI(self):
        """Basic UI setup"""
        mainLayout = QVBoxLayout()
        self.label = QLabel("Please press the key combination\n"
                            "you would like to assign")
        self.label.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.label)
        self.setLayout(mainLayout)
        self.setWindowTitle("Grab key combination")

    def resetDialog(self):
        self.extra = self.key_string = None
        self.meta = self.ctrl = self.alt = self.shift = False

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
        msg = None
        if not (self.shift or self.ctrl or self.alt or self.meta):
            msg = ("Please use at least one keyboard modifier\n"
                   "({meta}, {ctrl}, {alt}, {shift})".format(
                       **self.modkey_names))
        if (self.shift and not (self.ctrl or self.alt or self.meta)):
            msg = ("Shift needs to be combined with at least one\n"
                   "other modifier ({meta}, {ctrl}, {alt})".format(
                       **self.modkey_names))
        if not self.extra:
            msg = ("Please press at least one key that is \n"
                   "not a modifier (not {meta}, {ctrl}, "
                   "{alt}, or {shift})".format(
                       **self.modkey_names))

        if msg:
            self.label.setText(msg)
            self.resetDialog()
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

        self.accept()
