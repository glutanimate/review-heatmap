# -*- coding: utf-8 -*-

"""
Add-on agnostic constants

Also tries to import parent-level consts file to supply
add-on-specific constants to modules of this package.

Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals


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
)
CONTRIBUTORS = ()

# Merge in add-on specific consts:

try:
    from ..consts import (ADDON_NAME, ADDON_ID, ADDON_VERSION,  # noqa: F401
                          ADDON_HELP, LICENSE, LIBRARIES,
                          AUTHORS, CONTRIBUTORS)
except ImportError:
    pass


# ADD-ON AGNOSTIC CONSTANTS

# Social

_mail_author_snippets = ["ankiglutanimate", "ατ", "gmail.com"]  # anti-spam
MAIL_AUTHOR = "".join(_mail_author_snippets).replace("ατ", "@")
LINK_PATREON = "https://www.patreon.com/glutanimate"
LINK_COFFEE = "https://www.buymeacoffee.com/glutanimate"
LINK_DESCRIPTION = "https://ankiweb.net/shared/info/{}".format(ADDON_ID)
LINK_RATE = "https://ankiweb.net/shared/review/{}".format(ADDON_ID)
LINK_TWITTER = "https://twitter.com/glutanimate"
LINK_YOUTUBE = "https://www.youtube.com/c/glutanimate"

# Credits

PATRONS = ("Blacky 372", "Sebastián Ortega",
           "spiraldancing", "Jørgen Rahbek",
           "Peter Benisch", "Edan Maor")
