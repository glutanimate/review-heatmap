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
Components related to gathering and analyzing user activity
"""

import datetime
import time
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
)

from anki.utils import ids2str
from anki.errors import NotFoundError

if TYPE_CHECKING:
    from anki.collection import Collection
    from anki.dbproxy import DBProxy

from .errors import CollectionError
from .libaddon.anki.configmanager import ConfigManager
from .libaddon.debug import isDebuggingOn, logger
from .times import daystart_epoch
from .types import DeckId

# limit max forecast to 200 years to protect against invalid due dates
MAX_FORECAST_DAYS = 73000


class ActivityType(Enum):
    reviews = 0


class StatsType(Enum):
    streak = 0
    percentage = 1
    cards = 2


class StatsEntry(NamedTuple):
    value: int
    type: StatsType = StatsType.streak


class StatsEntryStreak(StatsEntry):
    value: int
    type: StatsType = StatsType.streak


class StatsEntryPercentage(StatsEntry):
    value: int
    type: StatsType = StatsType.percentage


class StatsEntryCards(StatsEntry):
    value: int
    type: StatsType = StatsType.cards


class StatsReport(NamedTuple):
    streak_max: StatsEntryStreak
    streak_cur: StatsEntryStreak
    pct_days_active: StatsEntryPercentage
    activity_daily_avg: StatsEntryCards


class ActivityReport(NamedTuple):
    activity: Dict[int, int]
    start: Optional[int]
    stop: Optional[int]
    today: int
    offset: int
    stats: StatsReport


class ActivityReporter:
    def __init__(self, col: "Collection", config: ConfigManager):
        self._col: "Collection"
        self._db: "DBProxy"

        self._config: ConfigManager = config
        self.set_collection(col)

    # Public API
    #########################################################################

    def get_report(
        self,
        limhist: Optional[int] = None,
        limfcst: Optional[int] = None,
        activity_type: ActivityType = ActivityType.reviews,
        current_deck_only: bool = False,
    ) -> Optional[ActivityReport]:

        history_start, forecast_stop = self._get_time_limits(limhist, limfcst)

        if activity_type == ActivityType.reviews:
            history = self._cards_done(
                start=history_start,
                current_deck_only=current_deck_only,
            )
            forecast = self._cards_due(
                start=self._today,
                stop=forecast_stop,
                current_deck_only=current_deck_only,
            )

            if not history:
                return None

            activity_report = self._get_activity(history=history, forecast=forecast)
        else:
            raise NotImplementedError(
                "activity type {} not implemented".format(activity_type)
            )

        return activity_report

    def set_collection(self, col: "Collection"):
        # NOTE: Binding the collection is dangerous if we ever persist ActivityReporter
        # across profile reloads, so allow outside callers to update the collection
        # if necessary

        if not col or not col.db:
            raise CollectionError("Anki collection and/or database is not ready")

        self._col = col
        self._db = col.db

    # Activity calculations
    #########################################################################

    # General

    def _get_activity(
        self,
        history: List[Sequence[int]],
        forecast: Optional[List[Sequence[int]]] = None,
    ) -> ActivityReport:

        first_day = history[0][0] if history else 0
        last_day = forecast[-1][0] if forecast else 0

        # Stats: cumulative activity and streaks

        streak_max: int = 0
        streak_cur: int = 0
        streak_last: int = 0
        current: int = 0
        total: int = 0
        idx: int = 0
        next_timestamp: Optional[int]

        for idx, item in enumerate(history):
            current += 1
            timestamp, activity = item

            try:
                next_timestamp = history[idx + 1][0]
            except IndexError:  # last item
                streak_last = current
                next_timestamp = None

            if timestamp + 86400 != next_timestamp:  # >1 day gap. streak over.
                if current > streak_max:
                    streak_max = current
                current = 0

            total += activity

        days_learned: int = idx + 1
        today = self._today

        # Stats: current streak
        if history[-1][0] in (today, today - 86400):
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

        days_total = (today - first_day) / 86400 + 1

        if days_total == 1:
            pdays = 100  # review history only extends to yesterday
        else:
            pdays = int(round((days_learned / days_total) * 100))

        # Compose activity data
        activity_dict: Dict[int, int] = dict(history + forecast)  # type: ignore
        if history[-1][0] == today:  # history takes precedence for today
            activity_dict[today] = history[-1][1]

        # individual cal-heatmap dates need to be in ms:

        return ActivityReport(
            activity=activity_dict,
            start=first_day * 1000 if first_day else None,
            stop=last_day * 1000 if last_day else None,
            today=today * 1000,
            offset=self._offset,
            stats=StatsReport(
                streak_max=StatsEntryStreak(value=streak_max),
                streak_cur=StatsEntryStreak(value=streak_cur),
                pct_days_active=StatsEntryPercentage(value=pdays),
                activity_daily_avg=StatsEntryCards(value=avg_cur),
            ),
        )

    # Collection properties
    #########################################################################

    @property
    def _sched_ver(self) -> Literal[1, 2, 3]:
        try:
            if self._col.v3_scheduler():
                return 3
        except AttributeError:
            pass
        try:
            return self._col.sched_ver()
        except AttributeError:
            return self._col.schedVer()

    @property
    def _offset(self) -> int:
        """
        Return daily scheduling cutoff time in hours
        """
        if self._sched_ver >= 2:
            rollover = self._col.conf.get("rollover", 4)
            return rollover

        start_date = datetime.datetime.fromtimestamp(self._col.crt)
        return start_date.hour

    @property
    def _today(self) -> int:
        """
        Return unix epoch timestamp in seconds for today (00:00 UTC)
        """
        return daystart_epoch(self._db, "now", is_timestamp=False, offset=self._offset)

    # Time limits
    #########################################################################

    def _get_time_limits(
        self, limhist: Optional[int] = None, limfcst: Optional[int] = None
    ) -> Tuple[Optional[int], Optional[int]]:

        conf = self._config["synced"]

        history_start: Optional[int]
        forecast_stop: Optional[int]

        if limhist is not None:
            history_start = self._days_from_today(-limhist)
        else:
            history_start = self._get_conf_history_limit(
                conf["limhist"], conf["limdate"]
            )

        if limfcst is not None:
            forecast_stop = self._days_from_today(limfcst)
        else:
            forecast_stop = self._get_conf_forecast_limit(conf["limfcst"])

        return (history_start, forecast_stop)

    def _get_conf_history_limit(
        self, limit_days: Optional[int], limit_date: Optional[int]
    ) -> Optional[int]:

        if limit_days is None and limit_date is None:
            return None

        if limit_days:
            limit_days_date = self._days_from_today(-limit_days)
        else:
            limit_days_date = 0

        limit_date = daystart_epoch(self._db, str(limit_date)) if limit_date else None

        # be defensive as col.crt can transiently be None (e.g. when importing colpkgs)
        creation_time = getattr(self._col, "crt", None)

        if (
            not limit_date
            or not creation_time
            or limit_date == daystart_epoch(self._db, creation_time)
        ):
            # ignore zero value or default value
            limit_date = 0
        else:
            limit_date = limit_date

        # choose most restricting limit
        return max(limit_days_date, limit_date) or None

    def _get_conf_forecast_limit(self, limit_days: int) -> int:
        limit_days = limit_days or MAX_FORECAST_DAYS
        return self._days_from_today(limit_days)

    def _days_from_today(self, days: int) -> int:
        return self._today + 86400 * days

    # Deck limits
    #########################################################################

    def _valid_decks(self, excluded: List[DeckId]) -> List[DeckId]:
        deck_manager = self._col.decks
        all_excluded = []

        for did in excluded:
            try:
                children = [d[1] for d in deck_manager.children(did)]
            except NotFoundError:  # 2.1.28+
                continue
            all_excluded.extend(children)

        all_excluded.extend(excluded)

        return [d["id"] for d in self._col.decks.all() if d["id"] not in all_excluded]

    def _did_limit(self, current_deck_only: bool) -> str:
        excluded_dids: List[DeckId] = self._config["synced"]["limdecks"]
        if not current_deck_only:
            if excluded_dids:
                dids = self._valid_decks(excluded_dids)
            else:
                dids = [d["id"] for d in self._col.decks.all()]
        else:
            dids = self.__get_active_deck_ids()
        return ids2str(dids)

    def _revlog_limit(self, current_deck_only: bool) -> str:
        excluded_dids = self._config["synced"]["limdecks"]
        ignore_deleted = self._config["synced"]["limcdel"]
        if not current_deck_only:
            if excluded_dids:
                dids = self._valid_decks(excluded_dids)
            elif ignore_deleted:
                # Limiting log entries to cids with assigned dids automatically
                # excludes deleted entries. In cases where we do not use a deck
                # limit we specify the following instead:
                return "cid IN (SELECT id FROM cards)"
            else:
                return ""
        else:
            dids = self.__get_active_deck_ids()
        return "cid IN (SELECT id FROM cards WHERE did IN %s)" % ids2str(dids)

    def __get_active_deck_ids(self) -> List["DeckId"]:
        deck_manager = self._col.decks
        try:
            selected_deck = deck_manager.get_current_id()
        except AttributeError:
            selected_deck = deck_manager.selected()
        active_deck_ids = deck_manager.deck_and_child_ids(selected_deck)
        return active_deck_ids

    # Other settings affecting included revlog entries
    #########################################################################

    @property
    def _ignore_rescheduled_entries(self) -> bool:
        return self._config["synced"]["limresched"]

    # Database queries for user activity
    #########################################################################

    def _cards_due(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        current_deck_only: bool = False,
    ) -> List[Sequence[int]]:
        """[summary]

        Args:
            start (Optional[int], optional): [description]. Defaults to None.
            stop (Optional[int], optional): [description]. Defaults to None.

        Returns:
            List[List[int]]: [[int, int]]
        """
        # start, stop: timestamps in seconds. Set to None for unlimited.
        # start: inclusive; stop: exclusive

        lim = ""
        if start is not None:
            lim += " AND day >= {}".format(start)
        if stop is not None:
            lim += " AND day < {}".format(stop)
        cmd = """
