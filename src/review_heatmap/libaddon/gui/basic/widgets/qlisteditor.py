# -*- coding: utf-8 -*-

"""
TODO: complete

Icons: plus.svg, minus.svg

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from .qt import *

from ....utils.platform import MODULE_ADDON

class QListEditor(QGroupBox):

    def __init__(self, *args, **kwargs):
        super(QListEditor, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignHCenter)
        self._setupWidgets()

    def _setupWidgets(self):
        hlayout = QHBoxLayout(self)
        vlayout = QVBoxLayout(self)

        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for name, icon in (("btnAdd", "plus"), ("btnRem", "minus")):
            setattr(self, name, QToolButton(self))
            btn = getattr(self, name)
            btn.setMinimumSize(QSize(32, 0))
            iconAdd = QIcon()
            iconAdd.addPixmap(QPixmap(":/{}/icons/{}.svg".format(
                MODULE_ADDON, icon)), QIcon.Normal, QIcon.Off)
            btn.setIcon(iconAdd)
            btn.setIconSize(QtCore.QSize(16, 16))

        spacer = QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        hlayout.addWidget(self.list)
        vlayout.addWidget(self.btnAdd)
        vlayout.addWidget(self.btnRem)
        vlayout.addItem(spacer)
        hlayout.addLayout(vlayout)
