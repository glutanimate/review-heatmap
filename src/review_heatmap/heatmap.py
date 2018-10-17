# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
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

        classes = self._getCSSclasses()

        heatmap = stats = ""
        if prefs["display"][view]:
            heatmap = self._generateHeatmapElm(data, heatmap_legend)
        else:
            classes.append("rh-disable-heatmap")
        
        if prefs["display"][view] or prefs["statsvis"]:
            stats = self._generateStatsElm(data, stats_legend)
        else:
            classes.append("rh-disable-stats")

        return html_main_element.format(content=heatmap + stats,
                                        classes=" ".join(classes))

    def _getCSSclasses(self):
        conf = self.config["synced"]
        classes = ["rh-platform-{}".format(PLATFORM),
                   "rh-theme-{}".format(conf["colors"]),
                   "rh-mode-{}".format(conf["mode"])]
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
