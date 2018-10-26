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
Heatmap and stats elements generation
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from aqt import mw

from anki.utils import json

from .libaddon.platform import ANKI21, PLATFORM

from .activity import ActivityReporter
from .config import heatmap_modes
from .web import *

__all__ = ["HeatmapCreator"]


class HeatmapCreator(object):

    css_colors = (
        "rh-col0", "rh-col11", "rh-col12", "rh-col13", "rh-col14",
        "rh-col15", "rh-col16", "rh-col17", "rh-col18", "rh-col19",
        "rh-col20"
    )

    # workaround for list comprehensions not working in class-scope
    def compress_levels(colors, indices):
        return [colors[i] for i in indices]

    stat_levels = {
        # tuples of threshold value, css_colors index
        "streak": list(zip((0, 14, 30, 90, 180, 365),
                       compress_levels(css_colors, (0, 2, 4, 6, 9, 10)))),
        "percentage": list(zip((0, 25, 50, 60, 70, 80, 85, 90, 95, 99),
                           css_colors)),
    }

    legend_factors = (0.125, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 4)

    stat_units = {
        "streak": "day",
        "percentage": None,
        "cards": "card"
    }

    def __init__(self, config, whole=False):
        # TODO: rethink "whole" support
        self.config = config
        self.whole = whole
        self.activity = ActivityReporter(mw.col, self.config, whole=whole)

    def generate(self, view="deckbrowser", limhist=None, limfcst=None):
        prefs = self.config["profile"]
        data = self.activity.getData(limhist=limhist, limfcst=limfcst)

        if not data:
            return html_main_element.format(content=html_info_nodata,
                                            classes="")

        stats_legend, heatmap_legend = self._getDynamicLegends(
            data["stats"]["activity_daily_avg"]["value"])

        classes = self._getCSSclasses(view)

        heatmap = stats = ""
        if prefs["display"][view]:
            heatmap = self._generateHeatmapElm(data, heatmap_legend)
        else:
            classes.append("rh-disable-heatmap")
        
        if prefs["display"][view] or prefs["statsvis"]:
            stats = self._generateStatsElm(data, stats_legend)
        else:
            classes.append("rh-disable-stats")

        if self.whole:
            self._saveCurrentStreaks(data)

        return html_main_element.format(content=heatmap + stats,
                                        classes=" ".join(classes))

    def _getCSSclasses(self, view):
        conf = self.config["synced"]
        classes = ["rh-platform-{}".format(PLATFORM),
                   "rh-theme-{}".format(conf["colors"]),
                   "rh-mode-{}".format(conf["mode"]),
                   "rh-view-{}".format(view)]
        if not ANKI21:
            classes.append("rh-anki-20")
        return classes

    def _generateHeatmapElm(self, data, dynamic_legend):
        mode = heatmap_modes[self.config["synced"]["mode"]]

        # TODO: pass on "whole" to govern browser link "deck:current" addition
        options = {
            "domain": mode["domain"],
            "subdomain": mode["subDomain"],
            "range": mode["range"],
            "domLabForm": mode["domLabForm"],
            "start": data["start"],
            "stop": data["stop"],
            "today": data["today"],
            "offset": data["offset"],
            "legend": dynamic_legend,
            "whole": self.whole
        }

        return html_heatmap.format(
            options=json.dumps(options),
            data=json.dumps(data["activity"])
        )


    def _generateStatsElm(self, data, dynamic_legend):
        stat_levels = {
            "cards": zip(dynamic_legend, self.css_colors)
        }
        stat_levels.update(self.stat_levels)

        format_dict = {}

        for name, stat_dict in data["stats"].items():
            stype = stat_dict["type"]
            value = stat_dict["value"]
            levels = stat_levels[stype]

            css_class = self.css_colors[0]
            for threshold, css_class in levels:
                if value <= threshold:
                    break

            label = self._dayS(value, self.stat_units[stype])

            format_dict["class_" + name] = css_class
            format_dict["text_" + name] = label

        return html_streak.format(**format_dict)

    def _getDynamicLegends(self, average):
        legend = self._dynamicLegend(average)
        stats_legend = [0] + legend
        heatmap_legend = self._heatmapLegend(legend)
        return stats_legend, heatmap_legend

    def _heatmapLegend(self, legend):
        # Inverted negative legend for future dates. Allows us to
        # implement different color schemes for past and future without
        # having to modify cal-heatmap:
        return [-i for i in legend[::-1]] + [0] + legend
    
    def _dynamicLegend(self, average):
        # set default average if average too low for informational levels
        avg = max(20, average)
        return [fct * avg for fct in self.legend_factors]

    def _dayS(self, count, term):
        if not term:
            return count
        return "{} {}{}".format(
            str(count), term,
            "s" if abs(count) > 1 else ""
        )

    def _saveCurrentStreaks(self, data):
        """
        Store current streak in mw object

        TODO: Make data like this available through a proper API

        Just a quick hack that allows us to assess user performance from
        other distant parts of the code / other add-ons
        """
        mw._hmStreakMax = data["stats"]["streak_max"]["value"]
        mw._hmStreakCur = data["stats"]["streak_cur"]["value"]
