# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2018  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the accompanied license file.
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
# terms and conditions of the GNU Affero General Public License which
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Addon-wide constants
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
    {"name": "Aristotelis P. <https//glutanimate.com/>", "years": "2016-2018",
     "contact": "https://glutanimate.com"},
)  # trailing comma required for single-element tuples
# automatically sorted:
CONTRIBUTORS = ("David Bailey", "hehu80", "Rapptz")
SPONSORS = ()
