# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
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
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Common interface to Qt widgets

Implements a number of common API calls that unify changing and reading
state from various Qt widgets. This allows for easier translation
between stored values and widget state, while also catching
type errors and other problems early on.

Subclassing each respective Qt widget would be the more elegant way,
but that is not feasible when primarily working with Qt designer generated
UIs.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from collections import MutableSequence, MutableSet, MutableMapping

from ...utils import getNestedAttribute
from ...platform import PYTHON3

from .widgets.qt import *
from .widgets.qkeygrabber import QKeyGrabButton
from .widgets.qcolorbutton import QColorButton
# TODO: Switch to QKeySequenceEdit once Qt4 support dropped
# TODO: add support for QSlider

__all__ = ["CommonWidgetInterface"]

# Variables used for type checks
MUTABLES = (MutableSequence, MutableSet, MutableMapping)
STRINGTYPES = (str,) if PYTHON3 else (str, unicode)
NUMERICTYPES = (int, float)
LISTTYPES = (list, tuple)


class CommonWidgetInterface(object):
    """
    Common interface to Qt widgets

    Implements a number of common API calls that unify changing and reading
    state from various Qt widgets. This allows for easier translation
    between stored values and widget state.

    Arguments:
        parent {QWidget} -- Qt parent widget whose children we want to control
                            with this interface (e.g. a QDialog instance)

    Raises:
        NotImplementedError -- In case of an unimplemented API call
        AssertionErorr -- In case of illegitimate API calls (e.g. wrong
                          value types, missing dictionary keys, etc.)


    ------- Detailed Description -------

    CommonWidgetInterface offers two ways of updating / reading
    a widget's properties:

        - by passing the Qt object (and value) on to public 'meta'
          getter/setter methods like getValue() or getCurrent()
        - by using the convenience methods set() and get() which take
          the widget name and property name and automatically
          determine the right 'meta' getter / setter methods to call

    In the second case, mapping between property names and corresponding
    'meta' getter/setter methods is assigned in the methods_by_key dictionary.

    In both cases, 'meta' getter methods like setValue or getValue
    in turn call the correct Qt API getters/setters depending
    on the widget type (sometimes after passing through other public
    'meta' getters/setters).

    A list of supported Qt widgets, properties, and data types may be found
    below:

    --- Setters ---

    QWidget         | value       items      current    min       max
    ================|=====================================================
    QColorButton    | str         -         -           -         -
    QKeyGrabButton  | str         -         -           -         -
    QCheckBox       | bool        -         -           -         -
    QRadioButton    | bool        -         -           -         -
    QSpinBox        | numeric     -         -           numeric   numeric
    QDoubleSpinBox  | numeric     -         -           numeric   numeric
    QComboBox       | immutable   listtypes immutable   -         -
    QListWidget     | listtypes   listtypes immutable   -         -
    QDateEdit       | int         -         -           int       int
    QLineEdit       | str         -         -           -         -
    QLabel          | str         -         -           -         -
    QPushButton     | str         -         -           -         -
    QTextEdit       | str         -         -           -         -
    QPlainTextEdit  | str         -         -           -         -
    QFontComboBox   | dict        -         -           -         -

    --- Getters ---

    QWidget         | value       items      current    min       max
    ================|=====================================================
    QColorButton    | str         -         -           -         -
    QKeyGrabButton  | str         -         -           -         -
    QCheckBox       | bool        -         -           -         -
    QRadioButton    | bool        -         -           -         -
    QSpinBox        | numeric     -         -           -         -
    QDoubleSpinBox  | numeric     -         -           -         -
    QComboBox       | immutable   listtypes immutable   -         -
    QListWidget     | listtypes   listtypes immutable   -         -
    QDateEdit       | int         -         -           -         -
    QLineEdit       | str         -         -           -         -
    QLabel          | str         -         -           -         -
    QPushButton     | str         -         -           -         -
    QTextEdit       | str         -         -           -         -
    QPlainTextEdit  | str         -         -           -         -
    QFontComboBox   | dict        -         -           -         -

    --- Additional notes ---

    QWidget         | Notes
    ================|=====================================================
    QColorButton    | str should be an HTML color code (e.g. "#FFFFFF")
    ----------------------------------------------------------------------
    QKeyGrabButton  | str should be a valid Qt key sequence (e.g. "Ctrl+F")
    ----------------------------------------------------------------------
    QComboBox       | items should be a tuple/list of tuples of the form
                    | (item_text {str}, item_data {immutable})
                    | value & current are mapped to the data of
                    | the current item
    ----------------------------------------------------------------------
    QListWidget     | items should be a tuple/list of tuples of the form
                    | (item_text, item_data)
                    | value is mapped to a list of all item data
                    | current is mapped to the data of the current item
    ----------------------------------------------------------------------
    QDateEdit       | value should be valid unix time in secs since epoch
    ----------------------------------------------------------------------
    QTextEdit,      | value can either be plain text or HTML
    QLabel          |
    ----------------------------------------------------------------------
    QFontComboBox   | value should be a dictionary with the following keys:
                    | - "family": font family {str}
                    | - "size": font point size {int}
                    | - "bold": font bold state {bool}
                    | - "italic": font italics state {bool}

    --- Legend ---
    
    Property keys:

        "value": Corresponds to the most commonly used property of each
                widget. E.g. in case of a QComboBox this might be the
                current item (or rather, its current data), while for a
                QListWidget it may be a list of all items
                (or rather, their data).

        "items": Relevant only to widgets with multiple user-modifiable
                 items. Corresponds to all widget items.

        "current": Relevancy same as above. Corresponds to the current
                   widget item (or rather, its data)

        "min"/"max": Relevant only to widgets with upper/lower boundaries.

        Property keys are assigned to different 'meta' methods in
        the methods_by_key dictionary.

    Types:

        "numeric": int, float
        "immutable": e.g. str, int, float
        "listtypes": list, tuple

    """

    # Property names assigned in this dictionary are used by set() / get()
    # to determine the correct 'meta' setter/getter to call
    #
    # Each value should be a tuple of
    # (setter_method_name {str}, getter_method_name {str})
    # where each name corresponds to a method of CommonWidgetInterface
    #
    # In case of an undefined setter or getter None should be used, instead.
    methods_by_key = {
        "value": ("setValue", "getValue"),
        "items": ("setValueList", "getValueList"),
        "current": ("setCurrentByData", "getCurrentData"),
        "min": ("setMinValue", None),
        "max": ("setMaxValue", None),
    }

    def __init__(self, parent):
        self.parent = parent

    # API
    ######################################################################

    # COMMON

    # Convenience methods that resolve widget_name -> widget and
    # property_name -> setter/getter method mappings defined in
    # methods_by_key

    def set(self, widget_name, property_name, data):
        """
        Sets widget data for given widget name, property name, and data
        
        Arguments:
            widget_name {str} -- Object name of Qt widget found in parent.
                                 Dot-separated attribute names are resolved
                                 automatically (e.g. "form.button" would
                                 be evaluated as self.parent.form.button)
            property_name {str} -- Name of the property to update, as defined
                                   in CommonWidgetInterface.methods_by_key.
                                   Currently supported:
                                   value, items, current, min, max
            data {obj} -- Data to set widget property to. Has to follow correct
                          type specs (see class-level docstring)
        
        Returns:
            object -- Setter return value
        """
        widget = self.nameToWidget(widget_name)
        
        try:
            setter = getattr(self, self.methods_by_key[property_name][0])
        except KeyError as error:
            error.args += ("Unrecognized widget property name: ",
                           property_name)
            raise
        except TypeError as error:
            error.args += ("Setter not defined for widget property name: ",
                           property_name)
            raise

        return setter(widget, data)

    def get(self, widget_name, property_name):
        """
        Gets widget data for given widget name and property name
        
        Arguments:
            widget_name {str} -- Object name of Qt widget. Dot-separated
                                 attribute names are resolved automatically
                                 (e.g. "form.button" would resolve to
                                  self.parent.form.button)
            property_name {str} -- Name of the property to update. Currently
                                   supported: value, items, current
        
        Returns:
            object -- Data assigned to widget property. Types follow type specs
                      defined in class-level docstring.
        """
        widget = self.nameToWidget(widget_name)

        try:
            getter = getattr(self, self.methods_by_key[property_name][1])
        except KeyError as error:
            error.args += ("Unrecognized widget property name: ",
                           property_name)
            raise
        except TypeError as error:  # raised when method name is None
            error.args += ("Setter not defined for widget property name: ",
                           property_name)
            raise
        
        return getter(widget)

    # Regular interface

    def setValue(self, widget, data):
        """
        Sets the current value for the provided widget.
        
        What constitutes the widget value varies depending on the widget, but
        tries to reflect the most common use case of that particular widget.

        For more information on the supported widgets and updated properties
        for each widget please see the class-level docstring.
        
        Arguments:
            widget {QWidget} -- Qt widget to update
            data {obj} -- Data to set widget property to. Has to follow correct
                          type specs (see class-level docstring)
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
            AssertionErorr -- In case of illegitimate API calls (e.g. wrong
                              value types, missing dictionary keys, etc.)
        """
        error_msg = "Invalid type {} for widget {}".format(type(data), widget)

        # custom widgets need to be listed first as they usually inherit
        # from default Qt widgets
        if isinstance(widget, QColorButton):
            assert isinstance(data, STRINGTYPES), error_msg
            widget.setColor(data)
        elif isinstance(widget, QKeyGrabButton):
            assert (isinstance(data, STRINGTYPES)), error_msg
            widget.setKey(data)
        elif isinstance(widget, (QCheckBox, QRadioButton)):
            assert isinstance(data, bool), error_msg
            widget.setChecked(data)
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            assert isinstance(data, NUMERICTYPES), error_msg
            widget.setValue(data)
        elif isinstance(widget, QComboBox):
            # data should be non-mutable
            assert not issubclass(type(data), MUTABLES), error_msg
            self._setComboCurrentByData(widget, data)
        elif isinstance(widget, QListWidget):
            try:
                self._checkItemTuples(data)
            except AssertionError as error:
                error.args.append(error_msg)
                raise
            self._addListValues(widget, data, clear=True)
        elif isinstance(widget, QDateEdit):
            assert isinstance(data, int), error_msg
            self._setDateTime(widget, data)
        elif isinstance(widget, (QLineEdit, QLabel, QPushButton)):
            assert (isinstance(data, STRINGTYPES)), error_msg
            widget.setText(data)
        elif isinstance(widget, QTextEdit):
            assert (isinstance(data, STRINGTYPES)), error_msg
            widget.setHtml(data)
        elif isinstance(widget, QPlainTextEdit):
            assert (isinstance(data, STRINGTYPES)), error_msg
            widget.setPlainText(data)
        elif isinstance(widget, QFontComboBox):
            assert isinstance(data, dict)
            self._setFontComboCurrent(data)
        else:
            raise NotImplementedError(
                "setValue not implemented for widget ", widget)

    def getValue(self, widget):
        """
        Gets the current value for the provided widget.
        
        What constitutes the widget value varies depending on the widget, but
        tries to reflect the most common use case of that particular widget.

        For more information on the supported widgets and returned
        properties for each widget please see the class-level docstring.
        
        Arguments:
            widget {QWidget} -- Qt widget to read data from
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
            AssertionError -- In case of illegitimate API calls (e.g. wrong
                              value types, missing dictionary keys, etc.)
        """

        # custom widgets need to be listed first as they usually inherit
        # from default Qt widgets
        if isinstance(widget, QColorButton):
            return widget.color()
        elif isinstance(widget, QKeyGrabButton):
            return widget.key()
        elif isinstance(widget, (QCheckBox, QRadioButton)):
            return widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return self._getComboCurrentData(widget)
        elif isinstance(widget, QListWidget):
            return self._getListData(widget)
        elif isinstance(widget, QDateEdit):
            return self._getDateTime(widget)
        elif isinstance(widget, (QLineEdit, QLabel, QPushButton)):
            return widget.text()
        elif isinstance(widget, QTextEdit):
            return widget.toHtml()
        elif isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, QFontComboBox):
            return self._getFontComboCurrent(widget)
        else:
            raise NotImplementedError(
                "getValue not implemented for widget ", widget)

    # WIDGETS WITH MULTIPLE ITEMS TO CHOOSE FROM:

    # setter

    def setValueList(self, widget, values, current=None, clear=True):
        """
        Sets the items of multi-item widgets based on a list of
        provided values.

        For more information on the supported widgets and updated properties
        for each widget please see the class-level docstring.
        
        Arguments:
            widget {QWidget} -- Qt widget to update. Supported:
                                QComboBox, QListWidget
            values {list,tuple} -- Sequence of values to create widget items
                                   from. Each value in the sequence should be
                                   a tuple of the form: (item_text, item_data)
        
        Keyword Arguments:
            current {immutable} -- Item to set as the current widget item,
                                   as characterized by its data
                                   (default: {None})
            clear {bool} -- Whether to clear all existing widget items before
                            creating any new items (default: {True})
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
            AssertionError -- In case of illegitimate API calls (e.g. wrong
                              value types, missing dictionary keys, etc.)
        
        Returns:
            object -- Setter return value
        """
        try:
            self._checkItemTuples(values)
            assert not issubclass(type(current), MUTABLES), \
                "current data should be an immutable type (e.g. str or int)"
            assert isinstance(clear, bool), \
                "clear should be set to a boolean"
        except AssertionError as error:
            error.args += ("Widget: ", widget)
            raise

        if isinstance(widget, QComboBox):
            return self._addComboValues(widget, values, current_data=current,
                                        clear=clear)
        elif isinstance(widget, QListWidget):
            return self._addListValues(widget, values, current_data=current,
                                       clear=clear)
        else:
            raise NotImplementedError(
                "setValues not implemented for widget ", widget)

    def setValueListAndCurrent(self, widget, values, current):
        """
        Convenience method to set a series of widget items and select
        a specific item to be the current item.
        
        See setValueList docstring for the method signature.

        Type checking and error handling delegated to setValueList
        """
        return self.setValueList(widget, values, current=current)

    def addValues(self, widget, values):
        """
        Convenience method to add a series of widget items without
        removing the existing ones.

        See setValueList docstring for the method signature.

        Type checking and error handling delegated to setValueList
        """
        return self.setValueList(widget, values, clear=False)

    def addValueAndMakeCurrent(self, widget, value):
        """
        Convenience method to add a widget item and make it the current one.

        See setValueList docstring for the method signature.

        Type checking and error handling delegated to setValueList
        """
        return self.setValueList(widget, [value], current=value[1],
                                 clear=False)

    def removeItemsByData(self, widget, data_to_remove):
        """
        Removes items from a widget by the provided sequence of data values

        Arguments:
            widget {QWidget} -- Qt widget to update. Supported:
                                QComboBox, QListWidget
            data_to_remove {list,tuple} -- Sequence of data values to identify
                                           and remove items by. Values should
                                           be immutable types (e.g. str or int)

        Raises:
            NotImplementedError -- In case of an unimplemented widget
            AssertionError -- In case of illegitimate API calls (e.g. wrong
                              value types, missing dictionary keys, etc.)
        """
        assert isinstance(data_to_remove, LISTTYPES), \
            "data_to_remove should be a list or tuple"
        assert (not data_to_remove or
                not issubclass(type(data_to_remove[0]), MUTABLES)), \
            "data_to_remove should contain immutables (e.g. str or int)"

        if isinstance(widget, QComboBox):
            return self._removeComboItemsByData(widget, data_to_remove)
        elif isinstance(widget, QListWidget):
            return self._removeListItemsByData(widget, data_to_remove)
        else:
            raise NotImplementedError(
                "removeValues not implemented for widget ", widget)

    def removeSelected(self, widget):
        """
        Removes currently selected item(s) of a widget
        
        Arguments:
            widget {QWidget} -- Qt widget to update. Supported:
                                QListWidget
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
        """
        if isinstance(widget, QListWidget):
            selected = self.getSelected(widget)
            for item in selected:
                self._removeListItem(widget, item)
        else:
            raise NotImplementedError(
                "removeSelectedValues not implemented for widget ", widget)

    def setCurrentByData(self, widget, data_current):
        """
        Set the current widget item by the provided widget data
        
        Arguments:
            widget {Qt widget} -- Qt widget to update. Supported:
                                  QComboBox, QListWidget
            data_current {immutable} -- Data to identify current item by
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
            AssertionError -- In case of illegitimate API calls (e.g. wrong
                              value types, missing dictionary keys, etc.)
        
        Returns:
            bool -- True if item found
        """
        assert not issubclass(type(data_current), MUTABLES), \
            "data_current should be an immutable object (e.g. str or int)"
        
        if isinstance(widget, QListWidget):
            return self._setListCurrentByData(widget, data_current)
        elif isinstance(widget, QComboBox):
            return self._setComboCurrentByData(widget, data_current)
        else:
            raise NotImplementedError(
                "setCurrent not implemented for widget ", widget)

    # getter

    def getValueList(self, widget):
        """
        Get list of current widget values
        
        Arguments:
            widget {QWidget} -- Qt widget to read. Supported:
                                QComboBox, QListWidget
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
        
        Returns:
            list -- List of tuples of the form (item_text, item_data)
        """
        if isinstance(widget, QComboBox):
            return self._getComboValues(widget)
        elif isinstance(widget, QListWidget):
            return self._getListValues(widget)
        else:
            raise NotImplementedError(
                "getValues not implemented for widget ", widget)

    def getCurrentData(self, widget):
        """
        Get list of current widget data properties
        
        Arguments:
            widget {QWidget} -- Qt widget to read. Supported:
                                QComboBox, QListWidget
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
        
        Returns:
            list -- List of data properties (immutables, e.g. str or int)
        """
        if isinstance(widget, QComboBox):
            return self._getComboCurrentData(widget)
        elif isinstance(widget, QListWidget):
            return self._getListCurrentData(widget)
        else:
            raise NotImplementedError(
                "getCurrent not implemented for widget ", widget)

    def getSelected(self, widget):
        """
        Get list of selected widget items
        
        Arguments:
            widget {QWidget} -- Qt widget to read. Supported:
                                QListWidget
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
        
        Returns:
            list -- List of QWidgets corresponding to the current widget items
        """
        if isinstance(widget, QListWidget):
            return widget.selectedItems()
        else:
            raise NotImplementedError(
                "getSelected not implemented for widget ", widget)

    # WIDGETS WITH VALUE BOUNDARIES:

    def setMinValue(self, widget, value):
        """
        Set lower boundary of widget
        
        Arguments:
            widget {Qt widget} -- Qt widget to update. Supported:
                                  QSpinBox, QDoubleSpinBox, QDateEdit
            value {int,float} -- Number to set lower boundary to.
                                 In case of QDateEdit:
                                 - value should be valid unix time in secs
                                   since epoch
        
        Raises:
            NotImplementedError -- In case of an unimplemented widget
        
        Returns:
            object -- Setter return value
        """
        try:
            assert isinstance(value, (int, float)), \
                "value should be an int or float"
        except AssertionError as error:
            error.args += ("Widget: ", widget)
            raise

        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.setMinimum(value)
        elif isinstance(widget, QDateEdit):
            return self._setDateTimeMin(widget, value)
        else:
            raise NotImplementedError(
                "setMinValue not implemented for widget ", widget)

    def setMaxValue(self, widget, value):
        """
        Set upper boundary of widget

        Arguments:
            widget {Qt widget} -- Qt widget to update. Supported:
                                  QSpinBox, QDoubleSpinBox, QDateEdit
            value {int,float} -- Number to set upper boundary to.
                                 In case of QDateEdit:
                                 - value should be valid unix time in secs
                                   since epoch

        Raises:
            NotImplementedError -- In case of an unimplemented widget

        Returns:
            object -- Setter return value
        """
        try:
            assert isinstance(value, (int, float)), \
                "value should be an int or float"
        except AssertionError as error:
            error.args += ("Widget: ", widget)
            raise

        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.setMaximum(value)
        elif isinstance(widget, QDateEdit):
            return self._setDateTimeMax(widget, value)
        else:
            raise NotImplementedError(
                "setMaxValue not implemented for widget ", widget)

    # UTILITY

    def nameToWidget(self, name):
        """
        Gets widget corresponding to attribute name.

        Dot-separated attribute names are resolved automatically
        (e.g. "form.button" would resolve to self.parent.form.button)

        Arguments:
            name {str} -- Object name of widget

        Raises:
            NotImplementedError -- Should the widget not be found

        Returns:
            QWidget -- widget corresponding to attribute name
        """
        assert isinstance(name, STRINGTYPES), \
            "name should be a string type"
        try:
            return getNestedAttribute(self.parent, name)
        except AttributeError:
            raise NotImplementedError(
                "Widget not implemented: ", name)

    # PRIVATE
    ######################################################################

    # COMMON

    def _selectWidgetItem(self, widget, item):
        """
        Select widget item
        """
        widget.selectionModel().clearSelection()
        widget.setCurrentItem(item)
        item.setSelected(True)

    def _getWidgetItems(self, widget):
        """
        Get list of current widget items
        """
        return [widget.item(idx) for idx in range(widget.count())]

    def _checkItemTuples(self, values):
        """
        Check validity of item tuples
        """
        # values provided as tuples of (str: label, immutable: data)
        assert isinstance(values, LISTTYPES), \
            "values should be provided as a list/tuple of tuples"
        # lazy check for first tuple. should catch most type errors:
        assert(len(values) == 0 or
               (len(values[0]) == 2 and
                isinstance(values[0][0], STRINGTYPES) and
                not issubclass(type(values[0][1]), MUTABLES))
               ), \
            "expected tuple types: (str: label, immutable (e.g. str): data"
        return True

    # WIDGET-SPECIFIC METHODS

    # QDateTimeEdit (dateedit)

    # setter

    def _createDateTimeFromUnix(self, unixtime):
        """
        Create QDateTime object and set it to unix time in secs
        """
        qdatetime = QDateTime()
        qdatetime.setTime_t(unixtime)
        return qdatetime

    def _setDateTime(self, qdatetimeedit, curtime):
        """
        Update date & time of QDateTimeEdit from unix time in secs
        """
        return qdatetimeedit.setDateTime(self._createDateTimeFromUnix(curtime))

    def _setDateTimeMin(self, qdatetimeedit, mintime):
        """
        Update min date & time of QDateTimeEdit from unix time in secs
        """
        return qdatetimeedit.setMinimumDateTime(
            self._createDateTimeFromUnix(mintime))

    def _setDateTimeMax(self, qdatetimeedit, maxtime):
        """
        Update max date & time of QDateTimeEdit from unix time in secs
        """
        return qdatetimeedit.setMaximumDateTime(
            self._createDateTimeFromUnix(maxtime))

    # getter

    def _getDateTime(self, qdatetimeedit):
        """
        Get current unix time from QDateTimeEdit
        """
        qdatetime = qdatetimeedit.dateTime()
        # Qt4 does not support toSecsSinceEpoch
        timestamp = int(round(qdatetime.toMSecsSinceEpoch() / 1000))
        return timestamp

    # QComboBox

    # setter

    def _addComboValues(self, combo_widget, item_tuples,
                        current_data=None, clear=False):
        """
        Add combo items by list of (item_text, item_data) tuples
        """
        if clear:
            combo_widget.clear()

        idx = 0
        cur_idx = None
        for text, data in item_tuples:
            combo_widget.addItem(text, data)
            if current_data is not None and data == current_data:
                cur_idx = idx
            idx += 1

        if cur_idx:
            combo_widget.setCurrentIndex(cur_idx)

    def _removeComboValues(self, combo_widget, item_tuples):
        """
        Remove items by list of (item_text, item_data) tuples
        """
        return self._removeComboItemsByData([item[1] for item in item_tuples])

    def _removeComboItemsByData(self, combo_widget, data_to_remove):
        """
        Remove items by list of item_data
        """
        for idx in range(combo_widget.count()):
            data = combo_widget.itemData(idx, Qt.UserRole)
            if data in data_to_remove:
                self._removeComboItemByIndex(idx)

    def _removeComboItemByIndex(self, combo_widget, index):
        """
        Remove item by model index (int)
        """
        return combo_widget.removeItem(index)

    def _setComboCurrentIndex(self, combo_widget, index):
        """
        Set current item by model index (int)
        """
        return combo_widget.setCurrentIndex(index)

    def _setComboCurrentByData(self, combo_widget, item_data):
        """
        Set current item by item_dta
        """
        index = combo_widget.findData(item_data)
        if index == -1:  # not found
            return False
        self._setComboCurrentIndex(combo_widget, index)
        return True

    # getter

    def _getComboValues(self, combo_widget):
        """
        Get list of current (item_text, item_data) tuples
        """
        result_list = []
        for idx in range(combo_widget.count()):
            text = combo_widget.itemText(idx)
            data = combo_widget.itemData(idx, Qt.UserRole)
            result_list.append((text, data))
        return result_list

    def _getComboData(self, combo_widget):
        """
        Get list of item_data values
        """
        return [item[1] for item in self._getComboValues(combo_widget)]

    def _getComboCurrentIndex(self, combo_widget):
        """
        Get model index of current item (int)
        """
        return combo_widget.currentIndex()

    def _getComboCurrentValue(self, combo_widget):
        """
        Get current (item_text, item_data) tuple
        """
        index = self._getComboCurrentIndex(combo_widget)
        text = combo_widget.currentText()
        data = combo_widget.itemData(index, Qt.UserRole)
        return (text, data)

    def _getComboCurrentData(self, combo_widget):
        """
        Get item_data of current item
        """
        return self._getComboCurrentValue(combo_widget)[1]

    # QListWidget

    # setter

    def _addListValues(self, list_widget, item_tuples,
                       current_data=None, clear=False):
        """
        Add list items by list of (item_text, item_data) tuples
        """
        if clear:
            list_widget.clear()

        for text, data in item_tuples:
            new_item = QListWidgetItem(text)
            if data:
                new_item.setData(Qt.UserRole, data)
            list_widget.addItem(new_item)
            if current_data is not None and data == current_data:
                self._selectWidgetItem(list_widget, new_item)

    def _removeListValues(self, list_widget, item_tuples):
        """
        Remove items by list of (item_text, item_data) tuples
        """
        return self._removeListItemsByData([item[1] for item in item_tuples])

    def _removeListItemsByData(self, list_widget, data_to_remove):
        """
        Remove items by list of item_data
        """
        for idx in range(list_widget.count()):
            item = list_widget.item(idx)
            data = item.data(Qt.UserRole)
            if data in data_to_remove:
                self._removeListItem(list_widget, item)

    def _removeListItem(self, list_widget, item):
        """
        Remove QListWidgetItem from list widget
        """
        list_widget.takeItem(list_widget.row(item))
        # takeItem does not delete the QListWidgetItem:
        del(item)

    def _setListCurrentByData(self, list_widget, item_data):
        """
        Set current item by item_dta
        """
        for item in self._getWidgetItems(list_widget):
            data = item.data(Qt.UserRole)
            if data == item_data:
                self._selectWidgetItem(list_widget, item)
                return True
        return False

    # getter

    def _getListValues(self, list_widget):
        """
        Get list of current (item_text, item_data) tuples
        """
        result_list = []
        for item in self._getWidgetItems(list_widget):
            data = item.data(Qt.UserRole)
            text = item.text()
            result_list.append((text, data))
        return result_list

    def _getListData(self, list_widget):
        """
        Get list of item_data values
        """
        return [item[1] for item in self._getListValues(list_widget)]

    def _getListCurrentIndex(self, list_widget):
        """
        Get model index of current item {int}
        """
        return list_widget.currentRow()

    def _getListCurrentItem(self, list_widget):
        """
        Get current QListWidgetItem
        """
        return list_widget.currentItem()

    def _getListCurrentValue(self, list_widget):
        """
        Get current (item_text, item_data) tuple
        """
        item = self._getListCurrentItem(list_widget)
        text = item.text()
        data = item.data(Qt.UserRole)
        return (text, data)

    def _getListCurrentData(self, list_widget):
        """
        Get item_data of current item
        """
        return self._getListCurrentValue()[1]

    # QFontComboBox

    # setter

    def _setFontComboCurrent(self, font_widget, font_dict):
        """
        Set font combo state from dictionary of font properties
        
        Arguments:
            font_widget {QFontComboBox} -- Font combo box to update
            font_dict {dict} -- Dictionary of font properties. Keys:
                family {str} -- Font family [required]
                size {int} -- Font size in pt [optional]
                bold {bool} -- Bold state [optional]
                italic {bool} -- Italics state [optional]

        """
        family = font_dict.get("family", None)
        size = font_dict.get("size", None)
        bold = font.setBold(font_dict["bold"])
        italic = font_dict.get("italic", None)

        assert family is not None and isinstance(family, STRINGTYPES), \
            "font family needs to be provided as a string type"
        font = Qfont(font_dict["family"])

        if size is not None:
            assert isinstance(size, (int, float))
            font.setPointSize(size)
        if bold is not None:
            assert isinstance(bold, bool)
            font.setBold(bold)
        if italic is not None:
            assert isinstance(italic, bool)
            font.setItalic(italic)

        return font_widget.setCurrentFont(font)

    # getter

    def _getFontComboCurrent(self, font_widget):
        """
        Set font combo state as dictionary of font properties
        
        Arguments:
            font_widget {QFontComboBox} -- Font combo box to update
        
        Returns:
            dict -- Dictionary of font properties. Keys:
                family {str} -- Font family [required]
                size {int} -- Font size in pt [optional]
                bold {bool} -- Bold state [optional]
                italic {bool} -- Italics state [optional]
        """
        font_dict = {
            "family": font_widget.family(),
            "size": font_widget.pointSize(),
            "bold": font_widget.bold(),
            "italic": font_widget.italic()
        }
        return font_dict
