# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles web elements

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .libaddon.platform import JSPY_BRIDGE, ANKI21, PLATFORM
from .libaddon.packaging import platformAwareImport

__all__ = ["html_main_element", "html_heatmap",
           "html_streak", "html_info_nodata"]

# Initialize Qt web resources
web_rc = platformAwareImport(".gui.forms", "web_rc", __name__)

# TODO: Look into moving more web components to designer/web

html_main_element = """
<script type="text/javascript" src="qrc:/review_heatmap/web/d3.min.js"></script>
<script type="text/javascript" src="qrc:/review_heatmap/web/cal-heatmap.js"></script>
<link rel="stylesheet" href="qrc:/review_heatmap/web/cal-heatmap.css">
<script type="text/javascript" src="qrc:/review_heatmap/web/heatmap.js"></script>
<link rel="stylesheet" href="qrc:/review_heatmap/web/heatmap.css">

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
No activity data to show <a href="" onclick='return pybridge("revhm_opts")'>(options)</a>.
"""
