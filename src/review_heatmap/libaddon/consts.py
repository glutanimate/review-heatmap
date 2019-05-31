# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2019  Aristotelis P. <https//glutanimate.com/>
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
Package-wide constants

In addition to defining a number of constants specific to libaddon, this
module also provides access to all constants in the parent add-on
(if any). Add-on specific constants take precedence and overwrite
constants in this module.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__all__ = ["ADDON_NAME", "ADDON_ID", "ADDON_VERSION", "LICENSE",
           "LIBRARIES", "AUTHORS", "CONTRIBUTORS", "SPONSORS",
           "MAIL_AUTHOR", "LINKS"]

# ADD-ON SPECIFIC CONSTANTS

# Define placeholders, in case add-on specific consts are incomplete

ADDON_NAME = "Glutanimate's add-on"
ADDON_ID = "0000000000"
ADDON_VERSION = "0.1.0"
LICENSE = "GNU AGPLv3"
LIBRARIES = ()
AUTHORS = (
    {"name": "Aristotelis P. (Glutanimate)", "years": "2018",
     "contact": "https://glutanimate.com"}
)  # main developers
CONTRIBUTORS = SPONSORS = MEMBERS_CREDITED = MEMBERS_TOP = ()
QRC_PREFIX = "libaddon"

# Merge in add-on specific consts:

# FIXME: find a less hacky solution
try:
    from ..consts import *  # noqa: F401
except ImportError:
    pass
try:
    from ..gui.resources import QRC_PREFIX  # noqa: F401
except ImportError:
    pass
try:
    from ..data.patrons import *  # noqa: F401
except ImportError:
    pass
try:
    from ..consts import LINKS as ADDON_LINKS  # noqa: F401
except ImportError:
    pass

# ADD-ON AGNOSTIC CONSTANTS

# Social

_mail_author_snippets = ["ankiglutanimate", "ατ", "gmail.com"]  # anti-spam
MAIL_AUTHOR = "".join(_mail_author_snippets).replace("ατ", "@")
LINKS = {
    "patreon": "https://www.patreon.com/glutanimate",
    "bepatron": "https://www.patreon.com/bePatron?u=7522179",
    "coffee": "http://ko-fi.com/glutanimate",
    "description": "https://ankiweb.net/shared/info/{}".format(ADDON_ID),
    "rate": "https://ankiweb.net/shared/review/{}".format(ADDON_ID),
    "twitter": "https://twitter.com/glutanimate",
    "youtube": "https://www.youtube.com/c/glutanimate"
}
LINKS.update(ADDON_LINKS)
