"""
Package for common reusable modules that can be
deployed across multiple add-ons.
"""

from __future__ import unicode_literals

import sys
import os

from .utils.platform import PYTHON3, ADDON_PATH, LIBADDON_NAME
from ._version import __version__  # noqa: F401

# Add local libraries to Python module search path

module_search_paths = []

# 1.) Shipped with library:
module_search_paths.append(os.path.join(ADDON_PATH, LIBADDON_NAME, "libs",
                           "python3" if PYTHON3 else "python2"))
module_search_paths.append(os.path.join(ADDON_PATH, LIBADDON_NAME, "libs",
                           "common"))
# 2.) Shipped with add-on:
module_search_paths.append(os.path.join(ADDON_PATH, "libs",
                           "python3" if PYTHON3 else "python2"))
module_search_paths.append(os.path.join(ADDON_PATH, "libs",
                           "common"))

# Insert at idx 0 in order to supersede system-wide packages
for path in module_search_paths:
    if not os.path.isdir(path):
        continue
    sys.path.insert(0, path)

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
