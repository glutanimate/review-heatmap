# -*- coding: utf-8 -*-

"""
Add-on agnostic options dialog module

Depends on presence of the following parent-level modules:
    
    consts, about

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals


from aqt.qt import *
from aqt.utils import showInfo, openLink

from ..consts import (ADDON_NAME, ADDON_VERSION, ADDON_HELP,
                      LINK_PATREON, LINK_COFFEE, LINK_RATE,
                      LINK_TWITTER, LINK_YOUTUBE)


from ..about import get_about_string  # noqa: E402


# Utility functions for operating with nested config collections

def getNestedValue(obj, keys):
    """
    Get value out of nested collection by supplying tuple of
    nested keys/indices

    Arguments:
        obj {list/dict} -- Nested collection
        keys {tuple} -- Key/index path leading to config val

    Returns:
        object -- Config value
    """
    cur = obj
    for nr, key in enumerate(keys):
        cur = cur[key]
    return cur


def setNestedValue(obj, keys, value):
    """
    Set value in nested collection by supplying tuple of
    nested keys / indices, and value to set

    Arguments:
        obj {list/dict} -- Nested collection
        keys {tuple} -- Tuple of keys/indices
        value {object} -- Key/index path leading to config val
    """
    depth = len(keys) - 1
    cur = obj
    for nr, key in enumerate(keys):
        if nr == depth:
            cur[key] = value
            return
        cur = cur[key]


# Options dialog and associated classes

class OptionsDialog(QDialog):

    """
    Add-on agnostic options dialog
    """

    def __init__(self, form, widgets, conf, defaults, parent=None):
        """
        Initialize options dialog with provided form and widgets, and
        set widget values based on provided conf dict.

        Arguments:
            form {PyQt form module} -- PyQt dialog form outlining the UI
            widgets {tuple} -- Tuple of dictionaries containing
                               widget <-> config key mappings
            conf {dict} -- Dictionary of user config values
            defaults {dict} -- Dictionary of default config values

        Keyword Arguments:
            parent {QWidget} -- Parent Qt widget (default: {None})

        Widget tuple specifications:
            Each member of the tuple should be a dictionary defining one
            widget and its value <-> config key mappings.

            Required dictionary keys:
                - "name": object name of the widget (e.g. `cbMain`)
                - "type": Qt type of the widget (e.g. `checkbox`)
                - "current": Mapping for the current value/state of the widget
                             (e.g. `("config", "main", 0)`)

            Optional dictionary keys:
                - Any number of additional value mappings for other widget
                  properties, e.g. minimum and maximum value, may be specified
                  (depending on which ones are supported by the widget type).
                  These follow the same specifications as the "current" entry

            Mapping dictionary specifications:

                A widget's properties can be assigned either by specifying
                a configuration path, or by specifying a callable to either
                parse the value beforehand or return a valid widget value
                without parsing the config directly.

                Similarly, when writing a config value changes may either be
                performed directly, or the value may be pre-processed by a
                specified callable.

                Paths to a config value in the provided conf collection
                are specified through the `confPath` key.

                Callables for processing a config value before setting
                a widget property to it are specified with the `getter`
                key.

                Callables for processing widget values to valid config values
                may be specified with the `setter` key.

                Example of a fully realized widget dictionary:

                > {
                >     "name": "listDecks",
                >     "type": "list",
                >     "current": {
                >         "confPath": ("config", "ignoredDecks"),
                >         "getter": "getIgnoredDecks",
                >         "setter": "setIgnoredDecks"
                >     }
                > },

            Supported Qt widget types, keywords, and properties:

                Qt Widget       type keyword        properties
                =====================================================
                QCheckBox        "checkbox"           current
                QComboBox        "combobox"           current, items
                QSpinBox         "spinbox"            current
                QListWIdget      "list"               current, items
                custom           "keygrabber"         current

        Widget form specifications:

            The form needs to contain a number of prespecified widgets:

            - Buttons for social media links, etc.:

                btnCoffee, btnPatreon, btnRate, btnTwitter, btnYoutube, btnHelp

            - A buttonBox with one button for each of the following roles:

                AcceptRole, RejectRole, ResetRole

            - Two label areas for showing version info and credits:

                labInfo, labAbout

        """

        super(OptionsDialog, self).__init__(parent=parent)
        self.conf = conf
        self.parent = parent
        self.widgets = widgets
        self.defaults = defaults
        # Set up UI from pre-generated UI form:
        self.form = form.Ui_Dialog()
        self.form.setupUi(self)
        # Perform any subsequent setup steps:
        self.setupLabels()
        self.setupEvents()
        self.applyConfig(conf)

    # Static widget setup

    def setupLabels(self):
        info_string = "{} v{}".format(ADDON_NAME, ADDON_VERSION)
        about_string = get_about_string()
        self.form.labInfo.setText(info_string)
        self.form.labAbout.setText(about_string)

    # User-entry widgets setup

    def confToWidgetVal(self, conf, value_dict):
        conf_path = value_dict.get("confPath", None)
        getter_name = value_dict.get("getter", None)
        getter = getattr(self, getter_name, None) if getter_name else None
        conf_val = getNestedValue(conf, conf_path) if conf_path else None

        if conf_val is not None and getter is not None:
            widget_val = getter(conf_val)
        elif getter is not None:
            widget_val = getter()
        elif conf_val is not None:
            widget_val = conf_val
        else:
            widget_val = None

        return widget_val

    def widgetToConfVal(self, value_dict, widget_val):
        conf_path = value_dict.get("confPath", None)
        setter_name = value_dict.get("setter", None)
        setter = getattr(self, setter_name, None) if setter_name else None

        if setter:
            conf_val = setter(widget_val)
        else:
            conf_val = widget_val

        return conf_path, conf_val

    def applyConfig(self, conf):
        """Set up widget data based on provided config dict"""

        for widget_dict in self.widgets:
            object_name, object_type = widget_dict["name"], widget_dict["type"]
            widget = getattr(self.form, object_name, None)

            if widget is None:
                print("Widget for object name {} not found".format(object_name))
                continue

            current = self.confToWidgetVal(conf, widget_dict["current"])

            if object_type == "combobox":
                widget.clear()
                items = self.confToWidgetVal(conf, widget_dict["items"])

                idx = 0
                cur_idx = 0
                for item_tuple in items:
                    label, key = item_tuple
                    widget.addItem(label, key)
                    if key == current:
                        cur_idx = idx
                    idx += 1

                widget.setCurrentIndex(cur_idx)

            elif object_type == "checkbox":
                widget.setChecked(current)

            elif object_type == "spinbox":
                widget.setValue(current)

            elif object_type == "dateedit":
                minimum = self.confToWidgetVal(conf, widget_dict["minimum"])
                minDateTime = QDateTime()
                minDateTime.setTime_t(minimum)

                if current:
                    curDateTime = QDateTime()
                    curDateTime.setTime_t(current)
                else:
                    curDateTime = minDateTime

                widget.setMinimumDateTime(minDateTime)
                widget.setDateTime(curDateTime)

            elif object_type == "keygrabber":
                self.updateHotkey(widget, current)
                widget.clicked.connect(lambda _, a=widget: self.grabKeyFor(a))

            else:
                print("Unhandled widget type: {}".format(object_type))
                continue

    def getConfig(self, conf):

        for widget_dict in self.widgets:
            object_name, object_type = widget_dict["name"], widget_dict["type"]
            widget = getattr(self.form, object_name, None)

            if widget is None:
                print("Widget for object name {} not found".format(object_name))
                continue

            if object_type == "combobox":
                current_index = widget.currentIndex()
                widget_val = widget.itemData(current_index, Qt.UserRole)

            elif object_type == "checkbox":
                widget_val = widget.isChecked()

            elif object_type == "spinbox":
                widget_val = widget.value()

            elif object_type == "dateedit":
                curDateTime = widget.dateTime()
                # Qt4 does not support toSecsSinceEpoch
                widget_val = curDateTime.toMSecsSinceEpoch() // 1000

            elif object_type == "keygrabber":
                widget_val = widget.text()

            conf_path, conf_val = self.widgetToConfVal(widget_dict["current"],
                                                       widget_val)
            setNestedValue(conf, conf_path, conf_val)

        return conf

    # Events

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Enter or evt.key() == Qt.Key_Return:
            evt.accept()
            return
        super(OptionsDialog, self).keyPressEvent(evt)

    def setupEvents(self):
        self.form.btnCoffee.clicked.connect(lambda: openLink(LINK_COFFEE))
        self.form.btnPatreon.clicked.connect(lambda: openLink(LINK_PATREON))
        self.form.btnRate.clicked.connect(lambda: openLink(LINK_RATE))
        self.form.btnTwitter.clicked.connect(lambda: openLink(LINK_TWITTER))
        self.form.btnYoutube.clicked.connect(lambda: openLink(LINK_YOUTUBE))
        self.form.btnHelp.clicked.connect(lambda: openLink(ADDON_HELP))
        restore_btn = self.form.buttonBox.button(
            QDialogButtonBox.RestoreDefaults)
        restore_btn.clicked.connect(self.restore)

    # Keygrabber widgets

    def updateHotkey(self, btn, hotkey):
        """Update hotkey label and attribute"""
        btn.setText(hotkey)

    def grabKeyFor(self, btn):
        """Invoke key grabber"""
        win = GrabKey(self, lambda key: self.updateHotkey(btn, key))
        win.exec_()

    # Button box

    def restore(self):
        """Restore widgets back to defaults"""
        self.applyConfig(self.defaults)

    def accept(self):
        """Apply changes on OK button press"""
        super(OptionsDialog, self).accept()

    def reject(self):
        """Dismiss changes on Close button press"""
        super(OptionsDialog, self).reject()


class GrabKey(QDialog):
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
        self.extra = None
        self.setupUI()

    def setupUI(self):
        """
        Basic UI setup
        """
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        label = QLabel('Please press the new key combination')
        mainLayout.addWidget(label)
        self.setWindowTitle('Grab key combination')

    def keyPressEvent(self, evt):
        """
        Interecept key presses and save current key plus
        active modifiers.

        Arguments:
            evt {QKeyEvent} -- Intercepted key press event
        """
        self.active += 1
        if evt.key() > 0 and evt.key() < 127:
            self.extra = chr(evt.key())
        elif evt.key() == Qt.Key_Control:
            self.ctrl = True
        elif evt.key() == Qt.Key_Alt:
            self.alt = True
        elif evt.key() == Qt.Key_Shift:
            self.shift = True
        elif evt.key() == Qt.Key_Meta:
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

        if not (self.shift or self.ctrl or self.alt or self.meta):
            showInfo("Please use at least one keyboard "
                     "modifier (Win, Ctrl, Alt, Shift)")
            return
        if (self.shift and not (self.ctrl or self.alt or self.meta)):
            showInfo("Shift needs to be combined with at "
                     "least one other modifier (Ctrl, Alt)")
            return
        if not self.extra:
            showInfo("Please press at least one key "
                     "that is not a keyboard modifier (not Win/Ctrl/Alt/Shift)")
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

        key_string = "+".join(combo)
        # TODO: Show key string according to platform-specific key designations:
        # keySeq = QKeySequence(key_string)
        # key_string = keySeq.toString(format=QKeySequence.NativeText)

        self.callback(key_string)

        self.close()
