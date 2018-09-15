# -*- coding: utf-8 -*-

"""
Generic options dialog for Anki add-ons

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""


from __future__ import unicode_literals

from aqt.qt import Qt, QDialogButtonBox

from aqt.utils import openLink

from .basic.dialog import BasicDialog

from ..consts import ADDON_NAME, ADDON_VERSION, LINKS
from ..utils.utils import getNestedValue, setNestedValue
from .about import get_about_string
from ..utils.platform import PLATFORM

# TODO: consider more elegant implementation of widgets_tuple
#       (perhaps doing away with it entirely)

# Options dialog and associated classes

class OptionsDialog(BasicDialog):

    def __init__(self, form_module, widgets_tuple, config, parent=None):

        """
        Creates an options dialog with the provided Qt form and populates its
        widgets from a ConfigManager config object.

        Arguments:
            form_module {PyQt form module} -- Dialog form module generated
                                              through pyuic
            widgets_tuple {tuple} -- A tuple of mappings between widget names,
                                     config value names, and special methods
                                     to act as mediators (see below for specs)
            config {ConfigManager} -- ConfigManager object providing access to
                                      add-on config values

        Keyword Arguments:
            parent {QWidget} -- Parent Qt widget (default: {None})

        ------- Detailed Information -------

        --- Widgets tuple specifications ---

        The widgets tuple should consist of a series of tuples
        of the form:

        > ("widget_object_name", property_mapping_tuple)

        where widget_object_name is the valid object name of a widget
        found in the options dialog, or a qualified dot-separated attribute
        path leading to it (e.g. "form.selHmlCol" for self.form.selHmCol)

        Each property mapping tuple should be phrased as follows:

        > ("property_descriptor", assignment_dictionary)

        where property_descriptor is a valid name as per the keys defined
        in CommonWidgetInterface.methods_by_key
        (as of writing: "value", "items", "current", "min", "max")

        The key, value pairs defined in the assignment dictionary determine
        the way in which config values are applied to and read from their
        corresponding widgets.

        The following key, value pairs are supported:

            "confPath" {tuple} -- Sequence of dictionary keys / sequence
                                    indices pointing to valid config value
                                    to be used for specified widget property
                                    (e.g. ("synced", "mode", 1) for getting
                                    self.config["synced"]["mode"][1]) )
            "getter" {str} -- Name of method called to either process
                                config value before being applied to the
                                widget property, or to return a config value
                                through other means
            "setter" {str} -- Name of method called to either process
                                widget value before being applied to the
                                configuration, or to return a widget value
                                through other means

        Only the following combinations of the above are supported:

            "confPath" only:
                Values are read from and written to self.config
                with no processing applied
            "confPath" and "getter" / "setter":
                Values are processed after reading and/or before writing
            "getter" / "setter":
                Reading and/or writing the values is delegated to the
                provided methods
                        
        The string values provided for the "getter" and "setter" keys
        describe instance methods of this class or classes inheriting
        from it.

        In summary, an example of a valid widgets tuple could look as
        follows:
        
        > (
        >     ("form.dateLimData", (
        >         ("value", {
        >             "confPath": ("synced", "limdate")
        >         }),
        >         ("min", {
        >             "getter": "getColCreationTime"
        >         }),
        >         ("max", {
        >             "getter": "getCurrentTime"
        >         }),
        >     )),
        >     ("form.selHmCalMode", (
        >         ("items", {
        >             "getter": "getHeatmapModes"
        >         }),
        >         ("value", {
        >             "confPath": ("synced", "mode"),
        >             "getter": "getHeatmapModeValue"
        >         }),
        >     ))
        > )
        """
        super(OptionsDialog, self).__init__(
            form_module=form_module, parent=parent)
        self.widgets = widgets_tuple
        self.config = config

    def setupDialog(self):
        # Perform any subsequent setup steps:
        self.setupCustomWidgets()
        if PLATFORM == "mac":
            self.setupTabs()
        self.setupInfo()
        self.setupEvents()
        self.setConfig(self.config)

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
