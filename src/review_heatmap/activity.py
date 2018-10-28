# -*- coding: utf-8 -*-

# Review Heatmap Add-on for Anki
#
# Copyright (C) 2016-2018  Aristotelis P. <https//glutanimate.com/>
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
Components related to gathering and analyzing user activity
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime

from aqt import mw

from anki.utils import ids2str

from .libaddon.platform import ANKI21

__all__ = ["ActivityReporter"]


class ActivityReporter(object):

    def __init__(self, col, config, whole=False):
        self.col = col
        self.config = config
        # NOTE: Refactor the following instance variables if we
        # ever decide to persist ActivityReporter objects across
        # multiple invocations (e.g. to cache results)
        self.whole = whole
        self.offset = self._getColOffset()
        self.today = self._getToday(self.offset)

    # Public API
    #########################################################################

    def getData(self, limhist=None, limfcst=None, mode="reviews"):
        time_limits = self._getTimeLimits(limhist, limfcst)

        if mode == "reviews":
            return self._getActivity(**self._reviewsData(time_limits))
        else:
            raise NotImplementedError(
                "activity mode {} not implemented".format(mode))

    # Activity calculations
    #########################################################################

    # General

    def _getActivity(self, history, forecast={}):
        if not history:
            return None
        
        first_day = history[0][0] if history else None
        last_day = forecast[-1][0] if forecast else None

        # Stats: cumulative activity and streaks

        streak_max = streak_cur = streak_last = 0
        current = total = 0

        for idx, item in enumerate(history):
            current += 1
            timestamp, activity = item

            try:
                next_timestamp = history[idx+1][0]
            except IndexError:  # last item
                streak_last = current
                next_timestamp = None

            if timestamp + 86400 != next_timestamp:  # >1 day gap. streak over.
                if current > streak_max:
                    streak_max = current
                current = 0

            total += activity

        days_learned = idx

        # Stats: current streak
        if history[-1][0] in (self.today, self.today - 86400):
            # last recorded date today or yesterday?
            streak_cur = streak_last

        # Stats: average count on days with activity
        avg_cur = int(round(total / max(days_learned, 1)))

        # Stats: percentage of days with activity
        #
        # NOTE: days_total is based on first recorded revlog entry, i.e. it is
        # not the grand total of days since collection creation date / whatever
        # history limits the user might have set. This value seems more
        # desirable and motivating than the raw percentage of days learned
        # in the date inclusion period.
        days_total = (self.today - first_day) / 86400
        if days_total == 0:
            pdays = 100  # review history only extends to yesterday
        else:
            pdays = int(round((days_learned / days_total) * 100))

        # Compose activity data
        activity = dict(history + forecast)
        if history[-1][0] == self.today:  # history takes precedence for today
            activity[self.today] = history[-1][1]

        return {
            "activity": activity,
            # individual cal-heatmap dates need to be in ms:
            "start": first_day * 1000 if first_day else None,
            "stop": last_day * 1000 if last_day else None,
            "today": self.today * 1000,
            "offset": self.offset,
            "stats": {
                "streak_max": {
                    "type": "streak",
                    "value": streak_max
                },
                "streak_cur": {
                    "type": "streak",
                    "value": streak_cur
                },
                "pct_days_active": {
                    "type": "percentage",
                    "value": pdays
                },
                "activity_daily_avg": {
                    "type": "cards",
                    "value": avg_cur
                }
            }
        }

    # Mode-specific

    def _reviewsData(self, time_limits):
        return {
            "history": self._cardsDone(start=time_limits[0]),
            "forecast": self._cardsDue(start=self.today,
                                       stop=time_limits[1])
        }

    # Collection properties
    #########################################################################

    def _getColOffset(self):
        """
        Return daily scheduling cutoff time in hours
        """
        if ANKI21 and self.col.schedVer() == 2:
            return self.col.conf.get("rollover", 4)
        start_date = datetime.datetime.fromtimestamp(self.col.crt)
        return start_date.hour

    @staticmethod
    def daystartEpoch(timestr, is_timestamp=True, offset=0):
        """
        Convert strftime date string into unix timestamp of 00:00 UTC
        """
        # Use db query instead of Python time-related modules to guarantee
        # consistency with rest of activity data (also: Anki does not seem
        # to ship 'pytz' by default, and 'calendar' might be removed from
        # packaging at some point, as Anki's code does not directly depend
        # on it)
        offset = " '-{} hours', ".format(offset) if offset else ""
        unixepoch = " 'unixepoch', " if is_timestamp else ""

        cmd = """
SELECT CAST(STRFTIME('%s', '{timestr}', {unixepoch} {offset}
'localtime', 'start of day') AS int)""".format(timestr=timestr,
                                               unixepoch=unixepoch,
                                               offset=offset)
        return mw.col.db.scalar(cmd)

    def _getToday(self, offset):
        """
        Return unix epoch timestamp in seconds for today (00:00 UTC)
        """
        return self.daystartEpoch("now", is_timestamp=False, offset=offset)

    # Time limits
    #########################################################################

    def _getTimeLimits(self, limhist=None, limfcst=None):
        conf = self.config["synced"]

        if limhist is not None:
            history_start = self._daysFromToday(-limhist)
        else:
            history_start = self._getConfHistoryLimit(
                conf["limhist"], conf["limdate"])
        
        if limfcst is not None:
            forecast_stop = self._daysFromToday(limfcst)
        else:
            forecast_stop = self._getConfForecastLimit(
                conf["limfcst"])
        
        return (history_start, forecast_stop)


    def _getConfHistoryLimit(self, limit_days, limit_date):
        if limit_days is None and limit_date is None:
            return None

        if limit_days:
            limit_days_date = self._daysFromToday(-limit_days)
        else:
            limit_days_date = 0

        limit_date = self.daystartEpoch(limit_date) if limit_date else None

        if (not limit_date or
                limit_date == self.daystartEpoch(self.col.crt)):
            # ignore zero value or default value
            limit_date = 0
        else:
            limit_date = limit_date

        # choose most restricting limit
        return max(limit_days_date, limit_date) or None

    def _getConfForecastLimit(self, limit_days):
        if not limit_days:
            return None
        return self._daysFromToday(limit_days)

    def _daysFromToday(self, days):
        return self.today + 86400 * days

    # Deck limits
    #########################################################################

    def _validDecks(self, excluded):
        all_excluded = []

        for did in excluded:
            children = [d[1] for d in self.col.decks.children(did)]
            all_excluded.extend(children)

        all_excluded.extend(excluded)

        return [d['id'] for d in self.col.decks.all()
                if d['id'] not in all_excluded]

    def _didLimit(self):
        excluded_dids = self.config["synced"]["limdecks"]
        if self.whole:
            if excluded_dids:
                dids = self._validDecks(excluded_dids)
            else:
                dids = [d['id'] for d in self.col.decks.all()]
        else:
            dids = self.col.decks.active()
        return ids2str(dids)

    def _revlogLimit(self):
        excluded_dids = self.config["synced"]["limdecks"]
        ignore_deleted = self.config["synced"]["limcdel"]
        if self.whole:
            if excluded_dids:
                dids = self._validDecks(excluded_dids)
            elif ignore_deleted:
                # Limiting log entries to cids with assigned dids automatically
                # excludes deleted entries. In cases where we do not use a deck
                # limit we specify the following instead:
                return "cid IN (SELECT id FROM cards)"
            else:
                return ""
        else:
            dids = self.col.decks.active()
        return ("cid IN (SELECT id FROM cards WHERE did IN %s)" %
                ids2str(dids))

    # Database queries for user activity
    #########################################################################

    def _cardsDue(self, start=None, stop=None):
        # start, stop: timestamps in seconds. Set to None for unlimited.
        # start: inclusive; stop: exclusive
        
        lim = ""
        if start is not None:
            lim += " AND day >= {}".format(start)
        if stop is not None:
            lim += " AND day < {}".format(stop)
        cmd = """
SELECT
STRFTIME('%s', 'now', 'localtime', 'start of day') + (due - :today) * 86400
AS day, -COUNT() -- negative to support heatmap legend
FROM cards
WHERE did IN {} AND queue IN (2,3)
{}
GROUP BY day ORDER BY day""".format(self._didLimit(), lim)

        return self.col.db.all(cmd, today=self.col.sched.today)

    def _cardsDone(self, start=None):
        """
        start: timestamp in seconds to start reporting from

        Group revlog entries by day while taking local timezone and DST
        settings into account. Return as unix timestamps of UTC day start
        (00:00:00 UTC+0 of each day)

        We perform the grouping here instead of passing the raw data on to
        cal-heatmap because of performance reasons (user revlogs can easily
        reach >100K entries).

        Grouping-by-day needs to be timezone-aware to assign the recorded
        timestamps to the correct day. For that reason we include the
        'localtime' strftime modifier, even though it does come at a
        performance penalty
        """
        offset = self.offset * 3600
        
        lims = []
        if start is not None:
            lims.append("day >= {}".format(start))

        deck_limit = self._revlogLimit()
        if deck_limit:
            lims.append(deck_limit)

        lim = "WHERE " + " AND ".join(lims) if lims else ""

        cmd = """
SELECT CAST(STRFTIME('%s', id / 1000 - {}, 'unixepoch',
                     'localtime', 'start of day') AS int)
AS day, COUNT()
FROM revlog {}
GROUP BY day ORDER BY day""".format(offset, lim)

        return self.col.db.all(cmd)
