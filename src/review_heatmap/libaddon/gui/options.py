# -*- coding: utf-8 -*-

"""
Add-on agnostic options dialog module

Depends on presence of the following parent-level modules:
    
    consts, about

---------------------------------------------------------------

OptionsDialog specifications:

1.) Widget tuple

Each member of the tuple should be a dictionary defining one
widget and its value <-> config key mappings.

Required dictionary entries:
    - "name": object name of the widget (e.g. `cbMain`)
    - "type": Qt type of the widget (e.g. `checkbox`)
    - "current": Mapping dictionary for the current value/state
                 of the widget

Optional dictionary entries:
    - Any number of additional mappings for other widget
      properties, e.g. minimum and maximum value, may be specified
      (depending on which ones are supported by the widget type).
      These follow the same specifications as the "current" entry

2.) Mapping dictionaries:

A widget's properties can be assigned either by specifying
a configuration path, or by specifying a callable to either
parse the value beforehand or return a valid widget value
without parsing the config directly.

Similarly, when writing a config value changes may either be
performed directly, or the value may be pre-processed by a
specified callable.

Paths to a config value in the provided conf collection
are specified through the `confPath` key and provided
as tuples of dictionary keys / list indices
(e.g. `("config", "main", 0)`).

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

3.) Supported Qt widgets:

What follows is a list of all supported Qt widgets, the keywords they
are designated by, and the supported properties that can be assigned
through mapping dictionaries:

Qt Widget       type keyword            properties       input value
====================================================================
QCheckBox        "checkbox"           current              boolean
QComboBox        "combobox"           current, items        
QSpinBox         "spinbox"            current
QListWIdget      "list"               current, items
custom           "keygrabber"         current

2.) Widget form specifications:

The form needs to contain a number of prespecified widgets:

- Buttons for social media links, etc.:

    btnCoffee, btnPatreon, btnRate, btnTwitter, btnYoutube, btnHelp

- A buttonBox with one button for each of the following roles:

    AcceptRole, RejectRole, ResetRole

- Two label areas for showing version info and credits:

    labInfo, labAbout

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

# TODO: add support for QLineEdit/QPlainTextEdit, QRadioButton,
#       QPushButton, QDoubleSpinBox, QSlider, QFontSelectionDialog,
#       custom color selectors
# TODO: migrate to QKeySequenceEdit once support for anki20 is dropped

from __future__ import unicode_literals

from aqt.qt import Qt, QDialogButtonBox

from aqt.utils import openLink

from .basic.dialog import BasicDialog
from .basic.interface import INTERFACE_API_BY_KEY

from ..consts import (ADDON_NAME, ADDON_VERSION, ADDON_HELP,
                      LINK_PATREON, LINK_COFFEE, LINK_RATE,
                      LINK_TWITTER, LINK_YOUTUBE)

from ..about import get_about_string  # noqa: E402

from ..config import getNestedValue, setNestedValue


# Options dialog and associated classes

class OptionsDialog(BasicDialog):

    """
    Add-on agnostic options dialog

    Creates an options dialog with provided form and widgets, and
    sets widget values based on provided conf dict.

    Arguments:
        form {PyQt form module} -- PyQt dialog form outlining the UI
        widgets {tuple} -- Tuple of dictionaries containing
                           widget <-> config key mappings
        conf {dict} -- Dictionary of user config values
        defaults {dict} -- Dictionary of default config values

    Keyword Arguments:
        parent {QWidget} -- Parent Qt widget (default: {None})

    """

    def __init__(self, form, widgets, conf, defaults, parent=None):
        super(OptionsDialog, self).__init__(form=form, parent=parent)
        self.widgets = widgets
        self.conf = conf
        self.defaults = defaults
        # Perform any subsequent setup steps:
        self.setupCustomWidgets()
        self.setupLabels()
        self.setupEvents()
        self.setConfig(conf)

    # Addon-specific widget setups go here:

    def setupCustomWidgets(self):
        pass

    # Static widget setup

    def setupLabels(self):
        info_string = "{} v{}".format(ADDON_NAME, ADDON_VERSION)
        about_string = get_about_string()
        self.form.labInfo.setText(info_string)
        self.form.labAbout.setText(about_string)

    # Events

    def keyPressEvent(self, evt):
        """
        Prevent accidentally closing dialog when editing complex widgets
        by ignoring Return and Escape
        """
        if evt.key() == Qt.Key_Enter or evt.key() == Qt.Key_Return:
            return evt.accept()
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

    def restore(self):
        """Restore widgets back to defaults"""
        self.applyConfig(self.defaults)

    # Utility functions to translate config into widget state and vice versa

    def confToWidgetVal(self, conf, properties):
        """
        Get value from config and translate it to valid widget
        value, optionally pre-processing it using defined
        getter method

        Arguments:
            conf {dict} -- Dictionary of user config values
            properties {dict} -- Dictionary describing widget <-> config
                                 mappping

        Returns:
            object -- Valid value for widget
        """
        conf_path = properties.get("confPath", None)
        getter_name = properties.get("getter", None)
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

    def widgetToConfVal(self, properties, widget_val):
        """
        Get widget state/value and translate it to valid
        config value, optionally pre-processing it using defined
        setter method

        Arguments:
            properties {dict} -- Dictionary describing widget <-> config
                                 mappping
            widget_val {object} -- Current widget value

        Returns:
            tuple  -- tuple of conf_path {tuple} and conf_val {object}
        """
        conf_path = properties.get("confPath", None)
        setter_name = properties.get("setter", None)
        setter = getattr(self, setter_name, None) if setter_name else None

        if setter:
            conf_val = setter(widget_val)
        else:
            conf_val = widget_val

        return conf_path, conf_val

    def setConfig(self, conf):
        """Set up widget data based on provided config dict"""
        for object_name, properties in self.widgets.items():
            widget = self.nameToWidget(object_name)

            if widget is None:
                raise NotImplementedError(
                    "Widget not implemented: ", object_name)

            for key in properties:
                if key in INTERFACE_API_BY_KEY:
                    value_setter = INTERFACE_API_BY_KEY[key][0]
                    if not value_setter:
                        raise NotImplementedError(
                            "Setter for widget property not implemented: ",
                            key)
                    value = self.confToWidgetVal(conf, properties[key])
                    value_setter(self, widget, value)
                else:
                    raise NotImplementedError(
                        "Widget property not implemented: ", key)

    def getConfig(self, conf):
        for object_name, properties in self.widgets.items():
            widget = self.nameToWidget(object_name)

            if widget is None:
                raise NotImplementedError(
                    "Widget not implemented: ", object_name)

            for key in properties:
                # FIXME: only if relevant for config
                if key in INTERFACE_API_BY_KEY:
                    value_getter = INTERFACE_API_BY_KEY[key][1]
                    if not value_getter:
                        raise NotImplementedError(
                            "Getter for widget property not implemented: ",
                            key)
                    widget_val = value_getter(self, widget)
                    conf_path, conf_val = self.widgetToConfVal(properties[key],
                                                               widget_val)
                    setNestedValue(conf, conf_path, conf_val)
                else:
                    raise NotImplementedError(
                        "Widget property not implemented: ", key)

        return conf
