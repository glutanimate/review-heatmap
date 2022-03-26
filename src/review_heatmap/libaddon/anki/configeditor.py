# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
# Copyright (C) 2016-2019  Ankitects Pty Ltd and contributors
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
anki20 compat: Add-on configuration editor
"""

import aqt
from aqt.qt import *
from aqt.utils import tooltip

from anki.utils import json

from ..consts import ADDON
from .._vendor import markdown2
from ..platform import PATH_THIS_ADDON

from .dialog_htmlview import HTMLViewer

class ConfigEditor(QDialog):
    
    def __init__(self, config_manager, parent):
        super(ConfigEditor, self).__init__(parent=parent)
        self.mgr = config_manager
        self.form = aqt.forms.editaddon.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle("{} Configuration".format(ADDON.NAME))
        self.setupWidgets()
        self.updateText(self.mgr["local"])
        self.exec()
    
    def setupWidgets(self):
        button_box = self.form.buttonBox
        restore_btn = button_box.addButton(QDialogButtonBox.RestoreDefaults)
        help_btn = button_box.addButton(QDialogButtonBox.Help)
        help_btn.clicked.connect(self.onHelpRequested)
        restore_btn.clicked.connect(self.onRestoreDefaults)
    
    def updateText(self, conf):
        self.form.text.setPlainText(
            json.dumps(conf, ensure_ascii=False, sort_keys=True,
                       indent=4, separators=(',', ': ')))
    
    def onRestoreDefaults(self):
        default_conf = self.mgr.defaults["local"]
        self.updateText(default_conf)
        tooltip("Restored defaults", parent=self)
        
    def onHelpRequested(self):
        docs_path = os.path.join(PATH_THIS_ADDON, "config.md")
        if not os.path.exists(docs_path):
            return False
        with open(docs_path, "r") as f:
            html = markdown2.markdown(f.read())
        dialog = HTMLViewer(html, title="{} Configuration Help".format(
            ADDON.NAME), parent=self)
        dialog.show()
    
    def accept(self):
        txt = self.form.text.toPlainText()
        try:
            new_conf = json.loads(txt)
        except ValueError as e:
            showInfo("Invalid configuration, restoring previous config: " +
                     repr(e))
            return
        if not isinstance(new_conf, dict):
            showInfo("Invalid configuration, restoring previous config: "
                     "top level object must be a map")
            return

        self.mgr["local"] = new_conf
        self.mgr.save(storage_name="local")
        super(ConfigEditor, self).accept()
