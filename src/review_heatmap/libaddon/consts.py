# -*- coding: utf-8 -*-

"""
Global constants

In addition to defining a number of constants specific to libaddon, this
module also provides access to all constants in the parent add-on
(if any). Add-on specific constants take precedence and overwrite
constants in this module.

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
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
    {"name": "Aristotelis P. (Glutanimate)", "years": "2018",
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
    "coffee": "https://www.buymeacoffee.com/glutanimate",
    "description": "https://ankiweb.net/shared/info/{}".format(ADDON_ID),
    "rate": "https://ankiweb.net/shared/review/{}".format(ADDON_ID),
    "twitter": "https://twitter.com/glutanimate",
    "youtube": "https://www.youtube.com/c/glutanimate"
}
LINKS.update(ADDON_LINKS)

# Credits

# https://www.patreon.com/glutanimate
PATRONS = ("Alex M", "Devin Beecher", "Edan Maor", "Itai Efrat",
           "Jørgen Rahbek", "Man Duong", "Nicolas Curi", "PapelMagico",
           "Paul McManus", "Peter Benisch", "Rob Alexander", "Scott Barnett",
           "Sebastián Ortega", "Shawn Lesniak",
           "spiraldancing", "Steven Nevers")
PATRONS_TOP = ("Paul Bake", "Blacky 372")
