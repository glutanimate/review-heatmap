# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki.

Global variables

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import sys
import os
from anki import version

ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

if ANKI21:
    ADDON_PATH = os.path.dirname(__file__)
else:
    ADDON_PATH = os.path.dirname(__file__).decode(SYS_ENCODING)

ANKIWEB_ID = "1771074083"
LINK_PATREON = "https://www.patreon.com/glutanimate"
LINK_COFFEE = "https://www.buymeacoffee.com/glutanimate"
LINK_DESCRIPTION = "https://ankiweb.net/shared/info/{}".format(ANKIWEB_ID)
LINK_RATE = "https://ankiweb.net/shared/review/{}".format(ANKIWEB_ID)
LINK_TWITTER = "https://twitter.com/glutanimate"
LINK_YOUTUBE = "https://www.youtube.com/c/glutanimate"
LINK_HELP = "https://github.com/glutanimate/review-heatmap/wiki"
