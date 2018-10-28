# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018  Aristotelis P. <https//glutanimate.com/>
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
           "MAIL_AUTHOR", "LINKS", "PATRONS", "PATRONS_TOP"]

# ADD-ON SPECIFIC CONSTANTS

# Define placeholders, in case add-on specific consts are incomplete

ADDON_NAME = "Glutanimate's add-on"
ADDON_ID = "0000000000"
ADDON_VERSION = "0.1.0"
LICENSE = "GNU AGPLv3"
LIBRARIES = ()
AUTHORS = (
    {"name": "Aristotelis P. <https//glutanimate.com/>", "years": "2018",
     "contact": "https://glutanimate.com"},
)  # main developers
CONTRIBUTORS = ()  # single code contributions
SPONSORS = ()  # sponsors / development commissions

# Merge in add-on specific consts:

try:
    from ..consts import *  # noqa: F401
    from ..consts import LINKS as ADDON_LINKS
except ImportError:
    pass

# ADD-ON AGNOSTIC CONSTANTS

# Social

_mail_author_snippets = ["ankiglutanimate", "ατ", "gmail.com"]  # anti-spam
MAIL_AUTHOR = "".join(_mail_author_snippets).replace("ατ", "@")
LINKS = {
    "patreon": "https://www.patreon.com/glutanimate",
    "coffee": "http://ko-fi.com/glutanimate",
    "description": "https://ankiweb.net/shared/info/{}".format(ADDON_ID),
    "rate": "https://ankiweb.net/shared/review/{}".format(ADDON_ID),
    "twitter": "https://twitter.com/glutanimate",
    "youtube": "https://www.youtube.com/c/glutanimate"
}
LINKS.update(ADDON_LINKS)

# Credits

# https://www.patreon.com/glutanimate
# automatically sorted:
PATRONS = ("Alex M", "Devin Beecher", "Edan Maor", "Itai Efrat",
           "Jørgen Rahbek", "Man Duong", "Nicolas Curi", "PapelMagico",
           "Paul McManus", "Peter Benisch", "Rob Alexander", "Scott Barnett",
           "Sebastián Ortega", "Shawn Lesniak", "spiraldancing",
           "Steven Nevers", "Henrik Giesel", "JessC",
           "Yuniesky Echemendia", "Andrew", "Michael Song", "Farhan Ahmad")
PATRONS_TOP = ("Paul Bake", "Blacky 372", "Fin Thiessen", "The Academy")
