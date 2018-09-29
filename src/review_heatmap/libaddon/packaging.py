# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys
import os

from .platform import PYTHON3
from .platform import ANKI21

__all__ = [
    "addPathToModuleLookup",
    "addSubdirPathToModuleLookup"
]

STRINGTYPES = (str,) if PYTHON3 else (str, unicode)  # noqa: F821
LOOKUP_SUBDIRS = ["common", "python3" if PYTHON3 else "python2"]

# Resolving version-specific module imports
######################################################################

def platformAwareImport(target_package, target_module, origin_module):
    # TODO: fix function-level import
    from stdlib import importlib  # not available at module import time
    package = origin_module.rsplit(".", 1)[0]

    components = [target_package, "anki21" if ANKI21 else "anki20",
                  target_module]
    relative_path = ".".join(components)

    return importlib.import_module(relative_path, package=package)


# Registering external libraries & modules
######################################################################

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
