# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Main Module. Initializes add-on components.

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .dialogs.options import initializeOptions
from .links import initializeLinks
from .views import initializeViews

initializeOptions()
initializeViews()
initializeLinks()
