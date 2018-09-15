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

from ..consts import ADDON_NAME, ADDON_VERSION, LINKS
from ..utils.utils import getNestedValue, setNestedValue
from .about import get_about_string
from ..utils.platform import PLATFORM

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

    def __init__(self, form, widgets, config, parent=None):
        super(OptionsDialog, self).__init__(form=form, parent=parent)
        self.widgets = widgets
        self.config = config
        # Perform any subsequent setup steps:
        self.setupCustomWidgets()
        if PLATFORM == "mac":
            self.setupTabs()
        self.setupInfo()
        self.setupEvents()
        self.setConfig(config)

    # Addon-specific widget setups go here:

    def setupCustomWidgets(self):
        pass

    # Static widget setup

    def setupTabs(self):
        """
        Decrease tab margins on macOS
        """
        tab_widget = getattr(self.form, "tabWidget", None)
        if not tab_widget:
            return
        for idx in range(tab_widget.count()):
            tab = tab_widget.widget(idx)
            layout = tab.layout()
            layout.setContentsMargins(3, 3, 3, 3)

    def setupInfo(self):
        """
        Fill out info & about text elements
        """
        if hasattr(self.form, "labInfo"):
            info_string = "{} v{}".format(ADDON_NAME, ADDON_VERSION)
            self.form.labInfo.setText(info_string)
        if hasattr(self.form, "htmlAbout"):
            about_string = get_about_string()
            self.form.htmlAbout.setHtml(about_string)

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
        for name, link in LINKS.items():
            btn_widget = getattr(self.form, "btn" + name.capitalize(), None)
            if not btn_widget:
                continue
            btn_widget.clicked.connect(lambda: openLink(link))

        if getattr(self.form, "buttonBox", None):
            restore_btn = self.form.buttonBox.button(
                QDialogButtonBox.RestoreDefaults)
            if restore_btn:
                restore_btn.clicked.connect(self.restore)

    def restore(self):
        """Restore widgets back to defaults"""
        self.setConfig(self.config.defaults)

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
        setter_name = properties.get("setter", None)
        setter = getattr(self, setter_name, None) if setter_name else None

        if setter:
            conf_val = setter(widget_val)
        else:
            conf_val = widget_val

        return conf_val

    def setConfig(self, config):
        """Set up widget data based on provided config dict"""
        for widget_name, properties in self.widgets:
            for key, property_dict in properties:
                value = self.confToWidgetVal(config, property_dict)
                self.interface.set(widget_name, key, value)

    def saveConfig(self):
        """Get data from dialog and write it to config"""
        config = self.config
        for widget_name, properties in self.widgets:
            for key, property_dict in properties:
                conf_path = property_dict.get("confPath", None)
                if not conf_path:  # property irrelevant for config
                    continue
                widget_val = self.interface.get(widget_name, key)
                conf_val = self.widgetToConfVal(property_dict, widget_val)
                setNestedValue(config, conf_path, conf_val)
        config.save()

    def onAccept(self):
        self.saveConfig()
        super(OptionsDialog, self).onAccept()