SELECT
STRFTIME('%s', 'now', '-{} hours', 'localtime', 'start of day')
    + (due - ?) * 86400
AS day, -COUNT(), due -- negative to support heatmap legend
FROM cards
WHERE did IN {} AND queue IN (2,3)
{}
GROUP BY day ORDER BY day""".format(
            self._offset, self._did_limit(current_deck_only), lim
        )

        res: List[Sequence[int]] = self._db.all(cmd, self._col.sched.today)

        if isDebuggingOn():
            self.__debug_cards_due(cmd, res)

        return [i[:-1] for i in res]

    def _cards_done(
        self,
        start: Optional[int] = None,
        current_deck_only: bool = False,
    ) -> List[Sequence[int]]:
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

        Returns:
            [[int, int]**]
        """
        offset = self._offset * 3600

        lims = []
        if start is not None:
            lims.append("day >= {}".format(start))

        if self._ignore_rescheduled_entries:
            lims.append("ease >= 1")

        deck_limit = self._revlog_limit(current_deck_only)
        if deck_limit:
            lims.append(deck_limit)

        lim = "WHERE " + " AND ".join(lims) if lims else ""

        cmd = """\
SELECT CAST(STRFTIME('%s', id / 1000 - {}, 'unixepoch',
                     'localtime', 'start of day') AS int)
AS day, COUNT()
FROM revlog {}
GROUP BY day ORDER BY day""".format(
            offset, lim
        )

        res = self._db.all(cmd)

        if isDebuggingOn():
            self.__debug_cards_done(cmd, res)

        return res

    def __debug_cards_due(self, cmd: str, res: List[Sequence[int]]):
        sched_ver = self._sched_ver
        if sched_ver >= 2:
            offset = self._col.conf.get("rollover", 4)
        else:
            startDate = datetime.datetime.fromtimestamp(self._col.crt)
            offset = startDate.hour

        try:
            day_cutoff = self._col.sched.day_cutoff
        except AttributeError:
            day_cutoff = self._col.sched.dayCutoff

        logger.debug(cmd)
        logger.debug(self._col.sched.today)
        logger.debug("Scheduler version %s", sched_ver)
        logger.debug("Day starts at setting: %s hours", offset)
        logger.debug(
            time.strftime(
                "dayCutoff: %Y-%m-%d %H:%M",
                time.localtime(day_cutoff),
            )
        )
        logger.debug(
            time.strftime("local now: %Y-%m-%d %H:%M", time.localtime(time.time()))
        )
        col_days = self._col.sched.today
        logger.debug("Col days: %s", col_days)
        if col_days is not None:
            logger.debug(
                time.strftime(
                    "Col today: %Y-%m-%d",
                    time.localtime(self._col.crt + 86400 * col_days),
                )
            )
        logger.debug(res)

    def __debug_cards_done(self, cmd: str, res: List[Sequence[int]]):
        logger.debug(cmd)
        logger.debug(res)
