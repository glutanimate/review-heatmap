# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

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
            c. any other type: Value is overridden.
            d. conflicting types: Value is overridden.

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
            else:
                result[key] = incoming[key]
        else:
            result[key] = incoming[key]

    return result
