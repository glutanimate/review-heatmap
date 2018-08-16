# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from .qt import QPushButton, QColorDialog, QPixmap, QColor, QIcon, QSize

class QColorButton(QPushButton):
    def __init__(self, color="#000000", parent=None):
        super(QColorButton, self).__init__(parent=parent)
        self._updateButtonColor(color)
        self.clicked.connect(self._chooseColor)

    def _chooseColor(self):
        dialog = QColorDialog(self.color)
        color = dialog.getColor()
        if not color.isValid():
            return False
        color = color.name()
        self._updateButtonColor(color)

    def _updateButtonColor(self, color):
        """Generate color preview pixmap and place it on button"""
        pixmap = QPixmap(128, 18)
        qcolour = QColor(0, 0, 0)
        qcolour.setNamedColor(color)
        pixmap.fill(qcolour)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(128, 18))
        self.color = color
    
    def color(self):
        return self.color
    
    def setColor(self, color):
        self._updateButtonColor(color)
