# -*- coding: utf-8 -*-

"""
Copyright: (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

# extracted from aqt.qt:
import sip

try:
    from PyQt5.Qt import *  # noqa: F401
except ImportError:
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    sip.setapi('QUrl', 2)
    try:
        sip.setdestroyonexit(False)
    except:  # noqa: E722
        # missing in older versions
        pass
    from PyQt4.QtCore import *  # noqa: F401
    from PyQt4.QtGui import *  # noqa: F401
