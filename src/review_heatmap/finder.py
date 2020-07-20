# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https//glutanimate.com/>
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
Finder extensions
"""

import re
from typing import TYPE_CHECKING, List, Optional

from anki.hooks import wrap
from aqt import mw

if TYPE_CHECKING:
    from aqt.browser import SearchContext


# LEGACY
######################################################################

# Used when clicking on heatmap date
def find_revlog_entries(self, val: tuple):
    """Find cards by revlog timestamp range"""
    args = val[0]
    cutoff1, cutoff2 = [int(i) for i in args.split(":")]
    return "c.id in (select cid from revlog where id between %d and %d)" % (
        cutoff1,
        cutoff2,
    )


def add_finders(self, col):
    """Add custom finder to search dictionary"""
    self.search["rid"] = self.findRevlogEntries


# CURRENT
######################################################################


def _find_cards_reviewed_between(start_date: int, end_date: int) -> List[int]:
    # select from cards instead of just selecting uniques from revlog
    # in order to exclude deleted cards
    return mw.col.db.list(  # type: ignore
        "SELECT id FROM cards where id in "
        "(SELECT cid FROM revlog where id between ? and ?)",
        start_date,
        end_date,
    )


_re_rid = re.compile(r"^rid:([0-9]+):([0-9]+)$")


def find_rid(search: str) -> Optional[List[int]]:
    match = _re_rid.match(search)

    if not match:
        return None

    start_date = int(match[1])
    end_date = int(match[2])

    return _find_cards_reviewed_between(start_date, end_date)


def on_browser_will_search(search_context: "SearchContext"):
    search = search_context.search
    if search.startswith("rid"):
        found_ids = find_rid(search)
    else:
        return

    if found_ids is None:
        return

    search_context.card_ids = found_ids


# HOOKS
######################################################################


def initialize_finder():
    try:
        from aqt.gui_hooks import browser_will_search

        browser_will_search.append(on_browser_will_search)
    except (ImportError, ModuleNotFoundError):
        from anki.find import Finder

        Finder.findRevlogEntries = find_revlog_entries
        Finder.__init__ = wrap(Finder.__init__, add_finders, "after")
