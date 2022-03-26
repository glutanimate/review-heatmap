# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Simple dialog with support for mapping widget state from/to dictionary
keys and/or setter/getter methods.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import *

from ...utils import getNestedValue, setNestedValue
from .dialog_basic import BasicDialog

__all__ = ["MappedDialog"]


class MappedDialog(BasicDialog):

    def __init__(self, mapped_widgets, data, defaults,
                 form_module=None, parent=None, **kwargs):
        """
        Simple dialog with support for mapping widget state from/to dictionary
        keys and/or setter/getter methods.

        Arguments:
            mapped_widgets {sequence} -- A list/tuple of mappings between
                                         widget names, dictionary keys, and
                                         special methods to act as mediators
                                         (see below for specs)
            data {dict} -- Dictionary containing user data
            defaults {dict} -- Dictionary containing default data

        Keyword Arguments:
            form_module {PyQt form module} -- Dialog form module generated
                                              through pyuic (default: {None})
            parent {QWidget} -- Parent Qt widget (default: {None})

        --- mapped_widgets specifications ---

        mapped_widgets should consist of a sequence (list or tuple) of tuples
        of the form:

        > ("widget_object_name", property_mapping_tuple)

        where widget_object_name is the valid object name of a widget
        found in the current dialog, or a qualified dot-separated attribute
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

            "dataPath" {tuple} -- Sequence of dictionary keys / sequence
                                  indices pointing to valid entry
                                  in the data and defaults dictionaries
                                  (e.g. ("synced", "mode", 1) for getting
                                  self.data["synced"]["mode"][1]) )
            "setter" {str} -- Name of method called to either process
                              config value before being applied to the
                              widget property, or to return a config value
                              through other means
            "getter" {str} -- Name of method called to either process
                              widget value before being applied to the
                              configuration, or to return a widget value
                              through other means

        Only the following combinations of the above are supported:

            "dataPath" only:
                Values are read from and written to self.config
                with no processing applied
            "dataPath" and "setter" / "getter":
                Values are processed after reading and/or before writing
            "setter" / "getter":
                Reading and/or writing the values is delegated to the
                provided methods

        The string values provided for the "setter" and "getter" keys
        describe instance methods of this class or classes inheriting
        from it.

        In summary, an example of a valid mapped_widgets object could
        look as follows:

        > (
        >     ("form.dateLimData", (
        >         ("value", {
        >             "dataPath": ("synced", "limdate")
        >         }),
        >         ("min", {
        >             "setter": "_setDateLimDataMIn"
        >         }),
        >         ("max", {
        >             "setter": "_setDateLimDataMax"
        >         }),
        >     )),
        >     ("form.selHmCalMode", (
        >         ("items", {
        >             "setter": "_setSelHmCalModeItems"
        >         }),
        >         ("value", {
        >             "dataPath": ("synced", "mode"),
        >             "setter": "_setselHmCalModeValue"
        >         }),
        >     ))
        > )
        """
        super(MappedDialog, self).__init__(form_module=form_module,
                                           parent=parent, **kwargs)
        self._mapped_widgets = mapped_widgets
        self._defaults = defaults
        self._data = data
        self.setData(data)

    # API

    def setData(self, data):
        for widget_name, properties in self._mapped_widgets:
            for key, property_dict in properties:
                value = self._dataToWidgetVal(data, property_dict)
                self.interface.set(widget_name, key, value)

    def getData(self):
        for widget_name, properties in self._mapped_widgets:
            for key, property_dict in properties:
                data_path = self._dataPathToList(
                    property_dict.get("dataPath", ""))
                if not data_path:  # property irrelevant for config
                    continue
                widget_val = self.interface.get(widget_name, key)
                self._widgetToDataVal(self._data, property_dict, widget_val,
                                      data_path)
        return self._data

    def restoreData(self):
        self.setData(self._defaults)

    # Events

    def _setupEvents(self):
        super(MappedDialog, self)._setupEvents()
        if getattr(self.form, "buttonBox", None):
            restore_btn = self.form.buttonBox.button(
                QDialogButtonBox.StandardButton.RestoreDefaults)
            if restore_btn:
                restore_btn.clicked.connect(self.restoreData)

    # Utility functions to translate data into widget state and vice versa

    def _dataPathToList(self, path):
        if not path:
            return []
        crumbs = path.split("/")
        return [c if not c.strip("-").isdigit() else
                int(c.strip("-")) * (-1 if c.startswith("-") else 1)
                for c in crumbs]

    def _dataToWidgetVal(self, data, property_dict):
        """
        Get value from config and translate it to valid widget
        value, optionally pre-processing it using defined
        setter method

        Arguments:
            data {dict} -- Dictionary of user config values
            property_dict {dict} -- Dictionary describing widget <-> config
                                 mappping

        Returns:
            object -- Valid value for widget
        """
        data_path = self._dataPathToList(
            property_dict.get("dataPath", ""))
        setter_name = property_dict.get("setter", "")
        setter = getattr(self, setter_name, None) if setter_name else None
        data_val = getNestedValue(data, data_path) if data_path else None

        if setter is not None:
            widget_val = setter(data_val)
        else:
            widget_val = data_val

        return widget_val

    def _widgetToDataVal(self, data, property_dict, widget_val, data_path):
        """
        Get widget state/value and translate it to valid
        config value, optionally pre-processing it using defined
        getter method

        Arguments:
            property_dict {dict} -- Dictionary describing widget <-> config
                                 mappping
            widget_val {object} -- Current widget value

        Returns:
            tuple  -- tuple of data_path {tuple} and data_val {object}
        """
        getter_name = property_dict.get("getter", None)
        getter = getattr(self, getter_name, None) if getter_name else None

        if getter:
            data_val = getter(widget_val)
        else:
            data_val = widget_val

        setNestedValue(data, data_path, data_val)
