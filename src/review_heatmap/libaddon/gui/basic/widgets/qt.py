# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018        Aristotelis P. <https//glutanimate.com/>
# Copyright (C) 2013-2018   Damien Elmes <anki@ichi2.net>
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
Qt imports
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

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
