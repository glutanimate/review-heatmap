# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime

from anki.utils import ids2str

from .libaddon.platform import ANKI21

__all__ = ["ActivityReporter"]


class ActivityReporter(object):

    # TODO: whole as a getData param / deck IDs instead
    def __init__(self, col, config, whole=False):
        self.col = col
        self.config = config
        self.whole = whole

    def getData(self, limhist=None, limfcst=None, mode="reviews"):
        conf = self.config["synced"]
        offset = self._getColOffset(self.col.crt)
        if limhist is None:
            limhist = self._getDynamicLimit(
                conf["limhist"], conf["limdate"]) or None
        if limfcst is None:
            limfcst = conf["limfcst"] or None  # 0 => None

        if mode == "reviews":
            # TODO:start/stop
            history = self._cardsDoneTs(offset)
            if not history:
                return None
            # TODO: handle today selection between history/forecast
            forecast = self._cardsDueTs(offset, start=0)
        else:
            raise NotImplementedError(
                "activity mode {} not implemented".format(mode))

        return self._getActivity(history, forecast)

    def _getActivity(self, history, forecast):
        col_crt = self.col.crt  # col creation unix timestamp
        offset = self._getColOffset(col_crt)  # daily cutoff offset in hours
        today = self._getToday(offset)  # 00:00 UTC timestamp for today
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
        if history[-1][0] in (today, today - 86400):
            # last recorded date today or yesterday?
            streak_cur = streak_last

        # Stats: average count on days with activity
        avg_cur = int(round(total / days_learned))

        # Stats: percentage of days with activity
        days_total = (today - first_day) / 86400
        if days_total == 0:
            pdays = 100  # review history only extends to yesterday
        else:
            pdays = int(round((days_learned / days_total) * 100))

        return {
            "activity": dict(history + forecast),
            # individual cal-heatmap dates need to be in ms:
            "start": first_day * 1000,
            "stop": last_day * 1000,
            "today": today * 1000,
            "offset": offset,
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

    def _getColOffset(self, col_crt):
        if ANKI21 and self.col.schedVer() == 2:
            return self.col.conf.get("rollover", 4)
        start_date = datetime.datetime.fromtimestamp(col_crt)
        return start_date.hour

    def _getToday(self, offset):
        time_str = self.col.db.scalar("""
select strftime('%s', "now", "-{} hours",
                "localtime", "start of day") as day""".format(offset))
        return int(time_str)

    def _getDynamicLimit(self, limit_days, limit_date):
        if limit_date == self.col.crt:
            # ignore default value (set to collection creation time)
            return limit_days

        days_since_date = int(round((
            (self.col.sched.dayCutoff - limit_date) / 86400)))

        if limit_days == 0:
            return days_since_date

        # set whatever limit is more restricting
        return min(days_since_date, limit_days)

    def _validDecks(self, excluded):
        all_excluded = []

        for did in excluded:
            children = [d[1] for d in self.col.decks.children(did)]
            all_excluded.extend(children)

        all_excluded.extend(excluded)

        return [d['id'] for d in self.col.decks.all()
                if d['id'] not in all_excluded]

    def _limit(self):
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
                return "cid in (select id from cards)"
            else:
                return ""
        else:
            dids = self.col.decks.active()
        return ("cid in (select id from cards where did in %s)" %
                ids2str(dids))

    def _cardsDue(self, start=None, end=None, chunk=1):
        # start, end: days from today (today: 0). Set to None for unlimited.
        # start: inclusive; end: exclusive
        # chunk: chunks in days (per day: 1)
        lim = ""
        if start is not None:
            lim += " and due-:today >= %d" % start
        if end is not None:
            lim += " and day < %d" % end
        return self.col.db.all("""
select (due-:today)/:chunk as day,
count()
from cards
where did in %s and queue in (2,3)
%s
group by day order by day""" % (self._limit(), lim),
                               today=self.col.sched.today,
                               chunk=chunk)

    def _cardsDoneTemp(self, offset, start=None):
        # num: number of days to look back:
        # chunk: chunks in days (per day: 1)
        lims = []
        # if start is not None:
        #     lims.append("id > {}".format(start * 1000))

        deck_limit = self._revlogLimit()
        if deck_limit:
            deck_limit.append(deck_limit)

        if lims:
            lim = "where " + " and ".join(lims)
        else:
            lim = ""

        # Group revlog entries by day while taking local timezone and DST
        # settings into account. Return as unix timestamps of UTC day start
        # (00:00:00 UTC+0 of each day)
        #
        # We perform the grouping here instead of passing the raw data on to
        # cal-heatmap because of performance reasons (user revlogs can easily
        # reach >100K entries).
        #
        # Grouping-by-day needs to be timezone-aware to assign the recorded
        # timestamps to the correct day. For that reason we include the
        # 'localtime' strftime modifier, even though it does come at a
        # performance penalty
        return self.col.db.all("""
select
strftime('%s', id/1000 - {}, 'unixepoch', 'localtime', 'start of day') as day,
count()
from revlog {}
group by day order by day""".format(offset, lim))

    def _cardsDone(self, num=7, chunk=1):
        # num: number of days to look back:
        # chunk: chunks in days (per day: 1)
        lims = []
        if num is not None:
            lims.append("id > %d" % (
                (self.col.sched.dayCutoff-(num*chunk*86400))*1000))

        lim = self._revlogLimit()
        if lim:
            lims.append(lim)

        if lims:
            lim = "where " + " and ".join(lims)
        else:
            lim = ""

        return self.col.db.all("""
select
(cast((id/1000.0 - :cut) / 86400.0 as int))/:chunk as day,
count()
from revlog %s
group by day order by day""" % lim,
                               cut=self.col.sched.dayCutoff,
                               chunk=chunk)

    def _cardsDueTs(self, offset, start=None, end=None,):
        # start, end: days from today (today: 0). Set to None for unlimited.
        # start: inclusive; end: exclusive
        # chunk: chunks in days (per day: 1)
        # TODO: limits
        lim = ""
        if start is not None:
            lim += " and due-:today >= %d" % start
        if end is not None:
            lim += " and day < %d" % end
        cmd = """
SELECT
strftime('%s', "now", 'localtime', "start of day") + (due - :today) * 86400
AS day, -count()
FROM cards
WHERE did IN {} AND queue IN (2,3)
{}
GROUP BY day ORDER BY day""".format(self._limit(), lim)
        # print("_cardsDueTsCmd: ", cmd)
        return self.col.db.all(cmd,
                               today=self.col.sched.today)

    def _cardsDoneTs(self, offset):
        # TODO: time limits
        lim = self._revlogLimit()
        if lim:
            lim = "where " + lim
        offset *= 3600
        cmd = """
SELECT
CAST(STRFTIME('%s', id / 1000 - {}, 'unixepoch', 'localtime', 'start of day') AS int) AS day, count()
FROM revlog {}
GROUP BY day ORDER BY day""".format(offset, lim)
        # print("_cardsDoneTsCmd: ", cmd)
        return self.col.db.all(cmd)
