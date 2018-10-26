# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018  Aristotelis P. <https//glutanimate.com/>
# Copyright (C) 2016  Jason R Coombs and other PyPA contributors
#                     <pypa-dev@googlegroups.com>
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
Components related to packaging third-party code and libraries
with Anki add-ons
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys
import os

from .platform import ANKI21

__all__ = [
    "addPathToModuleLookup",
    "addSubdirPathToModuleLookup"
]

# Resolving version-specific module imports
######################################################################

class VersionSpecificImporter:
    """
    A PEP 302 meta path importer for finding the right vendored package
    among bundled packages specific to Anki 2.1, 2.0, and packages common
    to both.

    Presupposes the following package structure:

    root_name
      - anki21
      - anki20
      - common
    
    Where either anki21, anki20, or common contain the packages/modules
    supplied in managed_imports.

    vendor_pkg may optionally be supplied in case the vendored packages are
    located under a different namespace than root_name.
    """

    module_dir = "anki21" if ANKI21 else "anki20"

    def __init__(self, root_name, managed_imports=(), vendor_pkg=None):
        self.root_name = root_name
        self.managed_imports = set(managed_imports)
        self.vendor_pkg = vendor_pkg or self.root_name

    @property
    def search_path(self):
        """
        Search version-specific vendor package, then common vendor package,
        then global package.
        """
        yield ".".join((self.vendor_pkg, self.module_dir, ""))
        yield ".".join((self.vendor_pkg, "common", ""))
        yield ''

    def find_module(self, fullname, path=None):
        """
        Return self when fullname starts with root_name and the
        target module is one vendored through this importer.
        """
        root, base, target = fullname.partition(self.root_name + '.')
        if root:
            return
        if not any(map(target.startswith, self.managed_imports)):
            return
        return self

    def load_module(self, fullname):
        """
        Iterate over the search path to locate and load fullname.
        """
        root, base, target = fullname.partition(self.root_name + '.')
        for prefix in self.search_path:
            try:
                extant = prefix + target
                __import__(extant)
                mod = sys.modules[extant]
                sys.modules[fullname] = mod
                # mysterious hack:
                # Remove the reference to the extant package/module
                # on later Python versions to cause relative imports
                # in the vendor package to resolve the same modules
                # as those going through this importer.
                if sys.version_info >= (3, ):
                    del sys.modules[extant]
                return mod
            except ImportError:
                pass
        else:
            raise ImportError(
                "The '{target}' package is required; "
                "normally this is bundled with this add-on so if you get "
                "this warning, consult the packager of your "
                "distribution.".format(**locals())
            )

    def install(self):
        """
        Install this importer into sys.meta_path if not already present.
        """
        if self not in sys.meta_path:
            sys.meta_path.append(self)


# Third-party add-on imports
######################################################################

def importAny(*modules):
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
    raise ImportError("Requires one of " + ', '.join(modules))



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

STRINGTYPES = (str,) if ANKI21 else (str, unicode)  # noqa: F821
LOOKUP_SUBDIRS = ["common", "anki21" if ANKI21 else "anki20"]

def _addPathToModuleLookup(path):
    # Insert at idx 0 in order to supersede system-wide packages
    sys.path.insert(0, path)

def addPathToModuleLookup(path):
    """
    Add modules shipped with the add-on to Python module search path
    
    Arguments:
        path {str,unicode} -- Fully qualified path to module directory
    """
    assert isinstance(path, STRINGTYPES)
    assert os.path.isdir(path)
    _addPathToModuleLookup(path)

def addSubdirPathToModuleLookup(path):
    """
    Recursively add module directory with version-specific subfolders
    to Python module search path

    Arguments:
        path {str,unicode} -- Fully qualified path to module directory with
                              one or more of the following subfolders:
                              python2, python3, common
    """
    assert isinstance(path, STRINGTYPES)
    assert os.path.isdir(path)
    # TODO: refactor
    for path in [os.path.join(path, subdir) for subdir in LOOKUP_SUBDIRS]:
        if not os.path.isdir(path):
            continue
        _addPathToModuleLookup(path)


# Installing binary dependencies (that are either part of a
# packaged module or standalone executables)
######################################################################

class BinaryInstaller(object):

    def __init__(self):
        raise NotImplementedError
