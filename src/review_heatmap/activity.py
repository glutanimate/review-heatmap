# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from anki.utils import ids2str

__all__ = ["ActivityReporter"]


class ActivityReporter(object):

    # TODO: whole as a getData param / deck IDs instead
    def __init__(self, col, config, whole=False):
        self.col = col
        self.config = config
        self.whole = whole

    def getData(self, limhist=None, limfcst=None, mode="reviews"):
        conf = self.config["synced"]
        if limhist is None:
            limhist = self._getDynamicLimit(conf["limhist"], conf["limdate"])
        if limfcst is None:
            limfcst = conf["limfcst"] or None  # 0 => None

        if mode == "reviews":
            history = self._cardsDone(num=limhist, chunk=1)
            if not history:
                return None
            # let history take precedence over forecast for today:
            startfcst = 1 if history[-1][0] == 0 else 0
            forecast = self._cardsDue(startfcst, limfcst)
        else:
            raise NotImplementedError(
                "activity mode {} not implemented".format(mode))

        return self._getActivity(history, forecast)

    def _getActivity(self, history, forecast):
        col_crt = self.col.crt  # col creation unix timestamp
        today = self.col.sched.today  # today in days since col creation time
        first_day = last_day = None
        streak_max = streak_cur = streak_last = 0

        current = total = 0
        activity_by_day = {}
        
        # Activity: history
        for idx, item in enumerate(history):
            current += 1
            days_ago = item[0]  # x days ago
            activity = item[1]  # activity count
            
            try:
                next_days_ago = history[idx+1][0]
            except IndexError:  # last item
                streak_last = current
                next_days_ago = None
            
            if days_ago + 1 != next_days_ago:  # days+1 ago, streak over
                if current > streak_max:
                    streak_max = current
                current = 0
            
            day = today + days_ago
            
            if first_day is None:
                first_day = day
            
            total += activity
            
            activity_by_day[col_crt + day * 86400] = activity  # by unix time

        # Stats: current streak
        if history[-1][0] in (0, -1):  # last recorded date today or yesterday?
            streak_cur = streak_last
        
        # Stats: average count on days with activity
        avg_cur = int(round(float(total) / (idx+1)))
        
        # Stats: percentage of days with activity
        dlearn = today - first_day
        if dlearn == 0:
            pdays = 100  # review history only extends to yesterday
        else:
            pdays = int(round(((idx+1) / float(dlearn+1))*100))

        # Activity: forecast
        for item in forecast:
            day = today + item[0]
            due = item[1]
            # negative counts allow us to apply separate cal-heatmap
            # colorschemes for past and future data:
            activity_by_day[col_crt + day * 86400] = -due
        
        last_day = day

        return {
            "activity": activity_by_day,
            "start": int((col_crt + first_day * 86400) * 1000),
            "stop": int((col_crt + last_day * 86400) * 1000),
            "today": col_crt + today * 86400,
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

    def _getDynamicLimit(self, limit_days, limit_date):
        # TODO: days since limit_date, return min(limit_days, limit_date_days)
        return limit_days if limit_days != 0 else None

    def _limit(self):
        if self.whole:
            return ids2str([d['id'] for d in self.col.decks.all()])
        return self.col.sched._deckLimit()

    def _revlogLimit(self):
        if self.whole:
            return ""
        return ("cid in (select id from cards where did in %s)" %
                ids2str(self.col.decks.active()))

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
