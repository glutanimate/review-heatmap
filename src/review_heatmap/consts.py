# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki.

Global variables

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import sys
import os
from anki import version

from ._version import __version__

# PLATFORM

ANKI21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()
if ANKI21:
    ADDON_PATH = os.path.dirname(__file__)
else:
    ADDON_PATH = os.path.dirname(__file__).decode(SYS_ENCODING)

# ADD-ON

ADDON_NAME = "Review Heatmap"
ADDON_ID = "1771074083"
ADDON_VERSION = __version__
ADDON_HELP = "https://github.com/glutanimate/review-heatmap/wiki"
LICENSE = "GNU AGPLv3"
LIBRARIES = (
    {"name": "d3.js", "version": "v3.5.17",
        "author": "Mike Bostock", "license": "BSD license"},
    {"name": "cal-heatmap", "version": "v3.6.2",
        "author": "Wan Qi Chen", "license": "MIT license"},
)
AUTHORS = (
    {"name": "Aristotelis P. (Glutanimate)", "years": "2016-2018",
     "contact": "https://glutanimate.com"},
)  # trailing comma required for single-element tuples
CONTRIBUTORS = ("hehu80", )
