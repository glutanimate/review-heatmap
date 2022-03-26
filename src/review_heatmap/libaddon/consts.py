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
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


def setAddonProperties(addon):
    """Update ADDON class properties from another ADDON class
    
    Arguments:
        addon {object} -- an ADDON class with properties stored as class
                          attributes
    """
    for key, value in addon.__dict__.items():
        if key.startswith("__") and key.endswith("__"):
            # ignore special attributes
            continue
        setattr(ADDON, key, value)

set_addon_properties = setAddonProperties

class ADDON(object):
    """Class storing general add-on properties
    Property names need to be all-uppercase with no leading underscores.
    Should be updated by add-on on initialization.
    """
    NAME = ""
    MODULE = ""
    REPO = ""
    ID = ""
    VERSION = ""
    LICENSE = ""
    AUTHORS = ()
    AUTHOR_MAIL = ""
    LIBRARIES = ()
    CONTRIBUTORS = ()
    SPONSORS = ()
    MEMBERS_CREDITED = ()
    MEMBERS_TOP = ()
    LINKS = {}
