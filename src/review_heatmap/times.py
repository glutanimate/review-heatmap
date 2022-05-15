# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2022  Aristotelis P. <https//glutanimate.com/>
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
Shared datetime/timezone handling
"""

from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from anki.dbproxy import DBProxy


def daystart_epoch(
    db: "DBProxy",
    time_specifier: Union[str, int],
    is_timestamp: bool = True,
    offset: int = 0,
) -> int:
    """
    Convert strftime date string into unix timestamp of 00:00 UTC
    """
    # Use db query instead of Python time-related modules to guarantee
    # consistency with rest of activity data (also: Anki does not seem
    # to ship 'pytz' by default, and 'calendar' might be removed from
    # packaging at some point, as Anki's code does not directly depend
    # on it)
    offset_str = " '-{} hours', ".format(offset) if offset else ""
    unixepoch = " 'unixepoch', " if is_timestamp else ""

    cmd = """
SELECT CAST(STRFTIME('%s', '{time_specifier}', {unixepoch} {offset}
'localtime', 'start of day') AS int)""".format(
        time_specifier=time_specifier, unixepoch=unixepoch, offset=offset_str
    )
    return db.scalar(cmd)
