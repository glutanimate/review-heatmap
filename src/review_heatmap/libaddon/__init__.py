# -*- coding: utf-8 -*-

"""
Libaddon: A helper library for Anki add-on development

Provides access to a number of commonly used modules shared across
many of my add-ons. Probably not fit for general use yet, as it likely
still is too specific to my own add-ons and implementations.

This module is the package entry-point.

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from ._version import __version__  # noqa: F401

__all__ = [
    "__version__"
]
