# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki.

Global variables

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from ._version import __version__

__all__ = ["ADDON_NAME", "ADDON_ID", "ADDON_VERSION", "LINKS",
           "LICENSE", "LIBRARIES", "AUTHORS", "CONTRIBUTORS",
           "SPONSORS"]

# ADD-ON

ADDON_NAME = "Review Heatmap"
ADDON_ID = "1771074083"
ADDON_VERSION = __version__
LINKS = {
    "help": "https://github.com/glutanimate/review-heatmap/wiki"
}
LICENSE = "GNU AGPLv3"
LIBRARIES = (
    {"name": "d3.js", "version": "v3.5.17",
        "author": "Mike Bostock", "license": "BSD license",
        "url": "https://d3js.org/"},
    {"name": "cal-heatmap", "version": "v3.6.3-anki",
        "author": "Wan Qi Chen", "license": "MIT license",
        "url": "https://github.com/glutanimate/cal-heatmap"},
)
AUTHORS = (
    {"name": "Aristotelis P. (Glutanimate)", "years": "2016-2018",
     "contact": "https://glutanimate.com"},
)  # trailing comma required for single-element tuples
CONTRIBUTORS = ("David Bailey", "hehu80", "Rapptz")
SPONSORS = ()
