# -*- coding: utf-8 -*-

"""
Generic options dialog for Anki add-ons

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt.qt import Qt

from aqt.utils import openLink

from ..consts import LINKS
from ..platform import PLATFORM

from .basic.dialog_mapped import MappedDialog
from .about import get_about_string
from .labelformatter import formatLabels

class OptionsDialog(MappedDialog):

    def __init__(self, mapped_widgets, config, form_module=None,
                 parent=None, **kwargs):
        """
        Creates an options dialog with the provided Qt form and populates its
        widgets from a ConfigManager config object.

        Arguments:
            mapped_widgets {sequence} -- A list or tuple of mappings between
                                         widget names, config value names, and
                                         special methods to act as mediators
                                         (see MappedDialog docstring for specs)
            config {ConfigManager} -- ConfigManager object providing access to
                                      add-on config values

        Keyword Arguments:
            form_module {PyQt form module} -- Dialog form module generated
                                              through pyuic (default: {None})
            parent {QWidget} -- Parent Qt widget (default: {None})


        """
        # Mediator methods defined in mapped_widgets might need access to
        # certain instance attributes. As super().__init__ instantiates
        # all widget values it is important that we set these attributes
        # beforehand:
        self.config = config
        super(OptionsDialog, self).__init__(
            mapped_widgets, self.config.all, self.config.defaults,
            form_module=form_module, parent=parent)
        # Instance methods that modify the initialized UI should either be
        # called from self._setupUI or from here
    
    # Static widget setup

    def _setupUI(self):
        formatLabels(self)
        self._setupAbout()
        if PLATFORM == "mac":
            # Decrease tab margins on macOS
            tab_widget = getattr(self.form, "tabWidget", None)
            if not tab_widget:
                return
            for idx in range(tab_widget.count()):
                tab = tab_widget.widget(idx)
                layout = tab.layout()
                layout.setContentsMargins(3, 3, 3, 3)

    def _setupAbout(self):
        """
        Fill out 'about' widget
        """
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

    def _setupEvents(self):
        super(OptionsDialog, self)._setupEvents()
        for name, link in LINKS.items():
            btn_widget = getattr(self.form, "btn" + name.capitalize(), None)
            if not btn_widget:
                continue
            btn_widget.clicked.connect(lambda _, link=link: openLink(link))

    def _onAccept(self):
        """Executed only if dialog confirmed"""
        self.getData()  # updates self.config in place
        self.config.save()
        super(OptionsDialog, self)._onAccept()
