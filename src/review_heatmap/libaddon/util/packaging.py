# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2020  Aristotelis P. <https//glutanimate.com/>
# Copyright (C) 2016  Jason R Coombs and other PyPA contributors
#                     <pypa-dev@googlegroups.com>
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
Components related to packaging third-party code and libraries
with Anki add-ons
"""

import os
import sys

from types import ModuleType

from typing import Optional


__all__ = ["importAny", "addPathToModuleLookup"]

# Third-party add-on imports
######################################################################


def importAny(*modules: str) -> Optional[ModuleType]:
    """
    Import by name, providing multiple alternative names

    Common use case: Support all the different package names found
    between 2.0 add-ons, 2.1 AnkiWeb releases, and 2.1 dev releases

    Raises:
        ImportError -- Module not found

    Returns:
        module -- Imported python module
    """
    for mod in modules:
        try:
            return __import__(mod)
        except ImportError:
            pass
    raise ImportError("Requires one of " + ", ".join(modules))


# Registering external libraries & modules
######################################################################

# NOTE: Use of these is discouraged and should be reserved for cases where
#       traditional vendoring fails or is not feasible to implement.

# NOTE: I have yet to find a reliable way to add modules to packages
# that *do* ship with Anki, but are missing specific sub-modules
# (e.g. 'version' module of 'distutils')
#
# The issue mainly arises when Anki has already loaded the corresponding
# module at add-on init time. At that point it becomes non-trivial to
# update the module cache with our own version of the module.
#
# It is easy to make due with explicitly importing our own version of
# the module if we have control over the code-base, but in case of
# dependencies of other modules this becomes a major problem
# (e.g. third-party packages depending on stdlib modules missing
# in Anki's Python distribution).


def addPathToModuleLookup(path: str) -> None:
    """
    Add modules shipped with the add-on to Python module search path

    Arguments:
        path {str,unicode} -- Fully qualified path to module directory
    """
    assert os.path.isdir(path)
    # Insert at idx 0 in order to supersede system-wide packages
    sys.path.insert(0, path)
