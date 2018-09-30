# -*- coding: utf-8 -*-

"""
This file is part of the Review Heatmap add-on for Anki

Handles web elements

Copyright: (c) 2016-2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .libaddon.platform import ANKI21
from .libaddon.packaging import platformAwareImport

# Initialize Qt web resources
web_rc = platformAwareImport(".gui.forms", "web_rc", __name__)

# TODO: Look into moving more web components to designer/web

heatmap_boilerplate = r"""
<script type="text/javascript" src="qrc:/review_heatmap/web/d3.min.js"></script>
<script type="text/javascript" src="qrc:/review_heatmap/web/cal-heatmap.min.js"></script>
<link rel="stylesheet" href="qrc:/review_heatmap/web/cal-heatmap.css">
"""

streak_css = """
<style>
.streak {margin-top: 2em;}
.streak-info {margin-left: 1em;}
.sstats {font-weight: bold;}
</style>
"""

heatmap_css = """
<style>
.cal-heatmap-container .graph {
    font-family: unset;
}
.hm-btn {
    height: 100%%%%;
    display: inline-block;
    cursor: pointer;
    background: #e6e6e6;
    color: #808080;
    padding: 2px 8px;
    border-radius: 3px;
    margin-left: 2px;
    text-decoration: none;
    user-select: none;
    vertical-align: center;
}
.hm-btn:hover {
    background: #bfbfbf;
}
.hm-btn:active {background: #000}
.graph-label {fill: #808080;}
.heatmap {
    margin-top: 1em;
    display:inline-block;
}
.heatmap-controls {margin-bottom: 0;}
.cal-heatmap-container rect.highlight-now {
    stroke: black;}
.cal-heatmap-container rect.highlight {
    stroke: #E9002E;}
.cal-heatmap-container .graph-rect {
    fill: %%s}
.streak {margin-top: 0.5em;}
.streak-info {margin-left: 1em;}
.sstats {font-weight: bold;}
/* future reviews (shades of grey): */
.cal-heatmap-container .q1{fill: %%s}
.cal-heatmap-container .q2{fill: %%s}
.cal-heatmap-container .q3{fill: %%s}
.cal-heatmap-container .q4{fill: %%s}
.cal-heatmap-container .q5{fill: %%s}
.cal-heatmap-container .q6{fill: %%s}
.cal-heatmap-container .q7{fill: %%s}
.cal-heatmap-container .q8{fill: %%s}
.cal-heatmap-container .q9{fill: %%s}
.cal-heatmap-container .q10{fill: %%s}
/* past reviews (shades of green): */
.cal-heatmap-container .q11{fill: %%s}
.cal-heatmap-container .q12{fill: %%s}
.cal-heatmap-container .q13{fill: %%s}
.cal-heatmap-container .q14{fill: %%s}
.cal-heatmap-container .q15{fill: %%s}
.cal-heatmap-container .q16{fill: %%s}
.cal-heatmap-container .q17{fill: %%s}
.cal-heatmap-container .q18{fill: %%s}
.cal-heatmap-container .q19{fill: %%s}
.cal-heatmap-container .q20{fill: %%s}
.ch-tooltip {
    color: rgb(240, 240, 240);
    animation: 0.5s ease 0s normal forwards 1 fadein;
    -webkit-animation: 0.5s ease 0s normal forwards 1 fadein;
}
@keyframes fadein {
    0%%%% { opacity:0; }
    66%%%% { opacity:0; }
    100%%%% { opacity:0.9; }
}
@-webkit-keyframes fadein {
    0%%%% { opacity:0; }
    66%%%% { opacity:0; }
    100%%%% { opacity:0.9; }
}
.alignleft {
    float: left;
    width:33.33333%%%%;
    text-align:left;
}
.aligncenter {
    float: left;
    width:33.33333%%%%;
    text-align:center;
}
.alignright {
    float: left;
    width:33.33333%%%%;
    text-align:right;
}
.opts-btn {
    padding: 2px 4px;
}
.opts-btn:hover {
    background: #bfbfbf;
}
.opts-btn>img {
    position:relative;
    top: calc(50%%%% - 12px);
    height: 10px;
    width: 10px;
}
.hm-sel {
    display: inline-block;
    height: 100%%%%;
    padding: 4px 8px;
    font-size: 80%%%%;
    cursor: pointer;
    color: #808080;
    border-radius: 3px;
    user-select: none;
    border: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background: %(bg)s #e6e6e6;
}
select.hm-sel:hover {
    background: %(bg)s #bfbfbf;
}
select.hm-sel:active, select.hm-sel:focus {
    background: %(bg)s #e6e6e6;
}
</style>
""" % {"bg": "" if not ANKI21 else
             "url(qrc:/review_heatmap/icons/down.svg) 96%% / 10%% no-repeat"}

heatmap_element = r"""
<div></div>
<div class="heatmap">
    <div class="heatmap-controls">
        <div class="alignleft">
            <span>&nbsp;</span>
        </div>
        <div class="aligncenter">
            <div title="Go back" onclick="cal.previous(%(rng)d);" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/left.svg" />
            </div>
            <div title="Today" onclick="cal.rewind();" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/circle.svg" />
            </div>
            <div title="Go forward" onclick="cal.next(%(rng)d);" class="hm-btn">
                <img height="10px" src="qrc:/review_heatmap/icons/right.svg" />
            </div>
        </div>
        <div class="alignright">
            <div class="hm-btn opts-btn" title="Options" onclick="%(bridge)s('revhm_opts')">
                <img src="qrc:/review_heatmap/icons/options.svg" />
            </div>
            <div class="hm-btn opts-btn" title="Support this add-on" onclick="%(bridge)s('revhm_contrib')">
                <img src="qrc:/review_heatmap/icons/heart_bw.svg" />
            </div>
        </div>
        <div style="clear: both;">&nbsp;</div>
    </div>
    <div id="cal-heatmap"></div>
</div>

<script type="text/javascript">

function onHmSelChange(selector) {
    selector.blur();
    var val = selector.value;
    console.log(val);
}

var calStartDate = new Date();
var calMinDate = new Date(%(start)s);
var calMaxDate = new Date(%(stop)s);

// Running overview of 6-month activity in month view:
if ("%(dom)s" === "month") {
    padding = %(rng)d / 2;
    // TODO: fix
    // E.g. 6 months of past activity, current month, 5 months of future activity
    paddingLower = Math.round(padding - 1);
    paddingUpper = Math.round(padding + 1);

    calStartDate.setMonth(calStartDate.getMonth() - paddingLower);
    calStartDate.setDate(1);

    // Start at first data point if history < 6 months
    if (calMinDate.getTime() > calStartDate.getTime()) {
        calStartDate = calMinDate;
    }

    tempDate = new Date()
    tempDate.setMonth(tempDate.getMonth() + paddingUpper)
    tempDate.setDate(1);

    // Always go back to centered view after scrolling back then forward
    if (tempDate.getTime() > calMaxDate.getTime()) {
        calMaxDate = tempDate;
    }
}

var cal = new CalHeatMap();
cal.init({
    domain: "%(dom)s",
    subDomain: "%(subdom)s",
    range: %(rng)d,
    minDate: calMinDate,
    maxDate: calMaxDate,
    cellSize: 10,
    verticalOrientation: false,
    dayLabel: true,
    domainMargin: [1, 1, 1, 1],
    itemName: ["card", "cards"],
    highlight: "now",
    start: calStartDate,
    legend: %(leg)s,
    displayLegend: false,
    domainLabelFormat: "%(domLabForm)s",
    tooltip: true,
    // TODO: fix 2.0 support ↓
    subDomainTitleFormat: function(isEmpty, fmt, rawData){
        var timeNow = Date.now();
        if (isEmpty) {
            if (timeNow < rawData.t) {
                label = "cards due";
            } else {
                label = "reviews";
            }
            return `<b>No</b> ${label} on ${fmt.date}`
        } else if (rawData.v < 0) {
            return `<b>${-1 * fmt.count}</b> ${rawData.v == -1 ? "card" : "cards"} <b>due</b> ${fmt.connector} ${fmt.date}`
        } else {
            return `<b>${fmt.count}</b> ${rawData.v == 1 ? "card" : "cards"} <b>reviewed</b> ${fmt.connector} ${fmt.date}`
        }
    },
    onClick: function(date, nb){
        // call link handler
        if (nb === null || nb == 0){
            cal.highlight("now"); return;
        }
        today = new Date();
        other = new Date(date);
        if (nb >= 0) {
            diff = today.getTime() - other.getTime();
            cmd = "revhm_seen:"
        } else {
            diff = other.getTime() - today.getTime();
            cmd = "revhm_due:"
        }
        cal.highlight(["now", date])
        diffdays = Math.ceil(diff / (1000 * 60 * 60 * 24))
        %(bridge)s(cmd + diffdays)
    },
    data: %(data)s
});

</script>
"""

streak_div = r"""
<div class="streak">
    <span class="streak-info">Daily average:</span>
    <span title="Average reviews on active days"
        style="color: %s;" class="sstats">%s</span>
    <span class="streak-info">Days learned:</span>
    <span title="Percentage of days with review activity over entire review history"
        style="color: %s;" class="sstats">%s%%</span>
    <span class="streak-info">Longest streak:</span>
    <span title="Longest continuous streak of review activity. All types of repetitions included."
        style="color: %s;" class="sstats">%s</span>
    <span class="streak-info">Current streak:</span>
    <span title="Current card review activity streak. All types of repetitions included."
        style="color: %s;" class="sstats">%s</span>
</div>
"""

ov_body = """
<center>
<h3>%(deck)s</h3>
%(shareLink)s
%(desc)s
%(table)s
%(stats)s
</center>
<script>$(function () { $("#study").focus(); });</script>
"""
