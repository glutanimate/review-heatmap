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
Static web components and templates
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .libaddon.platform import JSPY_BRIDGE, ANKI21, PLATFORM

__all__ = ["html_main_element", "html_heatmap",
           "html_streak", "html_info_nodata"]

html_main_element = """
<script type="text/javascript" src="qrc:/review_heatmap/web/d3.min.js"></script>
<script type="text/javascript" src="qrc:/review_heatmap/web/cal-heatmap.js"></script>
<link rel="stylesheet" href="qrc:/review_heatmap/web/cal-heatmap.css">
<script type="text/javascript" src="qrc:/review_heatmap/web/review-heatmap.js"></script>
<link rel="stylesheet" href="qrc:/review_heatmap/web/review-heatmap.css">

<script>
var pybridge = function(arg){{{{
    {bridge}(arg);
}}}};
var rhAnki21 = "{anki21}" === "True";
var rhPlatform = "{platform}";
</script>

<div class="rh-container {{classes}}">
{{content}}
</div>
""".format(bridge=JSPY_BRIDGE, anki21=ANKI21, platform=PLATFORM)

html_heatmap = """
<div class="heatmap">
    <div class="heatmap-controls">
        <div class="alignleft">
            <span>&nbsp;</span>
        </div>
        <div class="aligncenter">
            <div title="Go back\n(Shift-click for first year)" onclick="onHmNavigate(event, this, 'prev');" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/left.svg" />
            </div>
            <div title="Today" onclick="onHmHome(event, this);" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/circle.svg" />
            </div>
            <div title="Go forward\n(Shift-click for last year)" onclick="onHmNavigate(event, this, 'next');" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/right.svg" />
            </div>
        </div>
        <div class="alignright">
            <div class="hm-btn opts-btn" title="Options" onclick="onHmOpts(event, this);">
                <img src="qrc:/review_heatmap/icons/options.svg" />
            </div>
            <div class="hm-btn opts-btn" title="Support this add-on" onclick="onHmContrib(event, this);">
                <img src="qrc:/review_heatmap/icons/heart_bw.svg" />
            </div>
        </div>
        <div style="clear: both;">&nbsp;</div>
    </div>
    <div id="cal-heatmap"></div>
</div>
<script type="text/javascript">
    cal = initHeatmap({options}, {data});
</script>
"""

html_streak = """
<div class="streak">
    <span class="streak-info">Daily average:</span>
    <span title="Average reviews on active days"
        class="sstats {class_activity_daily_avg}">{text_activity_daily_avg}</span>
    <span class="streak-info">Days learned:</span>
    <span title="Percentage of days with review activity over entire review history"
        class="sstats {class_pct_days_active}">{text_pct_days_active}%</span>
    <span class="streak-info">Longest streak:</span>
    <span title="Longest continuous streak of review activity. All types of repetitions included."
        class="sstats {class_streak_max}">{text_streak_max}</span>
    <span class="streak-info">Current streak:</span>
    <span title="Current card review activity streak. All types of repetitions included."
        class="sstats {class_streak_cur}">{text_streak_cur}</span>
</div>
"""

html_info_nodata = """
No activity data to show (<span class="linkspan" onclick='pybridge("revhm_opts");'>options</span>).
"""
