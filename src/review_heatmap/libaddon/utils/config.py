# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""


from functools import reduce

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
