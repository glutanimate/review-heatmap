# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from ...libaddon.platform import ANKI21

if ANKI21:
    from .anki21 import *
else:
    from .anki20 import *

