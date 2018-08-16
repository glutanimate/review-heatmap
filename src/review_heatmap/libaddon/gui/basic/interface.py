# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from .widgets.qt import *
# TODO: Switch to QKeySequenceEdit once Qt4 support dropped
from .widgets.qkeygrabber import QKeyGrabButton
from .widgets.qcolorbutton import QColorButton


class CommonWidgetInterface(object):

    # WIDGET-AGNOSTIC METHODS

    # API

    def setValue(self, widget, value):
        """
        The modified properties try to mirror the most common use
        case (e.g. items for list widget, current item for combo box).

        For more fine-grained control use the other methods in this API.

        Arguments:
            widget {[type]} -- [description]
            value {[type]} -- [description]

        Raises:
            NotImplementedError -- [description]
        """
        if isinstance(widget, (QCheckBox, QRadioButton)):
            widget.setChecked(value)
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value)
        elif isinstance(widget, QComboBox):
            self._setComboCurrent(widget, value)
        elif isinstance(widget, QListWidget):
            self._addListValues(widget, value, clear=True)
        elif isinstance(widget, QDateEdit):
            self._setDateTime(widget, value)
        elif isinstance(widget, (QLineEdit, QLabel, QPushButton,
                                 QKeyGrabButton)):
            widget.setText(value)
        elif isinstance(widget, QTextEdit):
            widget.setHtml(value)
        elif isinstance(widget, QPlainTextEdit):
            widget.setPlainText(value)
        elif isinstance(widget, QFontComboBox):
            self._setFontComboCurrent(value)
        elif isinstance(widget, QColorButton):
            widget.setColor(color)
        else:
            raise NotImplementedError(
                "setValue not implemented for widget ", widget)

    def getValue(self, widget):
        """
        The returned properties try to mirror the most common use
        case (e.g. items for list widget, current item for combo box).

        For more fine-grained control use the other methods in this API.

        Arguments:
            widget {[type]} -- [description]
            value {[type]} -- [description]

        Raises:
            NotImplementedError -- [description]
        """

        if isinstance(widget, (QCheckBox, QRadioButton)):
            return widget.isChecked(current)
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return self._getComboCurrent(widget)
        elif isinstance(widget, QListWidget):
            return self._getListValues(widget)
        elif isinstance(widget, QDateEdit):
            return self._getDateTime(widget)
        elif isinstance(widget, (QLineEdit, QLabel, QPushButton,
                                 QKeyGrabButton)):
            return widget.text()
        elif isinstance(widget, QTextEdit):
            return widget.toHtml()
        elif isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, QFontComboBox):
            return self._getFontComboCurrent(value)
        elif isinstance(widget, QColorButton):
            return widget.color()
        else:
            raise NotImplementedError(
                "getValue not implemented for widget ", widget)

    # Widgets with multiple items to choose from:

    def setValues(self, widget, values):
        if isinstance(widget, QComboBox):
            return self._addComboValues(widget, values, clear=True)
        elif isinstance(widget, QListWidget):
            return self._addComboValues(widget, values, clear=True)
        else:
            raise NotImplementedError(
                "setValues not implemented for widget ", widget)

    def getValues(self, widget):
        if isinstance(widget, QComboBox):
            return self._getComboValues(widget)
        elif isinstance(widget, QListWidget):
            return self._getListValues(widget)
        else:
            raise NotImplementedError(
                "getValues not implemented for widget ", widget)

    def addValues(self, widget, values):
        if isinstance(widget, QComboBox):
            self._addComboValues(widget, values, clear=False)
        elif isinstance(widget, QListWidget):
            self._addListValues(widget, values, clear=False)
        else:
            raise NotImplementedError(
                "addValue not implemented for widget ", widget)

    def removeValues(self, widget, values):
        if isinstance(widget, QComboBox):
            self._removeComboValues(widget, values)
        elif isinstance(widget, QListWidget):
            self._removeListValues(widget, values)
        else:
            raise NotImplementedError(
                "removeValues not implemented for widget ", widget)

    def setValuesAndCurrent(self, widget, values, current):
        if isinstance(widget, QComboBox):
            self._addComboValues(widget, values, cur=current, clear=True)
        elif isinstance(widget, QListWidget):
            self._addListValues(widget, values, cur=current, clear=True)
        else:
            raise NotImplementedError(
                "setValuesAndCurrent not implemented for widget ", widget)

    def setCurrent(self, widget, value):
        if isinstance(widget, QListWidget):
            self._setListCurrent(widget, value)
        elif isinstance(widget, QComboBox):
            self._setComboCurrent(widget, value)
        else:
            raise NotImplementedError(
                "setCurrent not implemented for widget ", widget)

    def getCurrent(self, widget):
        if isinstance(widget, QComboBox):
            return self._getComboCurrent(widget)
        elif isinstance(widget, QListWidget):
            return self._getListCurrent(widget)
        else:
            raise NotImplementedError(
                "getCurrent not implemented for widget ", widget)

    def getSelected(self, widget):
        if isinstance(widget, QListWidget):
            return widget.selectedItems()
        else:
            raise NotImplementedError(
                "getSelected not implemented for widget ", widget)

    # Widgets with value boundaries:

    def setMinValue(self, widget, value):
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setMinimum(value)
        elif isinstance(widget, QDateEdit):
            self._setDateTimeMin(widget, value)
        else:
            raise NotImplementedError(
                "setMinValue not implemented for widget ", widget)

    def setMaxValue(self, widget, value):
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setMaximum(value)
        elif isinstance(widget, QDateEdit):
            self._setDateTimeMax(widget, value)
        else:
            raise NotImplementedError(
                "setMaxValue not implemented for widget ", widget)

    # PRIVATE

    def _selectWidgetItem(self, widget, item):
        widget.selectionModel().clearSelection()
        widget.setCurrentItem(item)

    def _getWidgetItems(self, widget):
        return [widget.item(idx) for idx in range(list_widget.count())]

    # WIDGET-SPECIFIC METHODS

    # QDateTimeEdit (dateedit)

    def _createDateTimeFromUnix(self, unixtime):
        qdatetime = QDateTime()
        qdatetime.setTime_t(unixtime)
        return qdatetime

    def _setDateTime(self, qdatetimeedit, curtime):
        qdatetimeedit.setDateTime(self._createDateTimeFromUnix(curtime))

    def _setDateTimeMin(self, qdatetimeedit, mintime):
        qdatetimeedit.setMinimumDateTime(self._createDateTimeFromUnix(mintime))

    def _setDateTimeMax(self, qdatetimeedit, maxtime):
        qdatetimeedit.setMaximumDateTime(self._createDateTimeFromUnix(maxtime))

    def _getDateTime(self, qdatetimeedit):
        qdatetime = widget.dateTime()
        # Qt4 does not support toSecsSinceEpoch
        return qdatetime.toMSecsSinceEpoch() // 1000

    # QComboBox

    def _setComboCurrent(self, combo_widget, item_tuple):
        for idx in range(combo_widget.count()):
            data = combo_widget.itemData(idx, Qt.UserRole)
            text = combo_widget.itemText(idx)
            if (data, text) == item_tuple:
                self._selectWidgetItem(list_widget, item)
                return True
        return False

    def _getComboCurrent(self, combo_widget):
        cur_idx = combo_widget.currentIndex()
        cur_text = combo_widget.currentText()
        cur_data = combo_widget.itemData(cur_idx, Qt.UserRole)
        return (cur_idx, cur_text, cur_data)

    def _addComboValues(self, combo_widget, item_tuples, cur=None, clear=False):
        if clear:
            combo_widget.clear()

        idx = 0
        cur_idx = None
        for text, data in item_tuples:
            combo_widget.addItem(text, data)
            if cur and ((data and data == cur) or (text and text == cur)):
                cur_idx = idx
            idx += 1

        if cur_idx:
            combo_widget.setCurrentIndex(cur_idx)

    def _removeComboValues(self, combo_widget, item_tuples):
        for idx in range(combo_widget.count()):
            data = combo_widget.itemData(idx, Qt.UserRole)
            text = combo_widget.itemText(idx)
            if (data, text) in item_tuples:
                combo_widget.removeItem(idx)

    def _getComboValues(self, combo_widget):
        item_tuples = []
        for idx in range(combo_widget.count()):
            data = combo_widget.itemData(idx, Qt.UserRole)
            text = combo_widget.itemText(idx)
            item_tuples.append((data, text))
        return item_tuples

    # QListWidget

    def _addListValues(self, list_widget, item_tuples, cur=None, clear=False):
        if clear:
            list_widget.clear()

        for text, data in item_tuples:
            new_item = QListWidgetItem(text)
            if data:
                new_item.setData(Qt.UserRole, data)
            if cur and ((data and data == cur) or (text and text == cur)):
                self._selectWidgetItem(list_widget, new_item)
            list_widget.addItem(new_item)

    def _removeListValues(self, list_widget, item_tuples):
        for idx in range(list_widget.count()):
            item = list_widget.item(idx)
            data = item.data(Qt.UserRole)
            text = item.text()
            if (data, text) in item_tuples:
                list_widget.takeItem(list_widget.row(item))
                # takeItem does not delete the QListWidgetItem:
                del(item)

    def _getListValues(self, list_widget):
        item_tuples = []
        for item in self._getWidgetItems(list_widget):
            data = item.data(Qt.UserRole)
            text = item.text()
            item_tuples.append((data, text))
        return item_tuples

    def _setListCurrent(self, list_widget, item_tuple):
        for item in self._getWidgetItems(list_widget):
            data = item.data(Qt.UserRole)
            text = item.text()
            if (data, text) == item_tuple:
                self._selectWidgetItem(list_widget, item)
                return True
        return False

    def _getListCurrent(self, list_widget):
        cur_idx = list_widget.currentRow()
        cur_item = list_widget.currentItem()
        cur_text = cur_item.text()
        cur_data = cur_item.data(Qt.UserRole)
        return (cur_idx, cur_text, cur_data)

    # QFontComboBox

    def _setFontComboCurrent(self, font_widget, font_dict):
        font = Qfont(font_dict["family"])
        if font_dict.get("size", None) is not None:
            font.setPointSize(font_dict["size"])
        if font_dict.get("bold", None) is not None:
            font.setBold(font_dict["bold"])
        if font_dict.get("italic", None) is not None:
            font.setItalic(font_dict["italic"])

    def _getFontComboCurrent(self, font_widget):
        font_dict = {
            "family": font_widget.family(),
            "size": font_widget.pointSize(),
            "bold": font_widget.bold(),
            "italic": font_widget.italic()
        }
        return font_dict


INTERFACE_API_BY_KEY = {
    "value": (CommonWidgetInterface.setValue,
              CommonWidgetInterface.getValue),
    "items": (CommonWidgetInterface.setValues,
              CommonWidgetInterface.getValues),
    "current": (CommonWidgetInterface.setCurrent,
                CommonWidgetInterface.getCurrent),
    "min": (CommonWidgetInterface.setMinValue,
            None),
    "max": (CommonWidgetInterface.setMaxValue,
            None),
}
