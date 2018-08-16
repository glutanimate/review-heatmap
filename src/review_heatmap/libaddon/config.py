

# Utility functions for operating with nested config collections

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
