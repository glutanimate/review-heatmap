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
Miscellaneuos utilities used around libaddon
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os

from functools import reduce
from copy import deepcopy

# Utility functions for operating with nested objects


def getNestedValue(obj, keys):
    """
    Get value out of nested collection by supplying tuple of
    nested keys/indices

    Arguments:
        obj {list/dict} -- Nested collection
        keys {tuple} -- Key/index path leading to config val

    Returns:
        object -- Config value
    """
    cur = obj
    for nr, key in enumerate(keys):
        cur = cur[key]
    return cur


def setNestedValue(obj, keys, value):
    """
    Set value in nested collection by supplying tuple of
    nested keys / indices, and value to set

    Arguments:
        obj {list/dict} -- Nested collection
        keys {tuple} -- Tuple of keys/indices
        value {object} -- Key/index path leading to config val
    """
    depth = len(keys) - 1
    cur = obj
    for nr, key in enumerate(keys):
        if nr == depth:
            cur[key] = value
            return
        cur = cur[key]


def getNestedAttribute(obj, attr, *args):
    """
    Gets nested attribute from "."-separated string

    Arguments:
        obj {object} -- object to parse
        attr {string} -- attribute name, optionally including
                         "."-characters to denote different levels
                         of nesting

    Returns:
        object -- object corresponding to attribute name

    Credits:
        https://gist.github.com/wonderbeyond/d293e7a2af1de4873f2d757edd580288
    """
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return reduce(_getattr, [obj] + attr.split('.'))


def deepMergeLists(original, incoming, new=False):
    """
    Deep merge two lists. Optionally leaves original intact.

    Procedure:
        Reursively call deep merge on each correlated element of list.
        If item type in both elements are
            a. dict: Call deepMergeDicts on both values.
            b. list: Call deepMergeLists on both values.
            c. any other type: Value is overridden.
            d. conflicting types: Value is overridden.

        If incoming list longer than original then extra values are appended.

    Arguments:
        original {list} -- original list
        incoming {list} -- list with updated values
        new {bool} -- whether or not to create a new list instead of
                      updating original

    Returns:
        list -- Merged list

    Credits:
        https://stackoverflow.com/a/50773244/1708932
    """
    result = original if not new else deepcopy(original)

    common_length = min(len(original), len(incoming))
    for idx in range(common_length):
        if (isinstance(result[idx], dict) and
                isinstance(incoming[idx], dict)):
            deepMergeDicts(result[idx], incoming[idx])
        elif (isinstance(result[idx], list) and
                isinstance(incoming[idx], list)):
            deepMergeLists(result[idx], incoming[idx])
        else:
            result[idx] = incoming[idx]

    for idx in range(common_length, len(incoming)):
        result.append(incoming[idx])

    return result


def deepMergeDicts(original, incoming, new=False):
    """
    Deep merge two dictionaries. Optionally leaves original intact.

    Procedure:
        For key conflicts if both values are:
            a. dict: Recursively call deepMergeDicts on both values.
            b. list: Call deepMergeLists on both values.
            c. any other type: Original value is overridden.
            d. conflicting types: Original value is preserved.

    In the context of Anki config objects:
        - original should correspond to default config, i.e. the "scheme"
        of the expected config values
        - incoming should correspond to the user-specific values
        - incoming values takes precedence over original values with the
        exception of:
        - new values added to the configuration
        - existing values whose data types have changed (e.g. list → dict)

    Arguments:
        original {list} -- original dictionary
        incoming {list} -- dictionary with updated values
        new {bool} -- whether or not to create a new dictionary instead of
                      updating original

    Returns:
        dict -- Merged dictionaries

    Credits:
        https://stackoverflow.com/a/50773244/1708932

    """
    result = original if not new else deepcopy(original)

    for key in incoming:
        if key in result:
            if (isinstance(result[key], dict) and
                    isinstance(incoming[key], dict)):
                deepMergeDicts(result[key], incoming[key])
            elif (isinstance(result[key], list) and
                    isinstance(incoming[key], list)):
                deepMergeLists(result[key], incoming[key])
            elif (result[key] is not None and
                    (type(result[key]) != type(incoming[key]))):
                # switched to different data type, original takes precedence
                # with the exception of None value in original being replaced
                pass
            else:
                # type preserved. incoming takes precedence.
                result[key] = incoming[key]
        else:
            result[key] = incoming[key]

    return result


# File system manipulation

def ensureExists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def openFile(path):
    """Open file in default viewer"""
    import subprocess
    from .platform import PLATFORM
    if PLATFORM == "win":
        try:
            os.startfile(path)
        except (OSError, UnicodeDecodeError):
            pass
    elif PLATFORM == "mac":
        subprocess.call(('open', path))
    else:
        subprocess.call(("xdg-open", path))
