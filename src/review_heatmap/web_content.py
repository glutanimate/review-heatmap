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
Static web components and templates
"""

from .libaddon.platform import MODULE_ADDON, PLATFORM

CSS_DISABLE_HEATMAP = "rh-disable-heatmap"
CSS_DISABLE_STATS = "rh-disable-stats"
CSS_PLATFORM_PREFIX = "rh-platform"
CSS_MODE_PREFIX = "rh-mode"
CSS_THEME_PREFIX = "rh-theme"
CSS_VIEW_PREFIX = "rh-view"

WEB_BASE = f"/_addons/{MODULE_ADDON}/web"

HTML_MAIN_ELEMENT: str = f"""
<script type="text/javascript" src="{WEB_BASE}/d3.min.js"></script>
<script type="text/javascript" src="{WEB_BASE}/anki-review-heatmap.js"></script>

<script>
var rhPlatform = "{PLATFORM}";
var rhNewFinderAPI = false;
</script>

<div class="rh-container {{classes}}">
{{content}}
</div>
"""

HTML_HEATMAP: str = f"""
<div class="heatmap">
    <div class="heatmap-controls">
        <div class="alignleft">
            <span>&nbsp;</span>
        </div>
        <div class="aligncenter">
            <div title="Go back\n(Shift-click for first year)" onclick="reviewHeatmap.onHmNavigate(event, this, 'prev');" class="hm-btn">
                <img height="10px" src="{WEB_BASE}/assets/left.svg" />
            </div>
            <div title="Today" onclick="reviewHeatmap.onHmHome(event, this);" class="hm-btn">
                <img height="10px" src="{WEB_BASE}/assets/circle.svg" />
            </div>
            <div title="Go forward\n(Shift-click for last year)" onclick="reviewHeatmap.onHmNavigate(event, this, 'next');" class="hm-btn">
                <img height="10px" src="{WEB_BASE}/assets/right.svg" />
            </div>
        </div>
        <div class="alignright">
            <div class="hm-btn opts-btn" title="Options" onclick="reviewHeatmap.onHmOpts(event, this);">
                <img src="{WEB_BASE}/assets/options.svg" />
            </div>
            <div class="hm-btn opts-btn" title="Support this add-on" onclick="reviewHeatmap.onHmContrib(event, this);">
                <img src="{WEB_BASE}/assets/heart_bw.svg" />
            </div>
        </div>
        <div style="clear: both;">&nbsp;</div>
    </div>
    <div id="cal-heatmap"></div>
</div>
<script type="text/javascript">
    window.reviewHeatmap = new ReviewHeatmap({{options}});
    reviewHeatmap.create({{data}});
</script>
"""

HTML_STREAK: str = """
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

HTML_INFO_NODATA: str = """
No activity data to show (<span class="linkspan" onclick='pycmd("revhm_opts");'>options</span>).
"""
